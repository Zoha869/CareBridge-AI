// src/components/doctor/ClinicalCopilot.jsx
// The Doctor AI Assistant panel. When a patient is selected on the
// dashboard, this can also write to that patient's record: say a
// medicine name / dosage / instructions, or "mark this patient as
// visited", and it's saved directly - no separate form needed.
import { useEffect, useRef, useState } from 'react'
import { doctorChat } from '../../lib/api.js'
import { useAuth } from '../../context/AuthContext.jsx'

const QUICK_ACTIONS = [
  { label: 'Today\u2019s schedule', message: 'What does my schedule look like today?' },
  { label: 'Who needs attention?', message: 'Which of my patients have urgent or moderate open concerns right now?' },
]

export default function ClinicalCopilot({ doctorFirstName, selectedPatientId, selectedPatientName }) {
  const { session } = useAuth()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    setMessages([
      {
        role: 'ai',
        content: `Good day, Dr. ${doctorFirstName}. I'm your Clinical Copilot - I can summarize a patient, walk through today's schedule, or flag who needs attention. Select a patient from the list, then just tell me the medicine, dosage, instructions, or "mark as visited" - I'll save it to their record.`,
      },
    ])
  }, [doctorFirstName])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(messageText) {
    const content = messageText ?? input
    if (!content.trim() || isSending) return

    setMessages((prev) => [...prev, { role: 'doctor', content }])
    setInput('')
    setIsSending(true)

    try {
      const reply = await doctorChat(session.access_token, {
        message: content,
        patientId: selectedPatientId,
        patientNameHint: selectedPatientName,
      })
      setMessages((prev) => [...prev, { role: 'ai', content: reply.response }])
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'ai', content: `Something went wrong: ${err.message}` }])
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="flex h-full flex-col rounded-2xl border border-ink/8 bg-panel dark:border-ink-dark/10 dark:bg-panel-dark">
      <div className="flex items-center gap-2 border-b border-ink/8 px-4 py-3.5 dark:border-ink-dark/10">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent text-white">✦</div>
        <div>
          <p className="font-display text-sm font-medium text-ink dark:text-ink-dark">Clinical Copilot</p>
          <p className="text-xs text-muted dark:text-muted-dark">Grounded in your real schedule &amp; records</p>
        </div>
      </div>

      {selectedPatientName && (
        <p className="border-b border-ink/8 px-4 py-2 text-xs text-muted dark:border-ink-dark/10 dark:text-muted-dark">
          Talking about: <span className="font-medium text-ink dark:text-ink-dark">{selectedPatientName}</span>
        </p>
      )}

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'doctor' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] whitespace-pre-line rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${
                m.role === 'doctor'
                  ? 'rounded-br-sm bg-primary text-white'
                  : 'rounded-bl-sm bg-surface text-ink dark:bg-surface-dark dark:text-ink-dark'
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {isSending && <p className="text-xs text-muted dark:text-muted-dark">Thinking…</p>}
        <div ref={bottomRef} />
      </div>

      <div className="flex flex-wrap gap-2 border-t border-ink/8 px-4 py-3 dark:border-ink-dark/10">
        {QUICK_ACTIONS.map((qa) => (
          <button
            key={qa.label}
            onClick={() => send(qa.message)}
            className="rounded-full border border-ink/12 px-3 py-1.5 text-xs text-ink transition
                       hover:border-accent hover:text-accent dark:border-ink-dark/15 dark:text-ink-dark"
          >
            {qa.label}
          </button>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          send()
        }}
        className="flex items-center gap-2 border-t border-ink/8 p-3 dark:border-ink-dark/10"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about a patient, or prescribe/instruct…"
          className="flex-1 rounded-full border border-ink/15 bg-surface px-4 py-2 text-sm text-ink
                     outline-none transition focus:border-accent dark:border-ink-dark/15
                     dark:bg-surface-dark dark:text-ink-dark"
        />
        <button
          type="submit"
          disabled={isSending}
          className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-white
                     transition hover:bg-primary-light disabled:opacity-60"
        >
          →
        </button>
      </form>
    </div>
  )
}