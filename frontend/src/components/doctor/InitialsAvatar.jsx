// Deterministic color from the name so the same patient always gets
// the same avatar color across the app - no stock photos.
const PALETTE = ['#1B4B66', '#2E8B78', '#B4693E', '#6B5CA5', '#3F7D6B', '#A6543F']

function colorFor(name) {
  const sum = [...(name || '')].reduce((acc, ch) => acc + ch.charCodeAt(0), 0)
  return PALETTE[sum % PALETTE.length]
}

function initialsFor(name) {
  const parts = (name || '?').trim().split(/\s+/)
  return parts.length > 1 ? parts[0][0] + parts[1][0] : parts[0].slice(0, 2)
}

export default function InitialsAvatar({ name, size = 40 }) {
  return (
    <div
      className="flex shrink-0 items-center justify-center rounded-full font-display font-medium text-white"
      style={{ width: size, height: size, backgroundColor: colorFor(name), fontSize: size * 0.4 }}
    >
      {initialsFor(name).toUpperCase()}
    </div>
  )
}