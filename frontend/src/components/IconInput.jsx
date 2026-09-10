// Text/email input with a small leading icon, matching the reference
// design's icon-prefixed fields (mail icon for email, person icon
// for full name).
export default function IconInput({ icon, type = 'text', value, onChange, placeholder, required = true }) {
  return (
    <div className="relative">
      <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted dark:text-muted-dark">
        {icon}
      </span>
      <input
        type={type}
        required={required}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="h-11 w-full rounded-lg border border-ink/15 bg-panel pl-11 pr-3
                   text-base text-ink outline-none transition focus:border-primary
                   sm:text-sm dark:border-ink-dark/15 dark:bg-panel-dark dark:text-ink-dark"
      />
    </div>
  )
}

// Reusable small icons, kept here so both the mail and person
// variants stay visually consistent with PasswordInput's icon style.
export const MailIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="5" width="18" height="14" rx="2" />
    <path d="M3 7l9 6 9-6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

export const PersonIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="8" r="4" />
    <path d="M4 20c1.5-4 5-6 8-6s6.5 2 8 6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)