// A real, working alternative to booking through chat - posts
// straight to POST /appointments. Doctor list comes from the same
// /doctors endpoint the chat's booking flow already uses.
import { useEffect, useState } from 'react'
import { getDoctors, bookAppointment } from '../../lib/api.js'
import { useAuth } from '../../context/AuthContext.jsx'

export default function BookAppointmentForm() {
  const { session } = useAuth()
  const [doctors, setDoctors] = useState([])
  const [doctorId, setDoctorId] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [reason, setReason] = useState('')
  const [status, setStatus] = useState({ state: 'idle', message: '' })

  useEffect(() => {
    getDoctors(session.access_token).then(setDoctors).catch(() => {})
  }, [session.access_token])

  async function handleSubmit(event) {
    event.preventDefault()
    setStatus({ state: 'loading', message: '' })
    try {
      await bookAppointment(session.access_token, { doctorId, date, time, reason })
      setStatus({ state: 'success', message: 'Appointment booked!' })
      setDoctorId('')
      setDate('')
      setTime('')
      setReason('')
    } catch (err) {
      setStatus({ state: 'error', message: err.message })
    }
  }

  const inputClass =
    'w-full rounded-lg border border-ink/15 bg-surface px-3 py-2 text-sm text-ink outline-none ' +
    'transition focus:border-accent dark:border-ink-dark/15 dark:bg-surface-dark dark:text-ink-dark'

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label className="mb-1 block text-xs font-medium text-muted dark:text-muted-dark">Doctor</label>
        <select value={doctorId} onChange={(e) => setDoctorId(e.target.value)} required className={inputClass}>
          <option value="" disabled>Choose a doctor</option>
          {doctors.map((d) => (
            <option key={d.id} value={d.id}>
              {d.full_name} {d.specialization ? `— ${d.specialization}` : ''}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-muted dark:text-muted-dark">Date</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required className={inputClass} />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-muted dark:text-muted-dark">Time</label>
          <input type="time" value={time} onChange={(e) => setTime(e.target.value)} required className={inputClass} />
        </div>
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-muted dark:text-muted-dark">Reason</label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          required
          rows={2}
          placeholder="What's this visit for?"
          className={inputClass}
        />
      </div>

      <button
        type="submit"
        disabled={status.state === 'loading'}
        className="w-full rounded-lg bg-primary py-2.5 text-sm font-medium text-white transition hover:bg-primary-light disabled:opacity-60"
      >
        {status.state === 'loading' ? 'Booking…' : 'Book Appointment'}
      </button>

      {status.state === 'success' && <p className="text-sm text-accent">{status.message}</p>}
      {status.state === 'error' && <p className="text-sm text-danger">{status.message}</p>}
    </form>
  )
}