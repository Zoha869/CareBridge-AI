// Top-level route table.
import { Navigate, Route, Routes } from 'react-router-dom'
import Auth from './pages/Auth.jsx'
import AuthCallback from './pages/AuthCallback.jsx'
import PatientDashboard from './pages/PatientDashboard.jsx'
import DoctorDashboard from './pages/DoctorDashboard.jsx'
import { useAuth } from './context/AuthContext.jsx'

function RequireSession({ children }) {
  const { session } = useAuth()
  return session ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Auth initialTab="login" />} />
      <Route path="/signup" element={<Auth initialTab="signup" />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route
        path="/welcome/patient"
        element={
          <RequireSession>
            <PatientDashboard />
          </RequireSession>
        }
      />
      <Route
        path="/welcome/doctor"
        element={
          <RequireSession>
            <DoctorDashboard />
          </RequireSession>
        }
      />
    </Routes>
  )
}