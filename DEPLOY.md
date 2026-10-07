# Deploying Resolve (Render + Streamlit Community Cloud)

Two pieces, two free services: the FastAPI backend on Render, the
Streamlit frontend on Streamlit Community Cloud. Both deploy straight
from this GitHub repo. Steps marked **(you)** need your own account/login
and can't be done for you — everything else is already in the repo.

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
2. **(you)** New → Blueprint → select the `resolve` repo. Render reads
   `render.yaml` from the repo root and proposes the `resolve-backend`
   service.
3. **(you)** Before deploying, set these environment variables in the
   Render dashboard (the blueprint leaves them blank on purpose — they're
   secrets):
   - `GEMINI_API_KEY` — your key from aistudio.google.com
   - `DATABASE_URL` — the Postgres connection string from step 1
4. Deploy. Render gives you a URL like
   `https://resolve-backend-xxxx.onrender.com`. Visit
   `<that-url>/health` to confirm it's up (the free tier spins down when
   idle, so the first request after a quiet period takes ~30-60s to wake
   up — that's normal, not broken).

## 3. Frontend on Streamlit Community Cloud

1. **(you)** Go to
   [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
2. **(you)** New app → pick the `resolve` repo, branch `main`, main file
   path `frontend/streamlit_app.py`.
3. **(you)** In the app's "Advanced settings" → Secrets, add:
   ```toml
   BACKEND_URL = "https://resolve-backend-xxxx.onrender.com"
   ```
   (the exact URL Render gave you in step 2).
4. Deploy. Streamlit gives you a public `*.streamlit.app` URL — that's
   the link to actually share.

## Notes

- **Cost stays $0** as long as you're on Gemini's free tier and don't
  exceed Render/Streamlit's free-tier limits. The rate limiter in
  `backend/app/rate_limit.py` (5 requests/hour per visitor, 50/day total
  by default) exists specifically to keep a public link from quietly
  burning through Gemini's free-tier daily quota.
- Render's free tier sleeps on idle — fine for a portfolio demo, not for
  anything latency-sensitive.
- If `GEMINI_MODEL` ever starts failing with a "model not found" error,
  check [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)
  for the current cheapest Flash/Flash-Lite model name and update the env
  var on Render — no code or redeploy of the frontend needed.
