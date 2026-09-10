// Left brand panel, shown on large screens as the wide illustrative
// side of the auth card.
//
// Mirrors the reference layout's structure — logo, headline, a short
// feature list with icons, and a friendly healthcare illustration.
const features = [
  {
    title: 'Smart Communication',
    description: 'Secure, real-time communication between patients and doctors.',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 11.5a8.4 8.4 0 0 1-8.9 8.4 8.6 8.6 0 0 1-3.4-.7L3 21l1.8-5.4A8.5 8.5 0 1 1 21 11.5Z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: 'Easy Appointments',
    description: 'Book, manage, and get reminders for upcoming visits.',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M3 10h18M8 3v4M16 3v4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: 'Private & Secure',
    description: 'Your data is protected with enterprise-grade security.',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 3l7 3v6c0 4.5-3 8-7 9-4-1-7-4.5-7-9V6l7-3Z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
]

export default function BrandPanel() {
  return (
    <div className="relative flex w-full shrink-0 flex-col justify-between overflow-hidden bg-[#eef5ff] px-6 py-7 sm:px-10 sm:py-9 lg:min-h-[732px] lg:w-[52%] lg:px-10 lg:py-10 dark:bg-[#17263b]">
      <div>
        <div className="flex items-center gap-2">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 21s-7-4.4-9.5-9C.7 8 2 4 6 4c2 0 3.5 1.2 4 2.2C10.5 5.2 12 4 14 4c4 0 5.3 4 3.5 8-2.5 4.6-9.5 9-9.5 9Z" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M9 12h2l1-2 2 4 1-2h1" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
          <div>
            <p className="font-display text-lg font-medium text-ink dark:text-ink-dark">
              CareBridge <span className="text-primary">AI</span>
            </p>
            <p className="text-xs text-muted dark:text-muted-dark">Bridging Care. Connecting Lives.</p>
          </div>
        </div>

        <h1 className="mt-7 font-display text-3xl font-medium leading-tight text-ink dark:text-ink-dark sm:mt-10">
          Better Care,<br />Stronger <span className="text-primary">Connection</span>
        </h1>
        <p className="mt-3 max-w-sm text-sm text-muted dark:text-muted-dark">
          CareBridge AI connects patients and doctors seamlessly, making
          healthcare accessible, personal, and efficient.
        </p>

        <ul className="mt-7 hidden space-y-4 sm:mt-8 sm:block sm:space-y-5">
          {features.map((feature) => (
            <li key={feature.title} className="flex gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-panel text-primary shadow-sm dark:bg-panel-dark">
                {feature.icon}
              </span>
              <div>
                <p className="text-sm font-semibold text-ink dark:text-ink-dark">{feature.title}</p>
                <p className="text-xs text-muted dark:text-muted-dark">{feature.description}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="relative mt-7 h-56 overflow-hidden rounded-2xl bg-[#dcecff] sm:h-64 lg:mt-8 lg:h-72 dark:bg-[#213b58]">
        <div className="absolute -right-12 -top-16 h-48 w-48 rounded-full border-[18px] border-white/35 dark:border-white/10" />
        <div className="absolute -bottom-24 -left-12 h-52 w-52 rounded-full border-[22px] border-primary/10" />
        <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-white/45 to-transparent dark:from-[#17263b]/50" />

        <div className="absolute left-[15%] right-[15%] top-[42%] h-2 rounded-full bg-primary/20" />
        <div className="absolute left-[15%] right-[15%] top-[42%] h-0.5 bg-primary/75" />
        <div className="absolute left-1/2 top-[42%] h-16 w-16 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/60 bg-white/70 shadow-lg backdrop-blur-sm dark:border-white/20 dark:bg-[#213b58]/80" />
        <div className="absolute left-1/2 top-[42%] flex h-9 w-9 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-primary text-xl font-semibold text-white shadow-md">+</div>

        <div className="absolute left-[8%] top-[25%] flex flex-col items-center">
          <span className="mb-1 rounded-lg rounded-bl-sm bg-white px-2.5 py-1 text-[10px] font-semibold text-primary shadow-sm">I need care</span>
          <div className="relative flex h-16 w-16 items-center justify-center rounded-full border-4 border-white bg-[#8db8e9] text-white shadow-md sm:h-20 sm:w-20">
            <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
              <circle cx="12" cy="7.5" r="3.5" />
              <path d="M4.5 21c.8-4.2 3.3-6.5 7.5-6.5s6.7 2.3 7.5 6.5" strokeLinecap="round" />
            </svg>
          </div>
          <span className="mt-2 text-xs font-semibold text-ink dark:text-ink-dark">Patient</span>
        </div>

        <div className="absolute right-[8%] top-[25%] flex flex-col items-center">
          <span className="mb-1 rounded-lg rounded-br-sm bg-primary px-2.5 py-1 text-[10px] font-semibold text-white shadow-sm">Here to help</span>
          <div className="relative flex h-16 w-16 items-center justify-center rounded-full border-4 border-white bg-accent text-white shadow-md sm:h-20 sm:w-20">
            <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
              <circle cx="12" cy="6.5" r="3" />
              <path d="M4 21c.6-4.2 3.1-6.4 8-6.4s7.4 2.2 8 6.4M8.5 14.5v-3M15.5 14.5v-3M6 10h12" strokeLinecap="round" />
            </svg>
          </div>
          <span className="mt-2 text-xs font-semibold text-ink dark:text-ink-dark">Doctor</span>
        </div>

        <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 items-center gap-1.5 rounded-full border border-white/70 bg-white/75 px-3 py-1.5 text-[10px] font-semibold text-primary shadow-sm backdrop-blur-sm dark:border-white/15 dark:bg-[#17263b]/75 dark:text-accent-light">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" /> Care connected
        </div>
      </div>

      <div className="mt-5 hidden items-center gap-3 rounded-xl bg-white/80 p-4 shadow-sm sm:flex dark:bg-panel-dark/80">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17 20v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M10 10a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM21 20v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
        <div>
          <p className="text-sm font-semibold text-ink dark:text-ink-dark">Together for Better Health</p>
          <p className="text-xs text-muted dark:text-muted-dark">
            Whether you're seeking care or providing it, we help bridge the gap.
          </p>
        </div>
      </div>
    </div>
  )
}