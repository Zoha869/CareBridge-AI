// A single message in the conversation — patient messages align right
// in the primary color, AI replies align left on a soft panel.
import MessageContent from './MessageContent.jsx'
export default function ChatBubble({ role, content }) {
  const isPatient = role === 'patient'

  return (
    <div className={`flex ${isPatient ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
          isPatient
            ? 'rounded-br-sm bg-primary text-white'
            : 'rounded-bl-sm bg-panel text-ink dark:bg-panel-dark dark:text-ink-dark'
        }`}
      >
        <MessageContent text={content} />
      </div>
    </div>
  )
}
