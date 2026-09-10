// Temporary post-login screen for patients.
//
// Phase 1 only proves that authentication and role routing work end
// to end — the real Patient AI Assistant interface arrives in
// Phase 2. This screen confirms to the person which side of the
// system they landed on.
import { useNavigate } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export default function WelcomePatient() {
  const { session, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-surface px-6 text-center dark:bg-surface-dark">
      <ThemeToggle />
      <span className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-accent/10 text-2xl text-accent">
        +
      </span>
      <h1 className="mt-6 font-display text-3xl font-medium text-ink dark:text-ink-dark">
        Welcome, {session?.full_name || 'friend'}.
      </h1>
      <p className="mt-2 max-w-md text-sm text-muted dark:text-muted-dark">
        You're signed in on the patient side of CareBridge-AI. Your assistant,
        appointments, and care history will appear here in the next phase.
      </p>
      <button
        onClick={handleLogout}
        className="mt-8 rounded-lg border border-ink/15 px-4 py-2 text-sm font-medium
                   text-ink transition hover:border-ink/30 dark:border-ink-dark/15 dark:text-ink-dark"
      >
        Sign out
      </button>
    </div>
  )
}
