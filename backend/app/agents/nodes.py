"""
Individual nodes of the patient assistant LangGraph workflow.
"""

import json
from app.agents.state import PatientState
from app.services.intent_service import detect_intent
from app.services.llm_service import chat_completion, structured_completion
from app.services.conversation_service import get_recent_messages
from app.services.appointment_service import (
    get_available_doctors,
    is_slot_available,
    create_appointment,
    get_patient_appointments,
    cancel_appointment,
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

ACTION_PROMPT = """Determine whether the patient wants to BOOK a new appointment or
CANCEL an existing one, based on the conversation.
Return JSON only: {{"action": "book" | "cancel"}}"""

CANCEL_MATCH_PROMPT = """The patient wants to cancel an appointment. Match their
message to one of their existing appointments below.

Existing appointments:
{appointments}

Return JSON only: {{"appointment_id": "<id from the list above>" or null}}
Set appointment_id to null if you can't confidently match one."""


def retrieve_context_node(state: PatientState) -> PatientState:
    state["history"] = get_recent_messages(state["db"], state["conversation_id"])
    return state


def intent_node(state: PatientState) -> PatientState:
    state["intent"] = detect_intent(state["message"], state["history"])
    return state


def safety_check_node(state: PatientState) -> PatientState:
    if state["intent"] == "urgent":
        state["response"] = (
            "This sounds urgent. Please contact emergency services or visit the "
            "nearest hospital immediately. This assistant cannot handle emergencies."
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

    action = structured_completion(ACTION_PROMPT, conversation_text).get("action", "book")

    if action == "cancel":
        _handle_cancel(state, db, conversation_text)
    else:
        _handle_book(state, db, conversation_text)

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
 "time": "HH:MM" or null, "reason": str or null, "ready_to_book": true/false}}
Set ready_to_book true only when doctor_id, date, time, and reason are all present.
If the patient hasn't named a doctor, ask them to choose from the available list."""

    details = structured_completion(extract_prompt, conversation_text)

    if not details.get("ready_to_book"):
        missing = [k for k in ("doctor_id", "date", "time", "reason") if not details.get(k)]
        if "doctor_id" in missing:
            names = ", ".join(f"{d['name']} ({d['specialization']})" for d in doctors)
            state["response"] = f"Which doctor would you like to see? Available: {names}."
        else:
            state["response"] = f"To book your appointment, please also provide: {', '.join(missing)}."
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
    state["response"] = (
        f"Your appointment is confirmed for {appointment.appointment_date} at {appointment.appointment_time}."
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