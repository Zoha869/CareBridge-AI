// One summary tile on the dashboard header. iconBg/iconColor let each
// stat have its own accent without a different component per card.
export default function StatCard({ label, value, sublabel, iconBg, iconColor, icon }) {
  return (
    <div className="rounded-2xl border border-ink/8 bg-panel p-5 dark:border-ink-dark/10 dark:bg-panel-dark">
      <div className="flex items-center gap-3">
        <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${iconBg}`}>
          <span className={`text-lg ${iconColor}`}>{icon}</span>
        </div>
        <div>
          <p className="font-display text-2xl leading-none text-ink dark:text-ink-dark">{value}</p>
          <p className="mt-1 text-sm text-muted dark:text-muted-dark">{label}</p>
        </div>
      </div>
      {sublabel && <p className="mt-3 text-xs text-muted dark:text-muted-dark">{sublabel}</p>}
    </div>
  )
}