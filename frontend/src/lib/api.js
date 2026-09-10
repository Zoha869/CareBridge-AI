// src/lib/api.js
// Thin wrapper around fetch() for talking to the FastAPI backend.
//
// Every function here returns the parsed JSON response and throws
// an Error with the backend's detail message on failure, so callers
// can show it directly to the user.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || 'Something went wrong. Please try again.')
  }

  return data
}

/** Registers a new patient or doctor with email + password. */
export function signupWithEmail({ email, password, fullName, role }) {
  return request('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: fullName, role }),
  })
}

/** Logs in an existing user with email + password. */
export function loginWithEmail({ email, password }) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

/**
 * Finalizes a Google sign-in: sends the Supabase access token
 * (obtained from the OAuth redirect) to the backend, which verifies
 * it and creates a matching profile row on first login.
 */
export function loginWithGoogle({ accessToken, role }) {
  return request('/auth/google', {
    method: 'POST',
    body: JSON.stringify({ access_token: accessToken, role }),
  })
}

async function authedRequest(path, token, options = {}) {
  return request(path, {
    ...options,
    headers: { Authorization: `Bearer ${token}`, ...options.headers },
  })
}

/** Sends a patient message to the AI assistant and returns its reply. */
export function sendMessage({ token, content, conversationId }) {
  return authedRequest('/conversations/messages', token, {
    method: 'POST',
    body: JSON.stringify({ content, conversation_id: conversationId }),
  })
}

/** Fetches the logged-in patient's appointment history. */
export function getMyAppointments(token) {
  return authedRequest('/appointments/me', token)
}

/** Lists all doctors — used to show doctor names in appointment history and booking. */
export function getDoctors(token) {
  return authedRequest('/doctors', token)
}

/** The logged-in doctor's own profile (name, specialization). */
export function getMyProfile(token) {
  return authedRequest('/doctors/me', token)
}

/** Today's confirmed appointments for the logged-in doctor. */
export function getTodaysAppointments(token) {
  return authedRequest('/appointments/today', token)
}

/** Doctor marks their own appointment as completed ("visited") or cancelled. */
export function updateAppointmentStatus(token, appointmentId, status) {
  return authedRequest(`/appointments/${appointmentId}/status`, token, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}

/** Every patient the logged-in doctor has an appointment with. */
export function getMyPatients(token) {
  return authedRequest('/doctors/patients', token)
}

/** Full dossier (concerns, visits, medications, instructions, summary) for one patient. */
export function getPatientDossier(token, patientId) {
  return authedRequest(`/doctors/patients/${patientId}`, token)
}

/** Doctor AI Assistant - ask about the schedule, or (with a selected patient)
 *  prescribe a medicine / give an instruction / mark a visit in natural language. */
export function doctorChat(token, { message, patientId, patientNameHint }) {
  return authedRequest('/doctors/chat', token, {
    method: 'POST',
    body: JSON.stringify({ message, patient_id: patientId, patient_name_hint: patientNameHint }),
  })
}

/** The logged-in patient's own profile (name, DOB, etc.). */
export function getMyPatientProfile(token) {
  return authedRequest('/patients/me', token)
}

/** The logged-in patient's recorded medications. */
export function getMedications(token) {
  return authedRequest('/patients/me/medications', token)
}

/** The logged-in patient's recorded doctor instructions. */
export function getInstructions(token) {
  return authedRequest('/patients/me/instructions', token)
}

/** The logged-in patient's open concerns. */
export function getOpenConcerns(token) {
  return authedRequest('/patients/me/concerns', token)
}

/** Books an appointment directly via the form (alternative to the conversational flow). */
export function bookAppointment(token, { doctorId, date, time, reason }) {
  return authedRequest('/appointments', token, {
    method: 'POST',
    body: JSON.stringify({ doctor_id: doctorId, appointment_date: date, appointment_time: time, reason }),
  })
}

/** Restores the ongoing conversation on page load. */
export function getConversationHistory(token) {
  return authedRequest('/conversations/history', token)
}