// Unified authentication page: role selection + Login/Sign Up tabs
// on a single screen, matching the reference design.
//
// The chosen role (patient/doctor) persists across both tabs — a
// person picks it once, then switches between logging in and
// signing up without losing that choice.
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BrandPanel from '../components/BrandPanel.jsx'
import RoleCard from '../components/RoleCard.jsx'
import GoogleButton from '../components/GoogleButton.jsx'
import PasswordInput from '../components/PasswordInput.jsx'
import IconInput, { MailIcon, PersonIcon } from '../components/IconInput.jsx'
import ThemeToggle from '../components/ThemeToggle.jsx'
import { loginWithEmail, signupWithEmail } from '../lib/api.js'
import { useAuth } from '../context/AuthContext.jsx'

const PatientIcon = (
  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="8" r="4" />
    <path d="M4 20c1.5-4 5-6 8-6s6.5 2 8 6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const DoctorIcon = (
  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="8" cy="8" r="3" />
    <circle cx="16" cy="8" r="3" />
    <path d="M3 20c.6-3 3-5 5-5s3.5 1 4 2c.5-1 2-2 4-2s4.4 2 5 5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

export default function Auth({ initialTab = 'login' }) {
  const [role, setRole] = useState('patient')
  const [tab, setTab] = useState(initialTab)
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const result =
        tab === 'signup'
          ? await signupWithEmail({ email, password, fullName, role })
          : await loginWithEmail({ email, password })

      login(result)
      navigate(result.role === 'doctor' ? '/welcome/doctor' : '/welcome/patient')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-surface p-0 dark:bg-surface-dark sm:p-4 lg:p-5">
      <ThemeToggle />

      {/* Compact mobile top bar — logo only, no split panel on small screens */}
      <div className="fixed inset-x-0 top-0 z-10 flex items-center gap-2 border-b border-ink/10 bg-panel px-5 py-4 lg:hidden dark:border-ink-dark/10 dark:bg-panel-dark">
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary">+</span>
        <p className="font-display text-base font-medium text-ink dark:text-ink-dark">
          CareBridge <span className="text-primary">AI</span>
        </p>
      </div>

      <div className="flex w-full max-w-[1120px] flex-col overflow-hidden bg-panel pt-16 shadow-xl dark:bg-panel-dark sm:rounded-2xl sm:pt-0 lg:min-h-[732px] lg:flex-row">
        <BrandPanel />

        {/* Form column */}
        <div className="w-full px-5 py-8 sm:px-10 sm:py-10 lg:w-[48%] lg:px-12 lg:py-10">
          <div className="mx-auto max-w-[422px]">
            <h2 className="text-center font-display text-[25px] font-semibold leading-tight text-ink dark:text-ink-dark">
              Welcome to CareBridge AI
            </h2>
            <p className="mt-1 text-center text-[13px] text-muted dark:text-muted-dark">
              Please log in or sign up to continue.
            </p>

            <p className="mt-5 text-center text-sm font-semibold text-ink dark:text-ink-dark">Choose Your Role</p>
            <div className="mt-2 grid grid-cols-2 gap-3.5">
              <RoleCard
                role="patient"
                label="I am a Patient"
                description="Book appointments, consult doctors, and manage your health."
                icon={PatientIcon}
                selected={role === 'patient'}
                onSelect={setRole}
              />
              <RoleCard
                role="doctor"
                label="I am a Doctor"
                description="Manage your patients, appointments, and provide better care."
                icon={DoctorIcon}
                selected={role === 'doctor'}
                onSelect={setRole}
              />
            </div>

            {/* Login / Sign Up tabs */}
            <div className="mt-5 flex border-b border-ink/10 dark:border-ink-dark/10">
              {['login', 'signup'].map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => { setTab(option); setError('') }}
                    className={`flex-1 border-b-2 pb-2.5 text-sm font-semibold transition
                    ${tab === option
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted hover:text-ink dark:text-muted-dark dark:hover:text-ink-dark'}`}
                >
                  {option === 'login' ? 'Login' : 'Sign Up'}
                </button>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="mt-5 space-y-3.5">
              {tab === 'signup' && (
                <IconInput
                  icon={PersonIcon}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Full name"
                />
              )}

              <IconInput
                icon={MailIcon}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email address"
              />

              <PasswordInput
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={tab === 'signup' ? 8 : undefined}
              />

              {tab === 'login' && (
                <div className="text-right">
                  <button type="button" className="text-xs font-medium text-primary hover:underline">
                    Forgot password?
                  </button>
                </div>
              )}

              {error && (
                <p className="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-white
                           transition hover:bg-primary-light disabled:opacity-60"
              >
                {isSubmitting
                  ? tab === 'signup' ? 'Creating account…' : 'Signing in…'
                  : tab === 'signup' ? 'Create Account' : 'Login'}
              </button>

              <div className="flex items-center gap-3 text-xs text-muted dark:text-muted-dark">
                <span className="h-px flex-1 bg-ink/10 dark:bg-ink-dark/10" />
                OR
                <span className="h-px flex-1 bg-ink/10 dark:bg-ink-dark/10" />
              </div>

              <GoogleButton role={role} />
            </form>

            <p className="mt-5 text-center text-xs text-muted dark:text-muted-dark">
              By continuing, you agree to our{' '}
              <span className="font-medium text-primary">Terms of Service</span> and{' '}
              <span className="font-medium text-primary">Privacy Policy</span>.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}