// src/pages/DoctorDashboard.jsx
// Doctor Dashboard - Phase 5 UI. Every number and row here comes
// from real endpoints (appointments/today, doctors/patients,
// doctors/me) - no placeholder stats or fake nav items for features
// that don't exist yet (billing, lab results, messages, etc.).
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle.jsx'
import StatCard from '../components/doctor/StatCard.jsx'
import AppointmentRow from '../components/doctor/AppointmentRow.jsx'
import PatientInsightRow from '../components/doctor/PatientInsightRow.jsx'
import ClinicalCopilot from '../components/doctor/ClinicalCopilot.jsx'
import PatientDossierPanel from '../components/doctor/PatientDossierPanel.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { getMyProfile, getTodaysAppointments, getMyPatients, updateAppointmentStatus } from '../lib/api.js'

function greeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

export default function DoctorDashboard() {
  const { session, logout } = useAuth()
  const navigate = useNavigate()

  const [profile, setProfile] = useState(null)
  const [appointments, setAppointments] = useState([])
  const [patients, setPatients] = useState([])
  const [search, setSearch] = useState('')
  const [selectedPatientId, setSelectedPatientId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const token = session.access_token
    Promise.all([getMyProfile(token), getTodaysAppointments(token), getMyPatients(token)])
      .then(([profileData, appts, pts]) => {
        setProfile(profileData)
        setAppointments(appts)
        setPatients(pts)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [session.access_token])

  const filteredPatients = useMemo(() => {
    if (!search.trim()) return patients
    return patients.filter((p) => p.full_name.toLowerCase().includes(search.toLowerCase()))
  }, [patients, search])

  const needAttentionCount = patients.filter((p) => p.top_severity === 'urgent' || p.top_severity === 'moderate').length
  const summariesReadyCount = patients.filter((p) => p.has_summary).length
  const selectedPatientName = patients.find((p) => p.patient_id === selectedPatientId)?.full_name

  // Doctor marks an appointment as completed ("visited") - updates the
  // backend, then reflects the new status straight in local state.
  async function handleMarkVisited(appointment) {
    try {
      const updated = await updateAppointmentStatus(session.access_token, appointment.id, 'completed')
      setAppointments((prev) => prev.map((a) => (a.id === updated.id ? { ...a, status: updated.status } : a)))
    } catch (err) {
      setError(err.message)
    }
  }

  function handleLogout() {
    logout()
    navigate('/login')
  }

  if (loading) {
    return <div className="flex h-screen items-center justify-center text-muted dark:text-muted-dark">Loading dashboard…</div>
  }

  return (
    <div className="flex h-screen bg-surface dark:bg-surface-dark">
      {/* Sidebar */}
      <aside className="flex w-60 shrink-0 flex-col justify-between bg-primary px-5 py-6 text-white">
        <div>
          <h1 className="font-display text-lg font-medium">CareBridge-AI</h1>
          <p className="text-xs text-white/60">Doctor Portal</p>

          <nav className="mt-10 space-y-1">
            <div className="flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-medium">
              Dashboard
            </div>
          </nav>
        </div>

        <button
          onClick={handleLogout}
          className="rounded-lg border border-white/20 px-3 py-2 text-left text-xs font-medium text-white/80 transition hover:bg-white/10"
        >
          Sign out
        </button>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center gap-4 border-b border-ink/8 px-8 py-4 dark:border-ink-dark/10">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search patients by name…"
            className="w-80 rounded-full border border-ink/12 bg-panel px-4 py-2 text-sm text-ink
                       outline-none transition focus:border-accent dark:border-ink-dark/15
                       dark:bg-panel-dark dark:text-ink-dark"
          />
          <div className="ml-auto flex items-center gap-3">
            <ThemeToggle />
            <div className="text-right">
              <p className="text-sm font-medium text-ink dark:text-ink-dark">{profile?.full_name}</p>
              <p className="text-xs text-muted dark:text-muted-dark">{profile?.specialization || 'Doctor'}</p>
            </div>
          </div>
        </header>

        <div className="flex flex-1 gap-6 overflow-hidden p-8">
          <div className="flex-1 space-y-6 overflow-y-auto pr-2">
            <div>
              <h2 className="font-display text-2xl text-ink dark:text-ink-dark">
                {greeting()}, Dr. {profile?.full_name?.split(' ').pop()} 👋
              </h2>
              <p className="mt-1 text-sm text-muted dark:text-muted-dark">
                Here's what's happening with your patients today.
              </p>
            </div>

            {error && <p className="text-sm text-danger">{error}</p>}

            <div className="grid grid-cols-4 gap-4">
              <StatCard
                label="Total Patients"
                value={patients.length}
                iconBg="bg-primary/10"
                iconColor="text-primary"
                icon="👥"
              />
              <StatCard
                label="Appointments Today"
                value={appointments.length}
                iconBg="bg-accent/10"
                iconColor="text-accent"
                icon="📅"
              />
              <StatCard
                label="Need Attention"
                value={needAttentionCount}
                sublabel="Urgent or moderate concerns"
                iconBg="bg-danger/10"
                iconColor="text-danger"
                icon="⚠️"
              />
              <StatCard
                label="AI Summaries"
                value={summariesReadyCount}
                sublabel="Ready to review"
                iconBg="bg-primary/10"
                iconColor="text-primary"
                icon="✦"
              />
            </div>

            <section className="rounded-2xl border border-ink/8 bg-panel p-5 dark:border-ink-dark/10 dark:bg-panel-dark">
              <h3 className="font-display text-base text-ink dark:text-ink-dark">Today's Appointments</h3>
              {appointments.length === 0 ? (
                <p className="mt-3 text-sm text-muted dark:text-muted-dark">Nothing scheduled for today.</p>
              ) : (
                <div className="mt-2">
                  {appointments.map((a) => (
                    <AppointmentRow
                      key={a.id}
                      appointment={a}
                      onView={() => setSelectedPatientId(a.patient_id)}
                      onMarkVisited={handleMarkVisited}
                    />
                  ))}
                </div>
              )}
            </section>

            <section className="rounded-2xl border border-ink/8 bg-panel p-5 dark:border-ink-dark/10 dark:bg-panel-dark">
              <h3 className="font-display text-base text-ink dark:text-ink-dark">Patient Insights</h3>
              {filteredPatients.length === 0 ? (
                <p className="mt-3 text-sm text-muted dark:text-muted-dark">No patients found.</p>
              ) : (
                <table className="mt-2 w-full text-left">
                  <tbody>
                    {filteredPatients.map((p) => (
                      <PatientInsightRow key={p.patient_id} patient={p} onView={() => setSelectedPatientId(p.patient_id)} />
                    ))}
                  </tbody>
                </table>
              )}
            </section>
          </div>

          <div className="w-96 shrink-0">
            <ClinicalCopilot
              doctorFirstName={profile?.full_name?.split(' ')[0]}
              selectedPatientId={selectedPatientId}
              selectedPatientName={selectedPatientName}
            />
          </div>
        </div>
      </div>

      {selectedPatientId && (
        <PatientDossierPanel patientId={selectedPatientId} onClose={() => setSelectedPatientId(null)} />
      )}
    </div>
  )
}