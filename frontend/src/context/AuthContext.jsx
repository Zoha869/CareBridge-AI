// Authentication context.
//
// Holds the current session (access token, role, name, email) in
// memory and localStorage so the person stays logged in across page
// reloads. This is intentionally simple for Phase 1 — later phases
// can add token refresh logic once the chat/appointment features
// need longer-lived sessions.
import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

const STORAGE_KEY = 'carebridge-session'

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? JSON.parse(saved) : null
  })

  const login = (sessionData) => {
    setSession(sessionData)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessionData))
  }

  const logout = () => {
    setSession(null)
    localStorage.removeItem(STORAGE_KEY)
  }

  return (
    <AuthContext.Provider value={{ session, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within an AuthProvider')
  return context
}
