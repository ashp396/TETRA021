# Finvestor backend

FastAPI service that reads a startup's fundraising documents (pitch deck,
financial statements, MIS, projections, cap table), cross checks them
against each other with a retrieval driven pipeline, and produces an
Investor Readiness Score, a sourced discrepancy report, follow up
questions, and an exportable PDF.

## What changed from the first version

- **One database, not two.** The earlier version used Postgres for
  everything except retrieval, which went through a separate ChromaDB
  vector store with a local embedding model. This version drops Chroma
  entirely: document chunks live in a `document_chunks` table in the
  same Postgres database, searched with native full text search
  (`tsvector` / `ts_rank`, see `app/search_index.py`). Simpler to run,
  one less service to install, no model download for embeddings.
- **Regulatory hygiene checks, honestly scoped.** A seventh scoring
  category, "Regulatory & Disclosure Hygiene," checks documents for
  ordinary Indian private placement paperwork (offer letter, valuation
  support, related party disclosure) that SEBI registered AIFs commonly
  expect from the startups they fund. This is disclosure hygiene, not a
  compliance audit: SEBI's own rulebook (ICDR, LODR, PIT regulations)
  mainly governs listed companies, IPOs, and SEBI registered funds; a
  private round is chiefly governed by the Companies Act, 2013, in
  particular the private placement limits in Section 42. Every score and
  report carries this disclaimer, and PennyPal repeats it if asked about
  compliance directly. Nothing here is legal advice.
- **Co founder access, not live collaboration.** Workspaces support
  members now (`app/routers/workspaces.py`): the owner invites a co
  founder by email, and that co founder gets standing access to the same
  documents, score, discrepancies, and comment threads whenever they log
  in. It behaves like a shared drive folder, not a live multiplayer
  session, so the earlier websocket broadcaster has been removed.

## What is real here

- Runs on Python 3.13, Postgres via SQLAlchemy 2.0 with the `psycopg`
  (v3) driver — users, workspaces, workspace members, documents, document
  versions, document chunks, analysis results, discrepancies, comments,
  tasks, chat history.
- Auth: signup/login with bcrypt password hashing and JWT bearer tokens.
- Retrieval: documents are parsed (pdf, docx, pptx, xlsx, csv, txt),
  chunked, and searched with Postgres full text search. Scoring and chat
  both retrieve the most relevant chunks before asking the model
  anything, so answers are grounded and cite which document they came
  from.
- LLM: Groq (free tier available), used only after retrieval, never
  given raw unretrieved documents to hallucinate over.
- Voice: speech to text runs locally with faster-whisper (free, no key).
  Text to speech defaults to Microsoft edge-tts (free, no key); set
  `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` in `.env` to use
  ElevenLabs instead.
- Team access: invite a co founder by email once they have a Finvestor
  account; they see the same workspace on their own login, persistently.
- Reports: a one page PDF built with reportlab, no external binary
  dependencies, including the regulatory disclaimer.

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
