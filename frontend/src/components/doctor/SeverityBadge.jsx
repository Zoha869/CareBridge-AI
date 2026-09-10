// Small color-coded pill for a concern's severity. Distinct hues so
// a doctor can triage the list at a glance without reading every word.
const STYLES = {
  urgent: 'bg-danger/10 text-danger ring-1 ring-danger/25',
  moderate: 'bg-amber-500/10 text-amber-700 ring-1 ring-amber-500/25 dark:text-amber-400',
  low: 'bg-accent/10 text-accent ring-1 ring-accent/25',
}

export default function SeverityBadge({ severity }) {
  const style = STYLES[severity] || STYLES.low
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${style}`}>
      {severity}
    </span>
  )
}