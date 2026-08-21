<div align="center">

# ResearchIQ

### AI-Powered Research Paper Analysis Platform

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

Upload, analyse, search and compare scientific papers using AI.

[Live Demo](https://researchiq-omega.vercel.app) · [API Docs](https://researchiq.onrender.com/docs) · [Report Bug](https://github.com/alymkarim/researchiq/issues)

</div>

---

## What is this?

ResearchIQ lets you upload research papers (PDFs) and get structured analysis back in seconds. It extracts the key parts like objectives, methodology, findings, strengths and limitations so you don't have to read through 20+ pages yourself.

You can search across your whole collection, compare papers side by side, and optionally connect an LLM for deeper AI analysis.

## Why use it?

* Saves time when reviewing multiple papers
* Works without an API key (heuristic analysis is built in)
* Search across all your uploaded papers at once
* Compare papers on methodology, findings and conclusions
* Export analysis as PDF or DOCX
* Your papers stay on your infrastructure

---

## Features

### Core

* Upload single or multiple PDF research papers
* Automatic metadata extraction (title, authors, abstract)
* AI or heuristic paper analysis (summary, methodology, findings, strengths, limitations, keywords)
* Full text search with page aware results
* Side by side paper comparison
* Citation export (BibTeX, APA, MLA)
* Paper recommendations based on similarity
* In app PDF viewer with navigation and zoom
* User authentication with JWT

### New in the platform overhaul

* Chat with papers (conversational Q&A using RAG)
* Search external papers from Semantic Scholar and arXiv
* Visualizations: word clouds, keyword networks, methodology timelines
* Notes and annotations on papers
* Export analysis as PDF or DOCX
* Batch analyse multiple papers at once
* Quick, standard or deep analysis levels
* Multi model LLM support (OpenAI, Groq, Anthropic, Google, Ollama)
* FAISS based vector search with OpenAI embeddings
* Map analysis results back to specific PDF pages

---

## Live demo

**Frontend:** [https://researchiq-omega.vercel.app](https://researchiq-omega.vercel.app)

**Backend API:** [https://researchiq.onrender.com/docs](https://researchiq.onrender.com/docs)

---

## Tech stack

**Frontend:** React 18, TypeScript, Vite, React Router, Lucide Icons, PDF.js

**Backend:** FastAPI, SQLAlchemy, Pydantic, PyMuPDF, Scikit-learn, FAISS, SlowAPI, OpenAI SDK, ReportLab, python-docx

**Database:** SQLite (local), PostgreSQL via Supabase (production)

**Deployment:** Vercel (frontend), Render (backend), Supabase (database)

---

## How it works

`
┌─────────────────────────────────────────────────────┐
│                   FRONTEND                          │
│             React + TypeScript + Vite               │
│                                                     │
│  Upload · Analysis · Search · Compare · Chat        │
│  Export · Visualize · Notes · Discovery · Batch     │
└───────────────────────┬─────────────────────────────┘
                        │ REST API
                        ▼
┌─────────────────────────────────────────────────────┐
│                    BACKEND                          │
│                FastAPI + Python                     │
│                                                     │
│  PDF Processing (PyMuPDF)                           │
│  TF-IDF Search + Analysis (Scikit-learn)            │
│  Vector Search (FAISS)                              │
│  LLM Integration (OpenAI SDK)                       │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
           ▼                      ▼
    ┌─────────────┐    ┌──────────────────┐
    │ PostgreSQL  │    │  LLM Providers   │
    │ (Supabase)  │    │  OpenAI, Groq,   │
    │             │    │  Ollama, etc     │
    └─────────────┘    └──────────────────┘
`

---

## Getting started

### What you need

* Python 3.11 or newer
* Node.js 18 or newer

### Backend

`ash
cd backend
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
`

API runs at http://localhost:8000
Docs at http://localhost:8000/docs

### Frontend

`ash
cd frontend
npm install
cp .env.example .env
npm run dev
`

App runs at http://localhost:5173

---

## Environment variables

### Backend

`
DATABASE_URL=sqlite:///./researchiq.db
JWT_SECRET=your-random-secret
FRONTEND_ORIGIN=http://localhost:5173
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
`

Only DATABASE_URL and JWT_SECRET are required. The LLM settings are optional.

### Frontend

`
VITE_API_URL=http://localhost:8000
`

---

## LLM setup

ResearchIQ works without an LLM. If no API key is set, it uses a built in heuristic engine that pattern matches common phrases in academic papers.

To enable AI analysis, set the LLM environment variables. Any OpenAI compatible API works.

### Supported providers

| Provider | Base URL | Free? |
|----------|----------|-------|
| OpenAI | https://api.openai.com/v1 | No |
| Groq | https://api.groq.com/openai/v1 | Yes |
| Ollama | http://localhost:11434/v1 | Yes (local) |
| Anthropic | https://api.anthropic.com/v1 | No |

---

## API endpoints

| Method | Endpoint | What it does |
|--------|----------|--------------|
| GET | /api/documents | List uploaded papers |
| POST | /api/documents/upload | Upload PDF papers |
| DELETE | /api/documents/{id} | Delete a paper |
| POST | /api/analysis/{id} | Analyse a paper |
| POST | /api/search | Search papers |
| POST | /api/comparison | Compare papers |
| POST | /api/auth/register | Register |
| POST | /api/auth/login | Login |
| POST | /api/chat | Chat with a paper |
| GET | /api/export/analysis/{id}/pdf | Export as PDF |
| GET | /api/export/analysis/{id}/docx | Export as DOCX |
| GET | /api/discovery/search | Search external papers |
| POST | /api/batch/analyse | Batch analyse |
| GET | /api/summary/{id} | Multi level summary |
| GET | /api/visualizations/wordcloud/{id} | Word cloud |
| GET | /api/visualizations/keyword-network/{id} | Keyword network |
| GET | /api/visualizations/methodology-timeline/{id} | Method timeline |
| GET | /api/visualizations/citation-graph | Citation graph |
| GET | /api/highlights/{id} | Page highlights |
| POST | /api/collaboration/notes | Create note |
| GET | /api/collaboration/notes/{id} | Get notes |
| POST | /api/collaboration/annotations | Create annotation |
| GET | /api/collaboration/annotations/{id} | Get annotations |
| GET | /api/llm/providers | List LLM providers |
| GET | /api/recommendations/{id} | Paper recommendations |
| GET | /api/citations/{id} | Export citation |
| GET | /api/health | Health check |

---

## Testing

`ash
cd backend
pytest -v
`

---

## What's next

* OCR support for scanned PDFs
* Real time collaboration
* Paper collections and folders
* Interactive citation graph
* Custom analysis templates
* Multi language support
* Browser extension for importing papers
* Mobile design improvements

---

## Contributing

1. Fork the repo
2. Create a branch (git checkout -b feature/my-feature)
3. Make your changes
4. Push and open a PR

---

## License

MIT

---

## Built with

* [FastAPI](https://fastapi.tiangolo.com/)
* [React](https://react.dev/)
* [PyMuPDF](https://pymupdf.readthedocs.io/)
* [Scikit-learn](https://scikit-learn.org/)
* [FAISS](https://faiss.ai/)
* [Lucide](https://lucide.dev/)
