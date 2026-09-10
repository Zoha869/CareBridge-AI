// Small icon button that switches between dark and light mode.
// Placed in a fixed corner so it's reachable from every auth screen.
import { useTheme } from '../context/ThemeContext.jsx'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle dark and light mode"
      className="fixed top-5 right-5 z-20 flex h-10 w-10 items-center justify-center
                 rounded-full border border-ink/10 bg-panel text-ink shadow-sm
                 transition hover:border-accent/40 hover:text-accent
                 dark:border-ink-dark/10 dark:bg-panel-dark dark:text-ink-dark"
    >
      {theme === 'dark' ? (
        // Sun icon (shown when in dark mode, to switch to light)
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" strokeLinecap="round" />
        </svg>
      ) : (
        // Moon icon (shown when in light mode, to switch to dark)
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      )}
    </button>
  )
}
