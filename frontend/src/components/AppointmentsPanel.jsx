// Slide-over panel showing the patient's appointment history.
// Fetches doctors separately since /appointments/me only returns
// doctor_id, not a name.
import { useEffect, useState } from 'react'
import AppointmentCard from './AppointmentCard.jsx'
import { getMyAppointments, getDoctors } from '../lib/api.js'
import { useAuth } from '../context/AuthContext.jsx'

export default function AppointmentsPanel({ onClose }) {
  const { session } = useAuth()
  const [appointments, setAppointments] = useState([])
  const [doctorsById, setDoctorsById] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [appointmentsData, doctorsData] = await Promise.all([
          getMyAppointments(session.access_token),
          getDoctors(session.access_token),
        ])
        setAppointments(appointmentsData)
        setDoctorsById(Object.fromEntries(doctorsData.map((d) => [d.id, d])))
      } catch (err) {
        setError(err.message)
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [session.access_token])

  return (
    <div className="absolute inset-y-0 right-0 z-10 w-full max-w-sm border-l border-ink/10 bg-surface shadow-xl dark:border-ink-dark/10 dark:bg-surface-dark">
      <div className="flex items-center justify-between border-b border-ink/10 px-4 py-4 dark:border-ink-dark/10">
        <h2 className="font-display text-base font-medium text-ink dark:text-ink-dark">
          My Appointments
        </h2>
        <button onClick={onClose} className="text-sm text-muted hover:text-ink dark:text-muted-dark dark:hover:text-ink-dark">
          Close
        </button>
      </div>

      <div className="space-y-3 overflow-y-auto p-4">
        {isLoading && <p className="text-sm text-muted dark:text-muted-dark">Loading…</p>}
        {error && <p className="text-sm text-danger">{error}</p>}
        {!isLoading && !error && appointments.length === 0 && (
          <p className="text-sm text-muted dark:text-muted-dark">
            No appointments yet — ask the assistant to book one.
          </p>
        )}
        {appointments.map((appt) => (
          <AppointmentCard
            key={appt.id}
            appointment={appt}
            doctorName={doctorsById[appt.doctor_id]?.full_name}
          />
        ))}
      </div>
    </div>
  )
}