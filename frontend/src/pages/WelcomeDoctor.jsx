// Temporary post-login screen for doctors.
//
// Mirrors WelcomePatient — confirms the doctor-side routing works;
// the real Doctor Dashboard (patient list, today's appointments)
// is built in Phase 5.
import { useNavigate } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export default function WelcomeDoctor() {
  const { session, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-surface px-6 text-center dark:bg-surface-dark">
      <ThemeToggle />
      <span className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-2xl text-primary">
        +
      </span>
      <h1 className="mt-6 font-display text-3xl font-medium text-ink dark:text-ink-dark">
        Welcome, Dr. {session?.full_name || ''}.
      </h1>
      <p className="mt-2 max-w-md text-sm text-muted dark:text-muted-dark">
        You're signed in on the doctor side of CareBridge-AI. Your dashboard,
        patient summaries, and today's appointments will appear here in a later phase.
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
