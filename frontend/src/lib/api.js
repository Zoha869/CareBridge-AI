// src/lib/api.js
// Thin wrapper around fetch() for talking to the FastAPI backend.
//
// Every function here returns the parsed JSON response and throws
// an Error with the backend's detail message on failure, so callers
// can show it directly to the user.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
const STORAGE_KEY = 'carebridge-session'

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
    const error = new Error(data.detail || 'Something went wrong. Please try again.')
    error.status = response.status
    throw error
  }

  return data
}

/** Registers a new patient or doctor with email + password. */
export function signupWithEmail({ email, password, fullName, role, specialization }) {
  return request('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: fullName, role, specialization }),
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

/**
 * Exchanges the stored refresh_token for a fresh access_token.
 * Updates localStorage directly and fires an event so AuthContext
 * (which only reads localStorage on mount) picks up the new token.
 *
 * If several requests hit 401 at the same time (e.g. the dashboard
 * firing 5 parallel calls right when the token expires), they must
 * NOT each call /auth/refresh separately — Supabase only accepts the
 * refresh_token once per short window, so the others would come back
 * 401 too. This shares a single in-flight refresh across all callers.
 */
let refreshPromise = null

async function refreshAccessToken() {
  if (refreshPromise) return refreshPromise

  refreshPromise = (async () => {
    const saved = localStorage.getItem(STORAGE_KEY)
    const session = saved ? JSON.parse(saved) : null

    if (!session?.refresh_token) {
      throw new Error('Session expired. Please log in again.')
    }

    const data = await request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: session.refresh_token }),
    })

    const updatedSession = { ...session, ...data }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSession))
    window.dispatchEvent(new CustomEvent('carebridge-session-updated', { detail: updatedSession }))

    return updatedSession.access_token
  })()

  try {
    return await refreshPromise
  } finally {
    refreshPromise = null
  }
}

async function authedRequest(path, token, options = {}) {
  try {
    return await request(path, {
      ...options,
      headers: { Authorization: `Bearer ${token}`, ...options.headers },
    })
  } catch (err) {
    if (err.status === 401) {
      const freshToken = await refreshAccessToken()
      return request(path, {
        ...options,
        headers: { Authorization: `Bearer ${freshToken}`, ...options.headers },
      })
    }
    throw err
  }
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

/** Uploads a document (PDF) to the patient's own record - also feeds the RAG index. */
export async function uploadDocument(token, { file, documentType }) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('document_type', documentType)

  const response = await fetch(`${API_BASE_URL}/patients/me/documents`, {
    method: 'POST',
    // No Content-Type header - the browser sets the multipart boundary itself.
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || 'Upload failed. Please try again.')
  }
  return data
}

/** Lists the logged-in patient's own uploaded documents. */
export function listMyDocuments(token) {
  return authedRequest('/patients/me/documents', token)
}

/** Doctor uploads a document (PDF) on behalf of one of their patients - shared with the patient. */
export async function uploadDocumentForPatient(token, patientId, { file, documentType }) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('document_type', documentType)

  const response = await fetch(`${API_BASE_URL}/doctors/patients/${patientId}/documents`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || 'Upload failed. Please try again.')
  }
  return data
}

/** Doctor's view of every document on a given patient's record (their own uploads + shared ones). */
export function getPatientDocuments(token, patientId) {
  return authedRequest(`/doctors/patients/${patientId}/documents`, token)
}

/** Gets a short-lived signed URL to view/download one of the patient's own documents. */
export function getMyDocumentDownloadUrl(token, documentId) {
  return authedRequest(`/patients/me/documents/${documentId}/download`, token)
}

/** Doctor: gets a short-lived signed URL to view/download one of a patient's documents. */
export function getPatientDocumentDownloadUrl(token, patientId, documentId) {
  return authedRequest(`/doctors/patients/${patientId}/documents/${documentId}/download`, token)
}