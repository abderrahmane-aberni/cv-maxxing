# Deploying CV-Maxxing (Render only)

Both pieces run on Render as two free web services from the same
`render.yaml`: the FastAPI backend (Python runtime) and the Streamlit
frontend (Docker runtime). Both deploy straight from this GitHub repo.
Steps marked **(you)** need your own account/login and can't be done for
you — everything else is already in the repo.

Originally the frontend was planned for Streamlit Community Cloud, but
that platform wraps every public app in an overlay showing the deployer's
GitHub avatar and name, with no option to disable it (confirmed by
Streamlit's own team — it's part of their hosting, not something app code
can touch). Running the same `frontend/Dockerfile` on Render instead
avoids that entirely, at the cost of a `.onrender.com` URL instead of a
`.streamlit.app` one.

## 1. Database: switch from SQLite to Postgres

Render's free web services have an ephemeral filesystem — a local SQLite
file gets wiped on every redeploy/restart. Use a free Postgres database
instead (same approach as the Ledger project):

1. **(you)** Create a free database at [neon.com](https://neon.com) (or
   Render's own free Postgres, if still offered on your account).
2. **(you)** Copy its connection string — looks like
   `postgresql://user:pass@host/dbname?sslmode=require`.
   You'll paste this into Render as `DATABASE_URL` in step 2.

## 2. Backend on Render

1. **(you)** Go to [render.com](https://render.com), sign in with GitHub.
2. **(you)** New → Blueprint → select the `cv-maxxing` repo. Render reads
   `render.yaml` and proposes two services — this step is about the
   `cv-maxxing-backend` one.
3. **(you)** Set these env vars on `cv-maxxing-backend` (left blank in the
   blueprint on purpose — they're secrets):
   - `GEMINI_API_KEY` — your key from aistudio.google.com
   - `DATABASE_URL` — the Postgres connection string from step 1
4. Deploy. Render gives you a URL like
   `https://cv-maxxing-backend-xxxx.onrender.com`. Visit
   `<that-url>/health` to confirm it's up (the free tier spins down when
   idle, so the first request after a quiet period takes ~30-60s to wake
   up — that's normal, not broken).

## 3. Frontend on Render

1. In the same Blueprint flow (or afterwards, as a separate deploy), set
   the `cv-maxxing-frontend` service's env var:
   - `BACKEND_URL` — the exact URL from step 2 (no trailing slash, no
     `/health` on the end), e.g. `https://cv-maxxing-backend-xxxx.onrender.com`
2. Deploy. Render gives you a second URL, e.g.
   `https://cv-maxxing-frontend-xxxx.onrender.com` — that's the public
   link to actually share. No avatar, no "created by" badge, no GitHub
   branding — it's just the app.

## Notes

- **Cost stays $0** as long as you're on Gemini's free tier and don't
  exceed Render's free-tier limits. The rate limiter in
  `backend/app/rate_limit.py` (5 requests/hour per visitor, 50/day total
  by default) exists specifically to keep a public link from quietly
  burning through Gemini's free-tier daily quota.
- Render's free tier sleeps on idle on **both** services now — the
  frontend's first load after a quiet period can take ~30-60s too, same
  as the backend.
- If `GEMINI_MODEL` ever starts failing with a "model not found" error,
  check [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)
  for the current cheapest Flash/Flash-Lite model name and update the env
  var on Render — no code change or redeploy needed, just restart.
