// Selectable role card ("I am a Patient" / "I am a Doctor").
//
// Shown as two side-by-side cards above the login/signup form so the
// chosen role is visible at a glance and persists across both tabs —
// matching the reference design's role-first flow.
export default function RoleCard({ role, label, description, icon, selected, onSelect }) {
  const accentClasses =
    role === 'doctor'
      ? { ring: 'border-accent bg-accent/5', badge: 'bg-accent', text: 'text-accent' }
      : { ring: 'border-primary bg-primary/5', badge: 'bg-primary', text: 'text-primary' }

  return (
    <button
      type="button"
      onClick={() => onSelect(role)}
      className={`relative flex min-h-[168px] flex-col items-center gap-2 rounded-[10px] border px-3 py-4 text-center
        transition
        ${selected
          ? `border-2 ${accentClasses.ring}`
          : 'border-ink/10 hover:border-ink/20 dark:border-ink-dark/10'}`}
    >
      {selected && (
        <span
          className={`absolute right-2 top-2 flex h-5 w-5 items-center justify-center
                      rounded-full text-white ${accentClasses.badge}`}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
      )}

      <span className={`mt-1 ${selected ? accentClasses.text : 'text-muted dark:text-muted-dark'}`}>
        {icon}
      </span>

      <span className={`text-sm font-semibold ${selected ? accentClasses.text : 'text-ink dark:text-ink-dark'}`}>
        {label}
      </span>
      <p className="text-xs leading-snug text-muted dark:text-muted-dark">{description}</p>
    </button>
  )
}