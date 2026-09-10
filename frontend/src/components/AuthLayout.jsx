// Shared two-panel layout for the login and signup screens: a
// brand panel on the left, and the passed-in form content on the
// right. Centers the form vertically and caps its width for
// readable line lengths.
//
// On small screens the full split-panel doesn't fit, so BrandPanel
// hides itself (see its own lg:flex) and this layout shows a compact
// gradient header bar instead — the person still sees the brand and
// gets a sense of place before landing on the form.
import BrandPanel from './BrandPanel.jsx'
import ThemeToggle from './ThemeToggle.jsx'

export default function AuthLayout({ heading, subheading, children }) {
  return (
    <div className="flex min-h-screen w-full flex-col bg-surface dark:bg-surface-dark lg:flex-row">
      <ThemeToggle />

      {/* Compact brand header — mobile and tablet only */}
      <div className="flex items-center gap-2 bg-gradient-to-r from-primary to-accent px-6 py-5 font-display text-lg text-white lg:hidden">
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-white/15">
          +
        </span>
        CareBridge-AI
      </div>

      <BrandPanel heading={heading} subheading={subheading} />

      <div className="flex w-full flex-1 items-center justify-center px-5 py-10 sm:px-6 lg:w-1/2 lg:py-12">
        <div className="w-full max-w-sm">{children}</div>
      </div>
    </div>
  )
}