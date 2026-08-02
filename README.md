# Finvestor

An AI powered cross document fundraising readiness checker for Indian
startups: upload a pitch deck, financial statements, MIS, projections and
cap table, and get a 350-850 Investor Readiness Score across 7 categories,
a sourced discrepancy report, investor style follow up questions, version
tracking, co founder access, and an exportable PDF, plus PennyPal, a voice
and chat assistant grounded in your own documents.

```
finvestor-repo/
├── docker-compose.yml   runs everything together: db, backend, frontend
├── backend/             FastAPI, Python 3.13, Postgres only (no separate vector store)
└── frontend/            Next.js 14, compiled production build
```

## Run the whole thing with one command

```
cp backend/.env.example backend/.env      # then paste in your free GROQ_API_KEY
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

This builds the backend on Python 3.13 and the frontend as a compiled
Next.js production build (`npm run build` + `npm start`, not the dev
server), then starts Postgres, the API, and the web app together.

## Running without Docker

Backend (needs Python 3.13 and a local or remote Postgres instance):
```
cd backend
cp .env.example .env
python3.13 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend, compiled build:
```
cd frontend
cp .env.local.example .env.local
npm install
npm run build
npm start
```
(or `npm run dev` while you're actively changing frontend code)


## Where each requested feature lives

| Feature | Where |
|---|---|
| Investor Readiness Score, 350-850, 7 categories | `backend/app/scoring.py`, `ScoreCard.tsx` |
| Stage based benchmarks | `scoring.py: STAGE_BENCHMARKS`, `/api/analysis/benchmarks` |
| Cross document retrieval driven verification | `backend/app/search_index.py` (Postgres full text search) feeding `scoring.py` |
| Discrepancy classification (missing / unresolved / verified) | `scoring.py` prompt rules, `DiscrepancyCard.tsx` |
| Regulatory & disclosure hygiene, SEBI aware, not a compliance audit | `scoring.py: REGULATORY_DISCLAIMER`, shown on the score page and in the PDF |
| Follow up question generation | `scoring.py`, Follow Ups tab |
| Voice first PennyPal | `backend/app/voice.py` (faster-whisper STT, edge-tts/ElevenLabs TTS), `PennyPal.tsx` |
| Document version tracking | `backend/app/routers/versions.py`, Versions tab |
| Co founders working as a team (persistent, not live) | `backend/app/routers/workspaces.py`, `TeamPanel.tsx` |
| Comments and task assignment on each discrepancy | `backend/app/routers/collab.py`, `DiscrepancyCard.tsx` |
| Exportable report | `backend/app/report.py` (PDF), Export Report tab |
| Auth, dark mode, profile | `backend/app/routers/auth.py`, `login/signup` pages, theme toggle in dashboard |

## On "SEBI guidelines"

SEBI's own rulebook (ICDR, LODR, PIT regulations) mainly governs listed
companies, IPOs, and SEBI registered Alternative Investment Funds. A
private seed or Series A round by an unlisted startup is chiefly governed
by the Companies Act, 2013 instead — in particular Section 42 on private
placement. Finvestor's "Regulatory & Disclosure Hygiene" category checks
for the paperwork and disclosure habits that SEBI registered AIFs
commonly expect from the startups they fund (an offer letter or board
resolution for the round, valuation support, related party transactions
flagged rather than buried). It does not perform a legal or regulatory
compliance review, and nothing it produces is legal advice — a company
secretary or securities lawyer should sign off on actual compliance.

## few limitations for some devices

- Postgres tables are created with `create_all` on startup for
  simplicity; before production use, switch to Alembic migrations.
- Full text search over English keywords is simpler to run than a vector
  database, but it is a keyword and phrase match rather than a semantic
  one — a query needs to share vocabulary with the documents to find the
  right chunk. Fundraising terms (revenue, cap table, runway, valuation)
  reliably do; very indirect phrasing may not.
- Team access is persistent, not real time: a co founder needs to
  refresh or reopen the page to see a teammate's latest comment, there is
  no live sync.
- `faster-whisper` runs on CPU and downloads a small model on first use;
  fine for a prototype, consider a hosted STT API if you scale up usage.
- No file storage service is wired in; uploaded documents are parsed to
  text and only the text is kept in Postgres, not the original files.
- I built and syntax checked this without a live Python 3.13 runtime or
  internet access — see the compatibility note above before you assume
  first boot will be silent.
