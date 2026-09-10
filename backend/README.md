# AI-Powered Patient-Doctor Communication & Support System — Backend (Phase 1)

Phase 1 delivers the foundation: project structure, database schema,
authentication (Google Sign-In + Email/Password via Supabase), role-based
access (Patient / Doctor), and the core CRUD API endpoints.

## Folder Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── config.py           # Environment-based settings
│   │   ├── supabase_client.py  # Supabase client (anon + admin)
│   │   └── security.py         # JWT verification / current-user dependency
│   ├── db/
│   │   └── database.py         # SQLAlchemy engine, session, Base
│   ├── models/                 # SQLAlchemy ORM models (one file per table)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/
│   │   └── auth_service.py     # Signup / login business logic
│   └── api/
│       ├── deps.py             # require_patient / require_doctor / require_admin
│       └── v1/
│           ├── router.py       # Combines all routers
│           ├── auth.py         # /api/v1/auth/*
│           ├── patients.py     # /api/v1/patients/*
│           ├── doctors.py      # /api/v1/doctors/*
│           └── appointments.py # /api/v1/appointments/*
├── requirements.txt
└── .env.example
```

## 1. Create the Supabase Project

1. Go to https://supabase.com and create a new project.
2. In **Project Settings → API**, copy:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` key → `SUPABASE_ANON_KEY`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY`
3. In **Project Settings → API → JWT Settings**, copy the `JWT Secret` → `SUPABASE_JWT_SECRET`.
4. In **Project Settings → Database**, copy the **Connection Pooling** URI → `DATABASE_URL`
   (replace the password placeholder with your database password).

## 2. Enable Google Sign-In in Supabase

1. In the Supabase Dashboard, go to **Authentication → Providers → Google**.
2. Enable it and paste your Google OAuth **Client ID** and **Client Secret**
   (created in Google Cloud Console → APIs & Services → Credentials).
3. Add your app's redirect URL (Supabase gives you the exact callback URL to
   paste into Google Cloud Console).
4. Email/Password sign-in is enabled by default under
   **Authentication → Providers → Email**.

## 3. Configure Environment Variables

```bash
cp .env.example .env
# then fill in every value using what you copied in steps 1-2
```

## 4. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 5. Create the Database Tables

Since this is Phase 1, the simplest path is to auto-create all tables
directly from the SQLAlchemy models (Alembic migrations can be added
once the schema stabilizes):

```bash
python -c "from app.db.database import Base, engine; from app import models; Base.metadata.create_all(engine)"
```

## 6. Run the Server

```bash
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI —
every endpoint below can be tested directly from there.

## How Authentication Works

- **Email/Password:** Frontend calls `POST /api/v1/auth/signup` or
  `POST /api/v1/auth/login` directly. The backend talks to Supabase
  Auth and returns an `access_token`.
- **Google Sign-In:** Frontend calls Supabase's client-side method
  `supabase.auth.signInWithOAuth({ provider: 'google' })`, which
  redirects the user through Google and back with a Supabase session.
  The frontend then sends that session's `access_token` to
  `POST /api/v1/auth/google`, which verifies it and creates a matching
  profile row (patient or doctor) on first login.
- Every protected endpoint expects `Authorization: Bearer <access_token>`.

## Endpoints Implemented in Phase 1

| Method | Path                          | Access  |
|--------|-------------------------------|---------|
| POST   | /api/v1/auth/signup           | Public  |
| POST   | /api/v1/auth/login             | Public  |
| POST   | /api/v1/auth/google             | Public  |
| GET    | /api/v1/patients/me            | Patient |
| PUT    | /api/v1/patients/me            | Patient |
| GET    | /api/v1/doctors/me             | Doctor  |
| PUT    | /api/v1/doctors/me             | Doctor  |
| GET    | /api/v1/doctors                | Any authenticated user |
| POST   | /api/v1/appointments           | Patient |
| GET    | /api/v1/appointments/me        | Patient |
| GET    | /api/v1/appointments/today     | Doctor  |

## Next: Phase 2

Chat endpoint, LLM integration (LangGraph), conversation state, and
patient-context retrieval — building directly on the `conversations`
and `messages` tables already defined in Phase 1's models.
