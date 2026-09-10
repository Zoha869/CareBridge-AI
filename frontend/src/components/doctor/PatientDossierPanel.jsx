// Full patient record, shown as a slide-over when a doctor clicks
// "View Case" / "View" anywhere on the dashboard. Structured per the
// proposal's Doctor View: Overview -> Concerns -> Visits ->
// Medications/Instructions -> Summary.
import { useEffect, useState } from 'react'
import InitialsAvatar from './InitialsAvatar.jsx'
import SeverityBadge from './SeverityBadge.jsx'
import { getPatientDossier } from '../../lib/api.js'
import { useAuth } from '../../context/AuthContext.jsx'

export default function PatientDossierPanel({ patientId, onClose }) {
  const { session } = useAuth()
  const [dossier, setDossier] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getPatientDossier(session.access_token, patientId)
      .then(setDossier)
      .catch((err) => setError(err.message))
  }, [patientId, session.access_token])

  return (
    <div className="fixed inset-0 z-20 flex justify-end bg-ink/30 backdrop-blur-sm" onClick={onClose}>
      <div
        className="h-full w-full max-w-lg overflow-y-auto bg-surface p-6 shadow-2xl dark:bg-surface-dark"
        onClick={(e) => e.stopPropagation()}
      >
        <button onClick={onClose} className="mb-4 text-sm text-muted hover:text-ink dark:text-muted-dark dark:hover:text-ink-dark">
          ← Close
        </button>

        {error && <p className="text-sm text-danger">{error}</p>}
        {!dossier && !error && <p className="text-sm text-muted dark:text-muted-dark">Loading patient record…</p>}

        {dossier && (
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <InitialsAvatar name={dossier.full_name} size={56} />
              <div>
                <h2 className="font-display text-xl text-ink dark:text-ink-dark">{dossier.full_name}</h2>
                <p className="text-sm text-muted dark:text-muted-dark">
                  {[dossier.gender, dossier.date_of_birth].filter(Boolean).join(' · ') || 'No demographic info on file'}
                </p>
              </div>
            </div>

            <section className="rounded-2xl border border-accent/20 bg-accent/5 p-4">
              <h3 className="font-display text-sm font-medium text-accent">AI Summary</h3>
              <p className="mt-2 text-sm leading-relaxed text-ink dark:text-ink-dark">
                {dossier.summary || 'No summary generated yet - one will appear once this patient logs a concern.'}
              </p>
            </section>

            <section>
              <h3 className="font-display text-sm font-medium text-ink dark:text-ink-dark">Open Concerns</h3>
              {dossier.open_concerns.length === 0 ? (
                <p className="mt-2 text-sm text-muted dark:text-muted-dark">None on record.</p>
              ) : (
                <ul className="mt-2 space-y-2">
                  {dossier.open_concerns.map((c, i) => (
                    <li key={i} className="flex items-start justify-between gap-3 rounded-xl bg-panel p-3 dark:bg-panel-dark">
                      <span className="text-sm text-ink dark:text-ink-dark">{c.description}</span>
                      <SeverityBadge severity={c.severity} />
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <div className="grid grid-cols-2 gap-4">
              <section>
                <h3 className="font-display text-sm font-medium text-ink dark:text-ink-dark">Recent Visits</h3>
                {dossier.recent_visits.length === 0 ? (
                  <p className="mt-2 text-sm text-muted dark:text-muted-dark">None on record.</p>
                ) : (
                  <ul className="mt-2 space-y-2">
                    {dossier.recent_visits.map((v, i) => (
                      <li key={i} className="text-sm text-ink dark:text-ink-dark">
                        <span className="font-medium">{v.visit_date}</span>
                        {v.notes && <p className="text-xs text-muted dark:text-muted-dark">{v.notes}</p>}
                      </li>
                    ))}
                  </ul>
                )}
              </section>

              <section>
                <h3 className="font-display text-sm font-medium text-ink dark:text-ink-dark">Medications</h3>
                {dossier.medications.length === 0 ? (
                  <p className="mt-2 text-sm text-muted dark:text-muted-dark">None on record.</p>
                ) : (
                  <ul className="mt-2 space-y-2">
                    {dossier.medications.map((m, i) => (
                      <li key={i} className="text-sm text-ink dark:text-ink-dark">
                        <span className="font-medium">{m.name}</span>
                        {m.dosage && <span className="text-xs text-muted dark:text-muted-dark"> — {m.dosage}</span>}
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </div>

            <section>
              <h3 className="font-display text-sm font-medium text-ink dark:text-ink-dark">Doctor Instructions</h3>
              {dossier.instructions.length === 0 ? (
                <p className="mt-2 text-sm text-muted dark:text-muted-dark">None on record.</p>
              ) : (
                <ul className="mt-2 space-y-1.5 text-sm text-ink dark:text-ink-dark">
                  {dossier.instructions.map((ins, i) => (
                    <li key={i}>• {ins.instruction_text}</li>
                  ))}
                </ul>
              )}
            </section>

            <section>
              <h3 className="font-display text-sm font-medium text-ink dark:text-ink-dark">Appointment History</h3>
              <ul className="mt-2 space-y-2">
                {dossier.appointments.map((a, i) => (
                  <li key={i} className="flex items-center justify-between text-sm">
                    <span className="text-ink dark:text-ink-dark">
                      {a.appointment_date} at {a.appointment_time?.slice(0, 5)} — {a.reason}
                    </span>
                    <span className="text-xs capitalize text-muted dark:text-muted-dark">{a.status}</span>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        )}
      </div>
    </div>
  )
}