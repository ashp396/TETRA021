
## Setup

The easiest path is the root level `docker-compose.yml` one directory up,
which builds this backend, the frontend, and Postgres together with one
`docker compose up --build`. The steps below run just this backend on
its own, useful while developing against it.

1. Copy `.env.example` to `.env` and fill in `GROQ_API_KEY` (free at
   console.groq.com). Everything else works without extra keys.
2. `docker compose up --build` starts Postgres and the API together, or
   run locally:
   ```
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
3. API docs are at `http://localhost:8000/docs` once it is running.

## Notes on first run

- Postgres tables, the full text search column, and its index are
  created automatically on startup; for production use, swap that for a
  real Alembic migration flow.
- `faster-whisper` downloads its `base` model on first voice
  transcription (a few hundred MB, cached after that, free, no key).
