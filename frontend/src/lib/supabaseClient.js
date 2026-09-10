// Supabase client for the frontend.
//
// This is used ONLY for the Google OAuth redirect flow
// (supabase.auth.signInWithOAuth). Email/password signup and login
// go through our own FastAPI backend instead, so that all
// business logic (creating the matching patient/doctor profile row)
// lives in one place.
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
