// Vite configuration for the CareBridge-AI frontend.
// Uses the standard React plugin; no custom build settings are
// required for Phase 1.
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
