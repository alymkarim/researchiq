# ResearchIQ Frontend

A modern retro-cartoon laboratory interface for the ResearchIQ research-paper analysis API.

## Local setup

```bash
npm install
cp .env.example .env
npm run dev
```

The default backend is:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Expected backend endpoints

```text
GET    /api/documents
POST   /api/documents/upload
DELETE /api/documents/{id}
POST   /api/analysis/{id}
POST   /api/search
POST   /api/comparison
```

Search request:

```json
{
  "query": "What methods were used?",
  "document_ids": [1, 2]
}
```

Comparison request:

```json
{
  "document_ids": [1, 2]
}
```

If your backend uses different request field names or paths, edit only `src/api.ts`.

## Deploy on Vercel

Set the project root to this frontend folder and add:

```env
VITE_API_URL=https://your-render-backend.onrender.com
```
