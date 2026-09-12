// src/components/MessageContent.jsx
// AI replies (especially RAG-grounded ones) come back with light markdown
// from the LLM - *bold* section labels, "- " bullet lines, blank-line
// paragraph breaks. Renders those properly instead of a raw string with
// literal asterisks and squished line breaks, without pulling in a full
// markdown library for it.

function renderInline(text, keyPrefix) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g)
  return parts.map((part, i) =>
    part.startsWith('*') && part.endsWith('*') ? (
      <strong key={`${keyPrefix}-${i}`}>
        {part.startsWith('**') ? part.slice(2, -2) : part.slice(1, -1)}
      </strong>
    ) : (
      <span key={`${keyPrefix}-${i}`}>{part}</span>
    )
  )
}

export default function MessageContent({ text }) {
  const lines = text.split('\n')

  return (
    <>
      {lines.map((line, i) => {
        const trimmed = line.trim()
        if (trimmed.startsWith('- ')) {
          return (
            <div key={i} className="flex gap-1.5 pl-1">
              <span>•</span>
              <span>{renderInline(trimmed.slice(2), i)}</span>
            </div>
          )
        }
        if (trimmed === '') return <div key={i} className="h-2" />
        return <div key={i}>{renderInline(line, i)}</div>
      })}
    </>
  )
}