# ResearchIQ

ResearchIQ is a full-stack research paper analysis platform that helps users upload, analyse, search and compare scientific papers through an intuitive web interface.

Built with React, FastAPI and PostgreSQL, the platform combines PDF processing, natural language processing and AI-assisted analysis to make exploring academic literature faster and more interactive.

## Features

- Upload one or multiple PDF research papers
- Automatic extraction of paper metadata
- AI-assisted paper diagnostics
- Executive summaries
- Methodology, dataset and findings extraction
- Strengths and limitations analysis
- Keyword extraction
- Full-text TF-IDF semantic search
- Page-aware search results
- Cross-paper comparison
- User authentication (JWT)
- Citation extraction
- Paper recommendations
- Rate limiting on auth and upload endpoints
- REST API with automatic OpenAPI documentation
- Health monitoring endpoint
- Production deployment

## Demo

**Live Application**

https://researchiq-omega.vercel.app

**Backend API**

https://your-render-backend.onrender.com/docs

## Screenshots

> Add screenshots or GIFs here.

### Upload papers

![Upload](docs/images/upload.png)

### Paper analysis

![Analysis](docs/images/analysis.png)

### Search

![Search](docs/images/search.png)

### Comparison

![Comparison](docs/images/comparison.png)

---

# Tech Stack

### Frontend

- React
- TypeScript
- Vite
- CSS

### Backend

- FastAPI
- SQLAlchemy
- Pydantic
- PyMuPDF
- Scikit-learn
- SlowAPI (rate limiting)

### Database

- SQLite (local development)
- PostgreSQL (Supabase production)

### Deployment

- Vercel
- Render
- Supabase

---

# Architecture

```
                React + TypeScript
                        │
                        ▼
                 FastAPI REST API
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
 PostgreSQL                    PDF Processing
 (Supabase)                     (PyMuPDF)
                                        │
                                        ▼
                          TF-IDF Search + Analysis
```

---

# Project Structure

```
researchiq/
│
├── backend/
│   ├── app/
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   └── package.json
│
└── README.md
```

---

# Running Locally

## Backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

uvicorn app.main:app --reload
```

Backend runs at

```
http://localhost:8000
```

Swagger documentation

```
http://localhost:8000/docs
```

---

## Frontend

```bash
cd frontend

npm install

copy .env.example .env

npm run dev
```

Frontend runs at

```
http://localhost:5173
```

---

# Environment Variables

Backend

```env
DATABASE_URL=

LLM_API_KEY=

LLM_BASE_URL=

LLM_MODEL=

JWT_SECRET=

FRONTEND_ORIGIN=http://localhost:5173
```

Frontend

```env
VITE_API_URL=http://localhost:8000
```

---

# AI Analysis

ResearchIQ works even without an LLM.

When no LLM credentials are supplied, the application automatically falls back to a lightweight heuristic analysis engine that extracts:

- Objective
- Methodology
- Dataset
- Findings
- Strengths
- Limitations
- Keywords

When an OpenAI-compatible endpoint is configured, ResearchIQ performs richer AI-assisted analysis while keeping the same API.

---

# API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/documents` | List uploaded papers |
| POST | `/api/documents/upload` | Upload PDF papers |
| DELETE | `/api/documents/{id}` | Delete a paper |
| POST | `/api/analysis/{id}` | Analyse a paper |
| POST | `/api/search` | Search uploaded papers |
| POST | `/api/comparison` | Compare selected papers |
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/health` | Health check |

---

# Testing

Run all backend tests

```bash
cd backend

pytest -v
```

---

# Future Improvements

- Vector embedding search
- OCR support for scanned PDFs
- Citation graph visualisation
- Research collections
- Export reports

---

# License

MIT License
