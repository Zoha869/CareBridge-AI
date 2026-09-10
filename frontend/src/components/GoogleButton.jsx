// "Continue with Google" button.
//
// Kicks off Supabase's client-side OAuth redirect. When the person
// returns from Google, Supabase completes the session automatically
// and our AuthCallback page takes over to sync the profile with the
// backend.
import { supabase } from '../lib/supabaseClient.js'

export default function GoogleButton({ role, label = 'Continue with Google' }) {
  const handleClick = async () => {
    // The chosen role travels through the redirect via query param so
    // AuthCallback knows whether to create a patient or doctor profile
    // on first-time Google sign-in.
    const redirectTo = `${window.location.origin}/auth/callback?role=${role}`

    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo },
    })
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className="flex w-full items-center justify-center gap-3 rounded-lg border
                 border-ink/15 bg-panel px-4 py-2.5 text-sm font-medium text-ink
                 transition hover:border-ink/30 hover:bg-ink/[0.03]
                 dark:border-ink-dark/15 dark:bg-panel-dark dark:text-ink-dark
                 dark:hover:bg-white/5"
    >
      <svg width="18" height="18" viewBox="0 0 48 48">
        <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.6l6.4-6.4C35.5 3 30.1 1 24 1 14.6 1 6.5 6.4 2.6 14.2l7.6 5.9C12.2 14 17.6 9.5 24 9.5z" />
        <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.2-.4-4.7H24v9h12.7c-.6 3-2.3 5.5-4.9 7.2l7.5 5.8c4.4-4 6.9-10 6.9-17.3z" />
        <path fill="#FBBC05" d="M10.2 28.1a14.5 14.5 0 0 1 0-8.2l-7.6-5.9a24 24 0 0 0 0 20l7.6-5.9z" />
        <path fill="#34A853" d="M24 47c6.1 0 11.5-2 15.3-5.6l-7.5-5.8c-2.1 1.4-4.8 2.3-7.8 2.3-6.4 0-11.8-4.5-13.8-10.5l-7.6 5.9C6.5 41.6 14.6 47 24 47z" />
      </svg>
      {label}
    </button>
  )
}