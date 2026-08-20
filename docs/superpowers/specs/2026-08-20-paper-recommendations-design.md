# Paper Recommendations Feature

## Overview

Add paper recommendations based on TF-IDF similarity between uploaded papers. This feature will allow users to discover related papers in their collection based on content similarity.

## Architecture

### Backend
- **Service**: `backend/app/services/recommendation_service.py` - TF-IDF similarity computation
- **Router**: `backend/app/routers/recommendations.py` - API endpoint for recommendations
- **Registration**: Add router to `backend/app/main.py`

### Frontend
- **Component**: `frontend/src/components/Recommendations.tsx` - UI for displaying recommendations
- **Integration**: Add to `frontend/src/components/AnalysisPanel.tsx`
- **API**: Add `getRecommendations` to `frontend/src/api.ts`
- **Styles**: Add recommendation styles to `frontend/src/styles.css`

## Data Flow

1. User selects a document in AnalysisPanel
2. Frontend calls `GET /api/recommendations/{document_id}?limit=3`
3. Backend retrieves target document and all other documents
4. Service computes TF-IDF vectors and cosine similarity
5. Returns top recommendations with similarity scores
6. Frontend displays recommendations as clickable cards

## Implementation Details

### Backend Service
- Use sklearn's TfidfVectorizer with English stop words
- Limit to 3000 features for efficiency
- Compute cosine similarity between target document and all others
- Filter results with similarity > 0.05 threshold
- Return document_id, title, and similarity score

### API Endpoint
- GET `/api/recommendations/{document_id}`
- Optional query parameter: `limit` (default: 3)
- Returns 404 if document not found
- Returns empty array if no recommendations found

### Frontend Component
- Shows related papers as small cards
- Display similarity score as percentage
- Click to view/analyse the recommended paper
- Empty state if no recommendations
- Uses CSS variables for styling

## Testing

- Backend: pytest tests for recommendation service
- Frontend: Build verification with `npm run build`
- Integration: Test API endpoint manually

## Success Criteria

1. Recommendations endpoint returns relevant papers
2. Frontend displays recommendations correctly
3. User can click to view recommended papers
4. Empty state shows when no recommendations available
5. All tests pass
6. Build succeeds