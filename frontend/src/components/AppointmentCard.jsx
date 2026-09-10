// Displays one appointment. doctorName is resolved on the parent
// panel since /appointments/me only returns doctor_id.
const STATUS_STYLES = {
  confirmed: 'bg-accent/15 text-accent',
  pending: 'bg-yellow-500/15 text-yellow-600',
  completed: 'bg-ink/10 text-muted',
  cancelled: 'bg-danger/15 text-danger',
}

export default function AppointmentCard({ appointment, doctorName }) {
  return (
    <div className="rounded-xl border border-ink/10 bg-panel p-4 dark:border-ink-dark/10 dark:bg-panel-dark">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-medium text-ink dark:text-ink-dark">{doctorName || 'Doctor'}</p>
          <p className="text-sm text-muted dark:text-muted-dark">{appointment.reason}</p>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${STATUS_STYLES[appointment.status]}`}>
          {appointment.status}
        </span>
      </div>
      <p className="mt-2 text-sm text-ink/70 dark:text-ink-dark/70">
        {appointment.appointment_date} at {appointment.appointment_time}
      </p>
    </div>
  )
}