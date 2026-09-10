const STATUS_STYLES = {
  confirmed: 'bg-accent/10 text-accent',
  pending: 'bg-amber-500/10 text-amber-700 dark:text-amber-400',
  completed: 'bg-ink/10 text-muted dark:text-muted-dark',
  cancelled: 'bg-danger/10 text-danger',
}

export default function AppointmentListItem({ appointment }) {
  return (
    <div className="flex items-center justify-between border-b border-ink/6 py-3 last:border-0 dark:border-ink-dark/8">
      <div>
        <p className="text-sm font-medium text-ink dark:text-ink-dark">
          Dr. {appointment.doctor_name || 'Unknown'}
        </p>
        <p className="text-xs text-muted dark:text-muted-dark">
          {appointment.appointment_date} at {appointment.appointment_time?.slice(0, 5)} — {appointment.reason}
        </p>
      </div>
      <span className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium capitalize ${STATUS_STYLES[appointment.status] || ''}`}>
        {appointment.status}
      </span>
    </div>
  )
}