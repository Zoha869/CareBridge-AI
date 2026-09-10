// Login screen: email + password, or "Continue with Google".
//
// A role selector (Patient / Doctor) is included because the same
// email can only belong to one role in our system, but on login the
// backend already knows the stored role — the selector here is only
// used for the Google flow, where the role is needed the very first
// time someone signs in with a given Google account.
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout.jsx'
import GoogleButton from '../components/GoogleButton.jsx'
import { loginWithEmail } from '../lib/api.js'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('patient')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const result = await loginWithEmail({ email, password })
      login(result)
      navigate(result.role === 'doctor' ? '/welcome/doctor' : '/welcome/patient')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      heading="Welcome back."
      subheading="Sign in to continue the conversation with your care team."
    >
      <h2 className="font-display text-2xl font-medium text-ink dark:text-ink-dark">Sign in</h2>
      <p className="mt-1 text-sm text-muted dark:text-muted-dark">
        New here?{' '}
        <Link to="/signup" className="font-medium text-accent hover:underline">
          Create an account
        </Link>
      </p>

      <div className="mt-6">
        <GoogleButton role={role} />
      </div>

      <div className="my-6 flex items-center gap-3 text-xs text-muted dark:text-muted-dark">
        <span className="h-px flex-1 bg-ink/10 dark:bg-ink-dark/10" />
        or continue with email
        <span className="h-px flex-1 bg-ink/10 dark:bg-ink-dark/10" />
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
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
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg border border-ink/15 bg-panel px-3 py-2.5
                       text-base text-ink outline-none transition focus:border-accent sm:text-sm
                       dark:border-ink-dark/15 dark:bg-panel-dark dark:text-ink-dark"
            placeholder="••••••••"
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
          {isSubmitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </AuthLayout>
  )
}
