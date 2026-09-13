// Patient's main screen from Phase 2 onward — the continuous AI
// assistant described in the proposal, not just an appointment
// chatbot. Replaces the Phase 1 placeholder WelcomePatient screen.
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle.jsx'
import ChatWindow from '../components/ChatWindow.jsx'
import AppointmentsPanel from '../components/AppointmentsPanel.jsx'
import DocumentsPanel from '../components/DocumentsPanel.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export default function PatientChat() {
  const { session, logout } = useAuth()
  const navigate = useNavigate()
  const [showAppointments, setShowAppointments] = useState(false)
  const [showDocuments, setShowDocuments] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="relative flex h-screen flex-col overflow-hidden bg-surface dark:bg-surface-dark">
      <header className="flex items-center justify-between border-b border-ink/10 px-5 py-4 dark:border-ink-dark/10">
        <div>
          <h1 className="font-display text-lg font-medium text-ink dark:text-ink-dark">
            CareBridge Assistant
          </h1>
          <p className="text-xs text-muted dark:text-muted-dark">
            Signed in as {session?.full_name}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowDocuments(true)}
            className="rounded-lg border border-ink/15 px-3 py-1.5 text-xs font-medium
                       text-ink transition hover:border-ink/30 dark:border-ink-dark/15 dark:text-ink-dark"
          >
            My Documents
          </button>
          <button
            onClick={() => setShowAppointments(true)}
            className="rounded-lg border border-ink/15 px-3 py-1.5 text-xs font-medium
                       text-ink transition hover:border-ink/30 dark:border-ink-dark/15 dark:text-ink-dark"
          >
            My Appointments
          </button>
          <ThemeToggle />
          <button
            onClick={handleLogout}
            className="rounded-lg border border-ink/15 px-3 py-1.5 text-xs font-medium
                       text-ink transition hover:border-ink/30 dark:border-ink-dark/15 dark:text-ink-dark"
          >
            Sign out
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-hidden">
        <ChatWindow />
      </div>

      {showAppointments && <AppointmentsPanel onClose={() => setShowAppointments(false)} />}
      {showDocuments && <DocumentsPanel onClose={() => setShowDocuments(false)} />}
    </div>
  )
}