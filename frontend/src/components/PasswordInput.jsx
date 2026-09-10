// Password field with a lock icon and a show/hide toggle (eye icon),
// matching the reference design's input style.
import { useState } from 'react'

export default function PasswordInput({ value, onChange, placeholder = 'Password', minLength }) {
  const [visible, setVisible] = useState(false)

  return (
    <div className="relative">
      <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted dark:text-muted-dark">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="5" y="11" width="14" height="9" rx="2" />
          <path d="M8 11V7a4 4 0 0 1 8 0v4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>

      <input
        type={visible ? 'text' : 'password'}
        required
        minLength={minLength}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="h-11 w-full rounded-lg border border-ink/15 bg-panel pl-11 pr-10
                   text-base text-ink outline-none transition focus:border-primary
                   sm:text-sm dark:border-ink-dark/15 dark:bg-panel-dark dark:text-ink-dark"
      />

      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        aria-label={visible ? 'Hide password' : 'Show password'}
        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink dark:text-muted-dark dark:hover:text-ink-dark"
      >
        {visible ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 3l18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 4.2A9.7 9.7 0 0 1 12 4c5 0 9 4 10 8-.4 1.4-1.1 2.7-2 3.8M6.5 6.7C4.6 8 3.2 9.8 2 12c1 4 5 8 10 8 1.5 0 2.9-.3 4.1-.9" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M2 12c1-4 5-8 10-8s9 4 10 8c-1 4-5 8-10 8s-9-4-10-8Z" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        )}
      </button>
    </div>
  )
}