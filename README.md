# ResearchIQ

Full-stack scientific literature analysis and comparison platform.

## Stack
- React + TypeScript + Vite
- FastAPI
- SQLAlchemy
- SQLite locally; PostgreSQL/Supabase via DATABASE_URL
- PyMuPDF
- TF-IDF retrieval
- Optional OpenAI-compatible LLM API

## Run backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

## Run frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend: http://localhost:5173  
Backend docs: http://localhost:8000/docs

## Optional LLM

```env
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
```

Without an API key, the app uses a lightweight heuristic analyser so the MVP still runs.

## Deploy
- Frontend: Vercel
- Backend: Render
- Database: Supabase PostgreSQL
