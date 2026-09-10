// Handles the redirect back from Google after GoogleButton starts
// the OAuth flow.
//
// Supabase's client library automatically parses the URL and
// establishes a session; this page just waits for that session,
// reads the intended role from the query string, and finalizes the
// login by calling our backend's /auth/google endpoint.
import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { supabase } from '../lib/supabaseClient.js'
import { loginWithGoogle } from '../lib/api.js'
import { useAuth } from '../context/AuthContext.jsx'

export default function AuthCallback() {
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login } = useAuth()

  useEffect(() => {
    const finalizeGoogleLogin = async () => {
      const role = searchParams.get('role') || 'patient'

      // Supabase needs a brief moment to parse the redirect and
      // populate the session after this page mounts.
      const { data, error: sessionError } = await supabase.auth.getSession()

      if (sessionError || !data.session) {
        setError('Could not complete Google sign-in. Please try again.')
        return
      }

      try {
        const result = await loginWithGoogle({
          accessToken: data.session.access_token,
          role,
        })
        login(result)
        navigate(result.role === 'doctor' ? '/welcome/doctor' : '/welcome/patient')
      } catch (err) {
        setError(err.message)
      }
    }

    finalizeGoogleLogin()
  }, [])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-surface dark:bg-surface-dark">
      {error ? (
        <p className="max-w-sm text-center text-sm text-danger">{error}</p>
      ) : (
        <p className="text-sm text-muted dark:text-muted-dark">Finishing sign-in…</p>
      )}
    </div>
  )
}
