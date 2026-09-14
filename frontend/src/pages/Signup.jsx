// Signup screen: role selection (Patient / Doctor), full name,
// email + password, or "Continue with Google".
//
// The role toggle is the one decision unique to signup — it's shown
// as two equal-weight buttons rather than a dropdown so the choice
// is visible at a glance before anyone starts typing.
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout.jsx'
import GoogleButton from '../components/GoogleButton.jsx'
import { signupWithEmail } from '../lib/api.js'
import { useAuth } from '../context/AuthContext.jsx'

export default function Signup() {
  const [role, setRole] = useState('patient')
  const [fullName, setFullName] = useState('')
  const [specialization, setSpecialization] = useState('')
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
      const result = await signupWithEmail({ email, password, fullName, role, specialization: role === 'doctor' ? specialization : undefined })
      login(result)
      navigate(role === 'doctor' ? '/welcome/doctor' : '/welcome/patient')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      heading="Care, coordinated."
      subheading="One account connects you with your patients or your care team."
    >
      <h2 className="font-display text-2xl font-medium text-ink dark:text-ink-dark">Create your account</h2>
      <p className="mt-1 text-sm text-muted dark:text-muted-dark">
        Already have an account?{' '}
        <Link to="/login" className="font-medium text-accent hover:underline">
          Sign in
        </Link>
      </p>

      {/* Role selector */}
      <div className="mt-6 grid grid-cols-2 gap-3">
        {['patient', 'doctor'].map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => setRole(option)}
            className={`rounded-lg border px-4 py-2.5 text-sm font-medium capitalize transition
              ${role === option
                ? 'border-accent bg-accent/10 text-accent'
                : 'border-ink/15 text-muted hover:border-ink/30 dark:border-ink-dark/15 dark:text-muted-dark'}`}
          >
            {option}
          </button>
        ))}
      </div>

      <div className="mt-6">
        <GoogleButton role={role} label={`Sign up as ${role} with Google`} />
      </div>

      <div className="my-6 flex items-center gap-3 text-xs text-muted dark:text-muted-dark">
        <span className="h-px flex-1 bg-ink/10 dark:bg-ink-dark/10" />
        or continue with email
        <span className="h-px flex-1 bg-ink/10 dark:bg-ink-dark/10" />
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-ink dark:text-ink-dark">Full name</label>
          <input
            type="text"
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="mt-1 w-full rounded-lg border border-ink/15 bg-panel px-3 py-2.5
                       text-base text-ink outline-none transition focus:border-accent sm:text-sm
                       dark:border-ink-dark/15 dark:bg-panel-dark dark:text-ink-dark"
            placeholder="Jane Doe"
          />
        </div>

        {role === 'doctor' && (
          <div>
            <label className="block text-sm font-medium text-ink dark:text-ink-dark">Specialization</label>
            <input
              type="text"
              required
              value={specialization}
              onChange={(e) => setSpecialization(e.target.value)}
              className="mt-1 w-full rounded-lg border border-ink/15 bg-panel px-3 py-2.5
                         text-base text-ink outline-none transition focus:border-accent sm:text-sm
                         dark:border-ink-dark/15 dark:bg-panel-dark dark:text-ink-dark"
              placeholder="e.g. Cardiology, General Medicine"
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-ink dark:text-ink-dark">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg border border-ink/15 bg-panel px-3 py-2.5
                       text-base text-ink outline-none transition focus:border-accent sm:text-sm
                       dark:border-ink-dark/15 dark:bg-panel-dark dark:text-ink-dark"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-ink dark:text-ink-dark">Password</label>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg border border-ink/15 bg-panel px-3 py-2.5
                       text-base text-ink outline-none transition focus:border-accent sm:text-sm
                       dark:border-ink-dark/15 dark:bg-panel-dark dark:text-ink-dark"
            placeholder="At least 8 characters"
          />
        </div>

        {error && (
          <p className="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">{error}</p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white
                     transition hover:bg-primary-light disabled:opacity-60"
        >
          {isSubmitting ? 'Creating account…' : 'Create account'}
        </button>
      </form>
    </AuthLayout>
  )
}