# TETRA021
# Finvestor
AI-Powered Cross-Document Financial Consistency Checker for Fundraising
FastAPI backend for cross-document financial consistency checking in fundraising. Upload pitch decks, financials, MIS, projections, and cap tables to get a deterministic 350–850 investor readiness score, source-linked inconsistencies, and a professional PDF report.
And meet PennyPal, your voice-powered AI assistant and chatbot.


# Features
Cross-Document Consistency: Automatically detects conflicting numbers, unsupported claims, and missing information across pitch deck, financials, MIS, projections, and cap table

Investor Readiness Score: Deterministic 350–850 score (not LLM-guessed) with category breakdown and stage benchmarks (Idea → Seed → Series A)

Source-Linked Findings: Every discrepancy cites exact document and page; no hallucinated numbers

RAG-Powered Extraction: Documents are chunked and indexed in ChromaDB for retrieval-augmented generation (extraction, cross-checking, and Q&A)

PDF Export: One-click download of investor-grade PDF report with score, discrepancies, and follow-up questions

Voice Agent (PennyPal): Ask questions via microphone; get retrieval-grounded answers with optional text-to-speech

100% Free-Tier Compatible: Works with free tiers of Groq, LlamaParse, Deepgram, and Supabase (no credit card required)

# Quick Start
1. Clone the Repository
bash
git clone https://github.com/yourusername/finvestor.git
cd finvestor
2. Set Up Environment Variables
bash
cp .env.example .env
Edit .env and fill in your API keys:

bash
# Database (optional: defaults to SQLite for local dev)
DATABASE_URL=sqlite:///./finvestor.db

# LLM & Extraction
GROQ_API_KEY=gsk_...                 # console.groq.com (free tier)
LLAMA_PARSE_API_KEY=...              # cloud.llamaindex.ai (1000 pages/month free)

# Voice Agent (optional)
DEEPGRAM_API_KEY=...                 # console.deepgram.com ($200 free credit)
ELEVENLABS_API_KEY=...               # elevenlabs.io (10K chars/month free)

# CORS
FRONTEND_ORIGIN=http://localhost:5500
3. Install Dependencies
bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
4. Run the Server
bash
uvicorn app.main:app --reload --port 8000
API docs are now available at: http://localhost:8000/docs


# API Flow
Step	Endpoint	Description
1	POST /auth/signup or POST /auth/login	Get bearer token
2	POST /analysis/runs	Create analysis run (company name)
3	POST /documents/upload	Upload document (multipart: run_id, doc_type, file)
4	POST /analysis/runs/{run_id}/execute	Run full pipeline (parse → extract → cross-check → score)
5	GET /report/runs/{run_id}/pdf	Download formatted PDF report
6	POST /voice/query (optional)	Send audio, get transcript + RAG answer + TTS audio
Example: Upload & Analyze
bash
# 1. Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"securepassword"}'

# 2. Create run
curl -X POST "http://localhost:8000/analysis/runs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Acme Startup"}'

# 3. Upload pitch deck
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "run_id=RUN_ID" \
  -F "doc_type=pitch" \
  -F "file=@pitch_deck.pdf"

# 4. Execute analysis
curl -X POST "http://localhost:8000/analysis/runs/RUN_ID/execute" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 5. Download PDF
curl -X GET "http://localhost:8000/report/runs/RUN_ID/pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output fundraising-report.pdf

# Architecture

┌─────────────────────────────────────────────────────────────┐
│                    Frontend (finvestor_app.html)            │
│  - Upload UI, Score Dashboard, PDF Download, Voice Agent    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  /auth/* → JWT authentication                               │
│  /analysis/* → Run orchestration                            │
│  /documents/* → Upload & parsing (LlamaParse)               │
│  /voice/* → Deepgram STT + RAG + ElevenLabs TTS             │
│  /report/* → PDF generation (WeasyPrint + Jinja2)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  PostgreSQL/SQLite (Supabase or local) → Runs, Users, Docs  │
│  ChromaDB (local) → Vector store for RAG                    │
│  Groq API → LLM for extraction & discrepancy explanations   │
└─────────────────────────────────────────────────────────────┘
RAG Pipeline
Document Parsing: LlamaParse converts PDF/PPTX/XLSX → text + tables with layout

Chunking & Indexing: Documents are chunked and stored in per-run ChromaDB collections with metadata (doc_type, page, section)

Retrieval-Augmented Extraction: For each metric (revenue, margin, customers, etc.), only relevant chunks are retrieved and sent to LLM (keeps prompts small, scales to long docs)

Cross-Document Checking: Retrieves matching chunks from all document types simultaneously; discrepancy explanations cite actual source text

Voice/Chat Agent: Retrieves across entire run for open-ended Q&A; answers only from retrieved context 


# Scoring System
The 350–850 investor readiness score is computed deterministically in app/scoring.py (not guessed by LLM):

Category	Weight	What It Measures
Financial Credibility	25%	Consistency of revenue, margins, cash position across documents
Pitch Deck Quality	20%	Clarity, traction evidence, market sizing
Due Diligence Preparation	20%	Data room readiness, completeness of documents
Cap Table Readiness	15%	Clean ownership structure, ESOP, option pool
Team & Governance	10%	Advisory board, key hires, governance
Market Opportunity	10%	TAM, growth assumptions, competitive landscape
Scoring Logic:

Base score: 500

Deduct 15 points per discrepancy

Add bonus up to +100 for completeness

Clamp to 350–850 range

Benchmarks:

350–500: Idea Stage

500–650: Seed Ready

650–850: Series A Ready

# Voice Agent
The /voice/query endpoint accepts audio and returns:

Transcript (Deepgram STT)

Retrieval-grounded answer (RAG pipeline)

Spoken audio (ElevenLabs TTS, Deepgram)

Free Tier Limits:

Deepgram: $200 credit 

ElevenLabs: 10K characters/month 

# Project Structure
text
finvestor/
├── README.md
├── finvestor_app.html           # Static frontend demo
├── requirements.txt
├── .env.example
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── auth.py                  # JWT authentication
│   ├── config.py                # Configuration management
│   ├── database.py              # Database connection
│   ├── rag.py                   # RAG pipeline (ChromaDB)
│   ├── scoring.py               # 350-850 scoring logic
│   ├── validation.py            # Plausibility checks (margins, counts)
│   ├── voice.py                 # Deepgram + ElevenLabs integration
│   ├── report.py                # PDF generation (WeasyPrint)
│   ├── models.py                # SQLAlchemy/Pydantic models
│   └── utils.py                 # Helper functions
├── data/
│   ├── uploads/                 # Temporary uploaded files
│   └── vectorstore/             # ChromaDB persistence
└── templates/
    └── pdf_report.html          # Jinja2 PDF template
    
# Tech Stack
Component	Technology	Free Tier
Backend	FastAPI (Python 3.11+)	Unlimited
Database	PostgreSQL (Supabase) / SQLite	500MB free
Vector Store	ChromaDB (local)	Unlimited
LLM	Groq (Llama 3.1 8B)	500K tokens/day, 14.4K requests/day
Document Parsing	LlamaParse	1000 pages/month
Voice STT	Deepgram Nova-2	$200 credit (~400 hours)
Voice TTS	ElevenLabs	10K chars/month (or $5/month Starter)
PDF Generation	WeasyPrint + Jinja2	Unlimited
Deployment	Railway (backend) + Vercel (frontend)	Free tiers

# Deployment
Backend (Railway)
bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
cd finvestor
railway init
railway up

# Set environment variables in Railway dashboard
DATABASE_URL=postgres://...
GROQ_API_KEY=gsk_...
LLAMA_PARSE_API_KEY=...
DEEPGRAM_API_KEY=...
FRONTEND_ORIGIN=https://finvestor-frontend.vercel.app
Frontend (Vercel)
bash
# Install Vercel CLI
npm i -g vercel

# Deploy static HTML
cd finvestor
vercel --prod

# Update backend .env
FRONTEND_ORIGIN=https://finvestor-frontend.vercel.app
Update BACKEND_URL in finvestor_app.html to your Railway URL.


Production: https://your-backend.up.railway.app/docs
