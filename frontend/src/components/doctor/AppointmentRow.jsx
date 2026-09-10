// src/components/doctor/AppointmentRow.jsx
import InitialsAvatar from './InitialsAvatar.jsx'

export default function AppointmentRow({ appointment, onView, onMarkVisited }) {
  const canMarkVisited = appointment.status === 'confirmed' || appointment.status === 'pending'

  return (
    <div className="flex items-center gap-4 border-b border-ink/6 py-3 last:border-0 dark:border-ink-dark/8">
      <div className="w-16 shrink-0 text-sm font-medium text-ink dark:text-ink-dark">
        {appointment.appointment_time?.slice(0, 5)}
      </div>
      <InitialsAvatar name={appointment.patient_name} size={36} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-ink dark:text-ink-dark">{appointment.patient_name}</p>
        <p className="truncate text-xs text-muted dark:text-muted-dark">{appointment.reason}</p>
      </div>
      <span className="shrink-0 text-xs capitalize text-muted dark:text-muted-dark">{appointment.status}</span>
      {canMarkVisited && (
        <button
          onClick={() => onMarkVisited(appointment)}
          className="shrink-0 rounded-lg border border-accent/40 px-3 py-1.5 text-xs font-medium text-accent
                     transition hover:bg-accent/10"
        >
          Mark Visited
        </button>
      )}
      <button
        onClick={() => onView(appointment)}
        className="shrink-0 rounded-lg border border-ink/12 px-3 py-1.5 text-xs font-medium text-primary
                   transition hover:bg-primary/5 dark:border-ink-dark/12 dark:text-accent-light"
      >
        View
      </button>
    </div>
  )
}