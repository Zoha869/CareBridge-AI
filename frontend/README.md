# CareBridge-AI — Frontend (Phase 1)

React + Vite + Tailwind. Implements login, signup (role selection),
Google Sign-In, dark/light mode, and two placeholder "Welcome"
screens that confirm role-based routing after authentication.

## Design

- **Colors:** deep clinical blue `#1B4B66` (primary), teal-green
  `#2E8B78` (accent), off-white `#F7FAF9` (background)
- **Type:** Fraunces (headings) + Inter (body/forms)
- **Layout:** split-screen — brand panel with a heartbeat-line motif
  on the left, form on the right; stacks to full-width on mobile

## 1. Install dependencies

```bash
cd frontend
npm install
```

## 2. Configure environment variables

```bash
cp .env.example .env
```

Fill in:

```
VITE_SUPABASE_URL=https://vmpuvkvaavojjcjplubo.supabase.co
VITE_SUPABASE_ANON_KEY=<same anon public key used in the backend .env>
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## 3. Add the frontend's redirect URL to Google Cloud Console

Google Sign-In redirects back to **this frontend**, not the backend,
so a second URL needs to be authorized (in addition to the Supabase
callback URL already configured):

1. Google Cloud Console → APIs & Services → Credentials → your OAuth
   Client ID → **Authorized redirect URIs** — this should already
   contain Supabase's callback URL from Phase 1 backend setup, no
   change needed here.
2. Same screen → **Authorized JavaScript origins** — add:
   ```
   http://localhost:5173
   ```
   This lets Google accept requests that originate from the local
   dev server. Add the production frontend URL here later too, once
   deployed.

## 4. Run the dev server

```bash
npm run dev
```

Visit **http://localhost:5173** — it redirects to `/login`.

Make sure the **backend is also running** (`uvicorn app.main:app --reload`
from the `backend` folder) — the frontend calls it directly for
email/password signup and login.

## How the pieces connect

- **Email/Password signup or login:** the form calls the backend's
  `/api/v1/auth/signup` or `/api/v1/auth/login` directly (see
  `src/lib/api.js`). The backend talks to Supabase and returns
  `{ access_token, role, full_name, ... }`, which is stored via
  `AuthContext` and used to route to the correct welcome screen.
- **Google Sign-In:** `GoogleButton` calls Supabase's client-side
  `signInWithOAuth`, which redirects to Google and back to
  `/auth/callback?role=<chosen role>`. `AuthCallback` reads the
  resulting Supabase session and sends its access token to the
  backend's `/api/v1/auth/google`, which verifies it and creates the
  patient/doctor profile row on first login.
- **Role routing:** whichever flow completes, the backend's response
  includes `role`, and the app navigates to `/welcome/patient` or
  `/welcome/doctor` accordingly.

## Next: Phase 2

The Welcome screens are replaced with the real Patient AI Assistant
chat interface, built against the `conversations` and `messages`
tables already defined in the backend.
