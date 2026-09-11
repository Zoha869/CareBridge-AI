"""
Individual nodes of the patient assistant LangGraph workflow.
"""

import json
import re
from app.agents.state import PatientState
from app.models.appointment import Appointment
from app.services.intent_service import detect_intent, detect_urgency
from app.services.llm_service import chat_completion, structured_completion
from app.services.conversation_service import get_recent_messages
from app.services.appointment_service import (
    get_available_doctors,
    is_slot_available,
    create_appointment,
    get_patient_appointments,
    cancel_appointment,
    reschedule_appointment,
)
from app.services.patient_context_service import build_context_text
from app.services.concern_service import extract_and_save_concern
from app.services.summary_service import regenerate_summary

GENERAL_PROMPT = """You are the CareBridge hospital patient assistant. Answer clearly
and briefly. Only claim to help with what this system actually supports:
- Booking, viewing, and cancelling appointments
- Answering questions about the patient's own recorded visits, medications, and
  doctor instructions
- Logging new symptoms/concerns so the doctor sees them
- General, non-diagnostic health information

Never claim to handle billing, insurance, lab/test results, prescription refills,
or anything not listed above - this system doesn't support those yet. If asked,
say so plainly and suggest contacting the clinic directly."""

HISTORY_PROMPT = """You are a hospital patient assistant. Answer the patient's
question using ONLY the patient record below - never invent visits, medications,
appointments, or instructions that aren't listed. If the record doesn't have what
they're asking about, say so plainly and suggest they contact the clinic.

Patient record:
{context}
"""

FOLLOWUP_MARKER = "Before I confirm —"

RESCHEDULE_HINT_PATTERN = re.compile(
    r"\breschedul|change (the |my )?(time|date|timing|appointment)|"
    r"move (it|my appointment)|different (time|date|day|timing)|"
    r"(new|another) (time|date)",
    re.IGNORECASE,
)

ACTION_PROMPT = """Determine whether the patient wants to BOOK a new appointment,
CANCEL an existing one, or RESCHEDULE (change the date/time of) an existing one,
based on the conversation.
Return JSON only: {{"action": "book" | "cancel" | "reschedule"}}"""

CANCEL_MATCH_PROMPT = """The patient wants to cancel an appointment. Match their
message to one of their existing appointments below.

Existing appointments:
{appointments}

Return JSON only: {{"appointment_id": "<id from the list above>" or null}}
Set appointment_id to null if you can't confidently match one."""

RESCHEDULE_MATCH_PROMPT = """The patient wants to change the date/time of an
existing appointment. Match it to one of their appointments below, using the
ENTIRE conversation - the new date/time may have been given a turn or two ago.

Existing appointments:
{appointments}

Return JSON only:
{{"appointment_id": "<id from the list above>" or null,
 "new_date": "YYYY-MM-DD" or null, "new_time": "HH:MM" or null}}
If they haven't given a new date, leave new_date null - do NOT reuse the
appointment's current date/time as if it were the new one. Set appointment_id
to null if you can't confidently match one appointment."""


def retrieve_context_node(state: PatientState) -> PatientState:
    state["history"] = get_recent_messages(state["db"], state["conversation_id"])
    return state


def intent_node(state: PatientState) -> PatientState:
    state["intent"] = detect_intent(state["message"], state["history"])
    return state


def safety_check_node(state: PatientState) -> PatientState:
    # detect_intent alone isn't enough here - it's told to keep classifying
    # messages as "appointment" while a booking is in progress, even if the
    # message looks urgent, so a red-flag symptom typed as the booking
    # reason never reached this check before. detect_urgency runs on the
    # raw message regardless of that booking-continuation logic.
    if state["intent"] == "urgent" or detect_urgency(state["message"]):
        # Urgent doesn't mean throw away what the patient just said - it
        # still needs to reach the doctor. Log it as a concern and refresh
        # the summary before replying, same as the concern/booking flows do.
        db = state["db"]
        concern = extract_and_save_concern(db, state["patient_id"], state["message"], state["history"])
        regenerate_summary(db, state["patient_id"])
        state["urgent_logged"] = True

        advisory = (
            "This sounds urgent. Please contact emergency services or visit the "
            "nearest hospital immediately. This assistant cannot handle emergencies.\n\n"
            f"I've logged this for your doctor: \"{concern.description}\" (urgent priority)."
        )

        if state["intent"] == "appointment":
            # A booking is already in progress and this message is answering
            # it (date/time/reason) - don't drop it. Let the appointment node
            # still run so the doctor actually gets an appointment on the
            # schedule, not just a note; the advisory gets prepended to
            # whatever the booking flow says next (missing-info ask or the
            # confirmation) in appointment_node.
            state["urgent_notice"] = advisory
        else:
            state["intent"] = "urgent"
            state["response"] = (
                advisory + "\n\nIf you're able to, it also helps your doctor to know: "
                "since when exactly this started, whether you've taken any medicine for "
                "it, and if there are any other symptoms along with it."
            )
    return state


def general_response_node(state: PatientState) -> PatientState:
    messages = state["history"] + [{"role": "user", "content": state["message"]}]
    state["response"] = chat_completion(GENERAL_PROMPT, messages)
    return state


def patient_history_node(state: PatientState) -> PatientState:
    context_text = build_context_text(state["db"], state["patient_id"])
    system_prompt = HISTORY_PROMPT.format(context=context_text)
    messages = state["history"] + [{"role": "user", "content": state["message"]}]
    state["response"] = chat_completion(system_prompt, messages)
    return state


def new_concern_node(state: PatientState) -> PatientState:
    db = state["db"]
    concern = extract_and_save_concern(db, state["patient_id"], state["message"], state["history"])
    regenerate_summary(db, state["patient_id"])

    state["response"] = (
        f"I've noted this: \"{concern.description}\" (marked as {concern.severity.value} priority). "
        "This has been added to your record so your doctor can see it. "
        "Would you like to book an appointment to discuss it?"
    )
    return state


def appointment_node(state: PatientState) -> PatientState:
    db = state["db"]
    conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in state["history"])
    conversation_text += f"\nuser: {state['message']}"

    # Checked first, same keyword-first/LLM-fallback pattern used on the
    # doctor side - the LLM classifier alone was unreliable on vague wording
    # like "change timing" (no explicit "reschedule"), silently falling back
    # to "book" and re-booking the same slot against itself.
    if RESCHEDULE_HINT_PATTERN.search(state["message"]):
        action = "reschedule"
    else:
        action = structured_completion(ACTION_PROMPT, conversation_text).get("action", "book")

    if action == "cancel":
        _handle_cancel(state, db, conversation_text)
    elif action == "reschedule":
        _handle_reschedule(state, db, conversation_text)
    else:
        _handle_book(state, db, conversation_text)

    if state.get("urgent_notice"):
        state["response"] = f"{state['urgent_notice']}\n\n{state['response']}"

    return state


def _handle_cancel(state: PatientState, db, conversation_text: str) -> None:
    appointments = get_patient_appointments(db, state["patient_id"])

    if not appointments:
        state["response"] = "You don't have any upcoming appointments to cancel."
        return

    prompt = CANCEL_MATCH_PROMPT.format(appointments=json.dumps(appointments))
    match = structured_completion(prompt, conversation_text)
    appointment_id = match.get("appointment_id")

    if not appointment_id:
        listing = "\n".join(f"- Dr. {a['doctor_name']} on {a['date']} at {a['time']}" for a in appointments)
        state["response"] = f"Which appointment would you like to cancel?\n{listing}"
        return

    cancelled = cancel_appointment(db, appointment_id)
    if cancelled is None:
        state["response"] = "I couldn't find that appointment. Could you confirm which one?"
        return

    state["response"] = f"Your appointment on {cancelled.appointment_date} at {cancelled.appointment_time} has been cancelled."


def _handle_reschedule(state: PatientState, db, conversation_text: str) -> None:
    appointments = get_patient_appointments(db, state["patient_id"])

    if not appointments:
        state["response"] = "You don't have any upcoming appointments to reschedule."
        return

    prompt = RESCHEDULE_MATCH_PROMPT.format(appointments=json.dumps(appointments))
    match = structured_completion(prompt, conversation_text)
    appointment_id = match.get("appointment_id")

    if not appointment_id:
        listing = "\n".join(f"- Dr. {a['doctor_name']} on {a['date']} at {a['time']}" for a in appointments)
        state["response"] = f"Which appointment would you like to reschedule?\n{listing}"
        return

    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if appointment is None:
        state["response"] = "I couldn't find that appointment. Could you confirm which one?"
        return

    new_date = match.get("new_date") or str(appointment.appointment_date)
    new_time = match.get("new_time")
    if not new_time:
        state["response"] = "What date and time would you like to move it to?"
        return

    if not is_slot_available(db, appointment.doctor_id, new_date, new_time, exclude_appointment_id=appointment.id):
        state["response"] = "That slot is already booked. Please choose a different time."
        return

    updated = reschedule_appointment(db, appointment.id, new_date, new_time)
    state["response"] = f"Your appointment has been moved to {updated.appointment_date} at {updated.appointment_time}."


def _handle_book(state: PatientState, db, conversation_text: str) -> None:
    doctors = get_available_doctors(db)

    if not doctors:
        state["response"] = "There are no doctors available for booking right now."
        return

    extract_prompt = f"""Extract appointment booking details from the ENTIRE conversation
below, not just the latest message - earlier messages may already contain the doctor,
date, time, or reason.
Match the patient's mentioned doctor (by name or specialization) to one of these:
{json.dumps(doctors)}

Return JSON only:
{{"doctor_id": "<id from the list above>" or null, "date": "YYYY-MM-DD" or null,
 "time": "HH:MM" or null, "reason": str or null, "ready_to_book": true/false,
 "reason_detail_sufficient": true/false}}
Set ready_to_book true only when doctor_id, date, time, and reason are all present.
If the patient hasn't named a doctor, ask them to choose from the available list.
reason_detail_sufficient is true only if the reason includes some real clinical
detail (how long, how severe, what makes it better/worse) - a bare one-line
complaint like "chest pain" alone is NOT sufficient."""

    details = structured_completion(extract_prompt, conversation_text)

    if not details.get("ready_to_book"):
        missing = [k for k in ("doctor_id", "date", "time", "reason") if not details.get(k)]
        if "doctor_id" in missing:
            names = ", ".join(f"{d['name']} ({d['specialization']})" for d in doctors)
            state["response"] = f"Which doctor would you like to see? Available: {names}."
        else:
            state["response"] = f"To book your appointment, please also provide: {', '.join(missing)}."
        return

    # Ask one clarifying follow-up before booking if the reason is too thin -
    # but only once, so we don't loop forever if the patient has nothing more
    # to add. FOLLOWUP_MARKER lets us check whether we already asked.
    already_asked = any(FOLLOWUP_MARKER in m.get("content", "") for m in state["history"])
    if not details.get("reason_detail_sufficient") and not already_asked:
        state["response"] = (
            f"{FOLLOWUP_MARKER} could you tell me a bit more about \"{details['reason']}\" - "
            "how long you've had it, how severe it is, and anything that makes it better or worse? "
            "This helps your doctor prepare."
        )
        return

    if not is_slot_available(db, details["doctor_id"], details["date"], details["time"]):
        state["response"] = "That slot is already booked. Please choose a different time."
        return

    appointment = create_appointment(
        db,
        patient_id=state["patient_id"],
        doctor_id=details["doctor_id"],
        appointment_date=details["date"],
        appointment_time=details["time"],
        reason=details["reason"],
    )

    # The booking reason often IS a new concern (e.g. "chest pain, worse on
    # stairs") - without this, that clinical detail only ever lived in the
    # appointment's "reason" field and never reached PatientConcern or the
    # doctor-facing summary. Skipped if safety_check_node already logged it
    # (urgent case) to avoid saving the same concern twice.
    if not state.get("urgent_logged"):
        extract_and_save_concern(db, state["patient_id"], details["reason"], state["history"])
    regenerate_summary(db, state["patient_id"])

    state["response"] = (
        f"Your appointment is confirmed for {appointment.appointment_date} at {appointment.appointment_time}. "
        "I've also added what you told me to your record so your doctor can see it beforehand."
    )


def route_by_intent(state: PatientState) -> str:
    intent = state["intent"]
    if intent == "urgent":
        return "end"
    if intent == "appointment":
        return "appointment"
    if intent == "patient_history":
        return "history"
    if intent == "new_concern":
        return "concern"
    return "general"