import InitialsAvatar from './InitialsAvatar.jsx'
import SeverityBadge from './SeverityBadge.jsx'

export default function PatientInsightRow({ patient, onView }) {
  return (
    <tr className="border-b border-ink/6 last:border-0 dark:border-ink-dark/8">
      <td className="py-3 pr-4">
        <div className="flex items-center gap-3">
          <InitialsAvatar name={patient.full_name} size={36} />
          <span className="text-sm font-medium text-ink dark:text-ink-dark">{patient.full_name}</span>
        </div>
      </td>
      <td className="py-3 pr-4 text-sm text-muted dark:text-muted-dark">
        {patient.last_appointment_date ? `Last seen ${patient.last_appointment_date}` : 'No visits yet'}
      </td>
      <td className="py-3 pr-4">
        {patient.top_severity ? (
          <SeverityBadge severity={patient.top_severity} />
        ) : (
          <span className="text-sm text-muted dark:text-muted-dark">—</span>
        )}
      </td>
      <td className="py-3 pr-4 text-sm text-muted dark:text-muted-dark">
        {patient.has_summary ? 'AI summary ready' : 'No summary yet'}
      </td>
      <td className="py-3 text-right">
        <button
          onClick={() => onView(patient)}
          className="rounded-lg bg-primary/5 px-3 py-1.5 text-xs font-medium text-primary
                     transition hover:bg-primary/10 dark:bg-accent/10 dark:text-accent-light"
        >
          View Case
        </button>
      </td>
    </tr>
  )
}