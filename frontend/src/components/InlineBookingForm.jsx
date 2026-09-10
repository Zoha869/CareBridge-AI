// Renders inside the chat as a special "bubble" when the patient
// explicitly asks to book an appointment. Collects the details, then
// hands them to a review/confirm step - it never books directly.
import { useEffect, useState } from 'react'
import { getDoctors } from '../lib/api.js'
import { useAuth } from '../context/AuthContext.jsx'

export default function InlineBookingForm({ onSubmit }) {
  const { session } = useAuth()
  const [doctors, setDoctors] = useState([])
  const [doctorId, setDoctorId] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [reason, setReason] = useState('')

  useEffect(() => {
    getDoctors(session.access_token).then(setDoctors).catch(() => {})
  }, [session.access_token])

  const inputClass =
    'w-full rounded-lg border border-ink/15 bg-surface px-3 py-2 text-sm text-ink outline-none ' +
    'transition focus:border-accent dark:border-ink-dark/15 dark:bg-surface-dark dark:text-ink-dark'

  function handleSubmit(event) {
    event.preventDefault()
    const doctor = doctors.find((d) => d.id === doctorId)
    onSubmit({ doctorId, doctorName: doctor?.full_name, date, time, reason })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-[85%] space-y-3 rounded-2xl rounded-bl-sm bg-panel p-4 dark:bg-panel-dark"
    >
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

      <button type="submit" className="w-full rounded-lg bg-primary py-2 text-sm font-medium text-white transition hover:bg-primary-light">
        Continue
      </button>
    </form>
  )
}