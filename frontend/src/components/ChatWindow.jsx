// The Patient AI Assistant chat interface.
//
// Three things beyond plain chat live here:
// 1. On mount, it loads the existing conversation from the backend
//    (GET /conversations/history) so a page refresh doesn't lose it.
// 2. A patient can explicitly trigger a guided booking flow (via the
//    calendar button or a quick-topic chip) - a form appears inline,
//    then a review step, and nothing is booked until they confirm.
//    Free-text booking through the AI still works too; this is an
//    additional, more guided path for when someone specifically asks.
// 3. A patient can attach a document (paperclip button) right from the
//    chat instead of a separate upload form - it uploads immediately
//    and the assistant confirms it in the conversation, matching the
//    "continuous assistant" feel rather than a static form elsewhere.
import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react'
import ChatBubble from './ChatBubble.jsx'
import InlineBookingForm from './InlineBookingForm.jsx'
import BookingConfirmCard from './BookingConfirmCard.jsx'
import { sendMessage, getConversationHistory, bookAppointment, uploadDocument } from '../lib/api.js'
import { useAuth } from '../context/AuthContext.jsx'

const GREETING = { role: 'ai', type: 'text', content: "Hi, I'm your CareBridge assistant. How can I help today?" }

const ChatWindow = forwardRef(function ChatWindow(_props, ref) {
  const { session } = useAuth()
  const [messages, setMessages] = useState([GREETING])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState(null)
  const [isSending, setIsSending] = useState(false)
  const [isBooking, setIsBooking] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    getConversationHistory(session.access_token)
      .then((history) => {
        if (history.length === 0) return
        setConversationId(history[0].conversation_id)
        setMessages(
          history.map((m) => ({
            role: m.sender_role === 'patient' ? 'patient' : 'ai',
            type: 'text',
            content: m.content,
          }))
        )
      })
      .catch(() => {}) // no history yet is fine - keep the default greeting
  }, [session.access_token])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function deliver(content) {
    if (!content.trim() || isSending) return

    setMessages((prev) => [...prev, { role: 'patient', type: 'text', content }])
    setInput('')
    setIsSending(true)
    setError('')

    try {
      const reply = await sendMessage({ token: session.access_token, content, conversationId })
      setConversationId(reply.conversation_id)
      setMessages((prev) => [...prev, { role: 'ai', type: 'text', content: reply.content }])
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSending(false)
    }
  }

  function openBookingForm() {
    setMessages((prev) => [
      ...prev,
      { role: 'ai', type: 'text', content: 'Sure! Kindly fill out this form to book your appointment:' },
      { role: 'ai', type: 'form' },
    ])
  }

  function handleFormSubmit(details) {
    setMessages((prev) => [
      ...prev.filter((m) => m.type !== 'form'),
      { role: 'ai', type: 'confirm', details },
    ])
  }

  async function handleConfirmBooking(details) {
    setIsBooking(true)
    try {
      await bookAppointment(session.access_token, details)
      setMessages((prev) => [
        ...prev.filter((m) => m.type !== 'confirm'),
        {
          role: 'ai',
          type: 'text',
          content: `✅ Your appointment is booked! ${details.date} at ${details.time} with Dr. ${details.doctorName}. Kindly review it under "My Appointments".`,
        },
      ])
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'ai', type: 'text', content: `Sorry, that didn't go through: ${err.message}` }])
    } finally {
      setIsBooking(false)
    }
  }

  function handleCancelBooking() {
    setMessages((prev) => [
      ...prev.filter((m) => m.type !== 'confirm'),
      { role: 'ai', type: 'text', content: 'No problem — let me know if you\u2019d like to try again.' },
    ])
  }

  function openFilePicker() {
    fileInputRef.current?.click()
  }

  async function handleFileSelected(event) {
    const file = event.target.files?.[0]
    event.target.value = '' // lets the same file be picked again later
    if (!file) return

    if (file.type !== 'application/pdf') {
      setMessages((prev) => [...prev, { role: 'ai', type: 'text', content: 'I can only accept PDF files right now — could you try that format?' }])
      return
    }

    setMessages((prev) => [...prev, { role: 'patient', type: 'text', content: `📎 ${file.name}` }])
    setIsUploading(true)
    try {
      await uploadDocument(session.access_token, { file, documentType: 'other' })
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          type: 'text',
          content: `Got it — I've added "${file.name}" to your record. You can rename its category anytime under Documents, and feel free to ask me about it.`,
        },
      ])
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'ai', type: 'text', content: `That upload didn't go through: ${err.message}` }])
    } finally {
      setIsUploading(false)
    }
  }

  useImperativeHandle(ref, () => ({
    sendPrompt: (text) => deliver(text),
    openBookingForm,
  }))

  const handleSend = (event) => {
    event.preventDefault()
    deliver(input)
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {messages.map((m, i) => {
          if (m.type === 'form') return <InlineBookingForm key={i} onSubmit={handleFormSubmit} />
          if (m.type === 'confirm') {
            return (
              <BookingConfirmCard
                key={i}
                details={m.details}
                isBooking={isBooking}
                onConfirm={() => handleConfirmBooking(m.details)}
                onCancel={handleCancelBooking}
              />
            )
          }
          return <ChatBubble key={i} role={m.role} content={m.content} />
        })}
        {isSending && <ChatBubble role="ai" content="Typing…" />}
        {isUploading && <ChatBubble role="ai" content="Uploading and reading your document…" />}
        <div ref={bottomRef} />
      </div>

      {error && <p className="px-4 pb-2 text-sm text-danger">{error}</p>}

      <form onSubmit={handleSend} className="flex items-center gap-2 border-t border-ink/10 p-3 dark:border-ink-dark/10">
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          onChange={handleFileSelected}
          className="hidden"
        />
        <button
          type="button"
          onClick={openFilePicker}
          disabled={isUploading}
          title="Attach a document (PDF)"
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-ink/15 text-lg
                     text-ink transition hover:border-accent hover:text-accent disabled:opacity-60 dark:border-ink-dark/15 dark:text-ink-dark"
        >
          ⬆️
        </button>
        <button
          type="button"
          onClick={openBookingForm}
          title="Book an appointment"
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-ink/15 text-lg
                     text-ink transition hover:border-accent hover:text-accent dark:border-ink-dark/15 dark:text-ink-dark"
        >
          📅
        </button>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your visits, medications, or symptoms…"
          className="flex-1 rounded-full border border-ink/15 bg-panel px-4 py-2.5 text-sm text-ink
                     outline-none transition focus:border-accent dark:border-ink-dark/15
                     dark:bg-panel-dark dark:text-ink-dark"
        />
        <button
          type="submit"
          disabled={isSending}
          className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white
                     transition hover:bg-accent-light disabled:opacity-60"
        >
          Send
        </button>
      </form>
    </div>
  )
})

export default ChatWindow