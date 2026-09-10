// Patient Dashboard - now with a collapsible (hamburger) sidebar and
// appointment booking moved fully into the chat's guided flow (see
// ChatWindow.jsx) instead of a separate always-visible form.
import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle.jsx'
import ChatWindow from '../components/ChatWindow.jsx'
import AppointmentListItem from '../components/patient/AppointmentListItem.jsx'
import StatCard from '../components/doctor/StatCard.jsx'
import SeverityBadge from '../components/doctor/SeverityBadge.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import {
  getMyPatientProfile,
  getMyAppointments,
  getMedications,
  getInstructions,
  getOpenConcerns,
} from '../lib/api.js'

const NAV_SECTIONS = [
  { id: 'overview', label: 'Overview' },
  { id: 'assistant', label: 'AI Assistant' },
  { id: 'appointments', label: 'My Appointments' },
  { id: 'medications', label: 'Medications' },
  { id: 'instructions', label: 'Doctor Instructions' },
]

const QUICK_TOPICS = [
  { label: 'My last visit', action: (chat) => chat.sendPrompt('When was my last visit and what happened?') },
  { label: 'My medications', action: (chat) => chat.sendPrompt('What medications am I currently on?') },
  { label: 'Book an appointment', action: (chat) => chat.openBookingForm() },
  { label: 'Report a new symptom', action: (chat) => chat.sendPrompt('I have a new symptom I want to report.') },
]

function greeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

export default function PatientDashboard() {
  const { session, logout } = useAuth()
  const navigate = useNavigate()
  const chatRef = useRef(null)

  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [profile, setProfile] = useState(null)
  const [appointments, setAppointments] = useState([])
  const [medications, setMedications] = useState([])
  const [instructions, setInstructions] = useState([])
  const [concerns, setConcerns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const token = session.access_token
    Promise.all([
      getMyPatientProfile(token),
      getMyAppointments(token),
      getMedications(token),
      getInstructions(token),
      getOpenConcerns(token),
    ])
      .then(([p, appts, meds, ins, cons]) => {
        setProfile(p)
        setAppointments(appts)
        setMedications(meds)
        setInstructions(ins)
        setConcerns(cons)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [session.access_token])

  const nextAppointment = useMemo(() => {
    const upcoming = appointments
      .filter((a) => a.status !== 'cancelled' && new Date(`${a.appointment_date}T${a.appointment_time}`) >= new Date())
      .sort((a, b) => new Date(`${a.appointment_date}T${a.appointment_time}`) - new Date(`${b.appointment_date}T${b.appointment_time}`))
    return upcoming[0]
  }, [appointments])

  function scrollTo(id) {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setSidebarOpen(false)
  }

  function handleLogout() {
    logout()
    navigate('/login')
  }

  if (loading) {
    return <div className="flex h-screen items-center justify-center text-muted dark:text-muted-dark">Loading your dashboard…</div>
  }

  return (
    <div className="relative flex h-screen overflow-hidden bg-surface dark:bg-surface-dark">
      {/* Sidebar - slides in as an overlay, doesn't push content */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-30 bg-ink/30 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-60 shrink-0 flex-col justify-between bg-primary px-5 py-6
                    text-white transition-transform duration-200 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div>
          <h1 className="font-display text-lg font-medium">CareBridge-AI</h1>
          <p className="text-xs text-white/60">Patient Portal</p>

          <nav className="mt-10 space-y-1">
            {NAV_SECTIONS.map((s) => (
              <button
                key={s.id}
                onClick={() => scrollTo(s.id)}
                className="block w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-white/85 transition hover:bg-white/10"
              >
                {s.label}
              </button>
            ))}
          </nav>
        </div>

        <button
          onClick={handleLogout}
          className="rounded-lg border border-white/20 px-3 py-2 text-left text-xs font-medium text-white/80 transition hover:bg-white/10"
        >
          Sign out
        </button>
      </aside>

      {/* Main content - full width, sidebar floats above */}
      <div className="flex-1 overflow-y-auto">
        <header className="flex items-center gap-3 border-b border-ink/8 px-6 py-4 dark:border-ink-dark/10">
          <button
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-ink/12 text-ink
                       transition hover:bg-ink/5 dark:border-ink-dark/15 dark:text-ink-dark"
          >
            ☰
          </button>
          <div className="flex-1">
            <h2 id="overview" className="font-display text-xl text-ink dark:text-ink-dark">
              {greeting()}, {profile?.full_name?.split(' ')[0]} 👋
            </h2>
            <p className="text-sm text-muted dark:text-muted-dark">Take care of your health — it's the most valuable thing.</p>
          </div>
          <ThemeToggle />
        </header>

        <div className="space-y-8 p-6 md:p-8">
          {error && <p className="text-sm text-danger">{error}</p>}

          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <StatCard
              label="Next Appointment"
              value={nextAppointment ? nextAppointment.appointment_date : '—'}
              sublabel={nextAppointment ? `${nextAppointment.appointment_time?.slice(0, 5)} · Dr. ${nextAppointment.doctor_name}` : 'None scheduled'}
              iconBg="bg-primary/10"
              iconColor="text-primary"
              icon="📅"
            />
            <StatCard
              label="Current Medications"
              value={medications.length}
              iconBg="bg-accent/10"
              iconColor="text-accent"
              icon="💊"
            />
            <StatCard
              label="Open Concerns"
              value={concerns.length}
              sublabel={concerns.length > 0 ? 'Logged with your doctor' : 'All clear'}
              iconBg="bg-danger/10"
              iconColor="text-danger"
              icon="⚠️"
            />
            <StatCard
              label="Doctor Instructions"
              value={instructions.length}
              sublabel="On record"
              iconBg="bg-primary/10"
              iconColor="text-primary"
              icon="📋"
            />
          </div>

          <section className="rounded-2xl bg-gradient-to-r from-primary to-accent p-6 text-white">
            <h3 className="font-display text-lg">Your AI Health Assistant</h3>
            <p className="mt-1 text-sm text-white/85">
              Ask anything about your visits, medications, or appointments — or book a new one, right here in chat.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {QUICK_TOPICS.map((qt) => (
                <button
                  key={qt.label}
                  onClick={() => {
                    scrollTo('assistant')
                    qt.action(chatRef.current)
                  }}
                  className="rounded-full bg-white/15 px-3.5 py-1.5 text-xs font-medium transition hover:bg-white/25"
                >
                  {qt.label}
                </button>
              ))}
            </div>
          </section>

          <section id="assistant" className="h-[32rem] rounded-2xl border border-ink/8 bg-panel dark:border-ink-dark/10 dark:bg-panel-dark">
            <ChatWindow ref={chatRef} />
          </section>

          <section id="appointments" className="rounded-2xl border border-ink/8 bg-panel p-5 dark:border-ink-dark/10 dark:bg-panel-dark">
            <h3 className="font-display text-base text-ink dark:text-ink-dark">My Appointments</h3>
            {appointments.length === 0 ? (
              <p className="mt-3 text-sm text-muted dark:text-muted-dark">No appointments yet.</p>
            ) : (
              <div className="mt-2">
                {appointments.map((a) => (
                  <AppointmentListItem key={a.id} appointment={a} />
                ))}
              </div>
            )}
          </section>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <section id="medications" className="rounded-2xl border border-ink/8 bg-panel p-5 dark:border-ink-dark/10 dark:bg-panel-dark">
              <h3 className="font-display text-base text-ink dark:text-ink-dark">Medications</h3>
              {medications.length === 0 ? (
                <p className="mt-3 text-sm text-muted dark:text-muted-dark">None on record.</p>
              ) : (
                <ul className="mt-2 space-y-2">
                  {medications.map((m, i) => (
                    <li key={i} className="text-sm text-ink dark:text-ink-dark">
                      <span className="font-medium">{m.name}</span>
                      {m.dosage && <span className="text-muted dark:text-muted-dark"> — {m.dosage}</span>}
                      {m.instructions && <p className="text-xs text-muted dark:text-muted-dark">{m.instructions}</p>}
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section id="instructions" className="rounded-2xl border border-ink/8 bg-panel p-5 dark:border-ink-dark/10 dark:bg-panel-dark">
              <h3 className="font-display text-base text-ink dark:text-ink-dark">Doctor Instructions</h3>
              {instructions.length === 0 ? (
                <p className="mt-3 text-sm text-muted dark:text-muted-dark">None on record.</p>
              ) : (
                <ul className="mt-2 space-y-1.5 text-sm text-ink dark:text-ink-dark">
                  {instructions.map((ins, i) => (
                    <li key={i}>• {ins.instruction_text}</li>
                  ))}
                </ul>
              )}
            </section>
          </div>

          {concerns.length > 0 && (
            <section className="rounded-2xl border border-ink/8 bg-panel p-5 dark:border-ink-dark/10 dark:bg-panel-dark">
              <h3 className="font-display text-base text-ink dark:text-ink-dark">Open Concerns</h3>
              <ul className="mt-2 space-y-2">
                {concerns.map((c, i) => (
                  <li key={i} className="flex items-center justify-between rounded-xl bg-surface p-3 dark:bg-surface-dark">
                    <span className="text-sm text-ink dark:text-ink-dark">{c.description}</span>
                    <SeverityBadge severity={c.severity} />
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}