export interface Analysis {
  id: number;
  document_id: number;
  summary?: string | null;
  objective?: string | null;
  methodology?: string | null;
  dataset?: string | null;
  findings?: string | null;
  strengths?: string | null;
  limitations?: string | null;
  keywords?: string | null;
  analysis_mode?: "llm" | "heuristic" | string | null;
}

export interface DocumentItem {
  id: number;
  filename: string;
  title?: string | null;
  authors?: string | null;
  abstract?: string | null;
  created_at?: string | null;
  analysis?: Analysis | null;
}

export interface SearchResult {
  document_id: number;
  document_title: string;
  filename: string;
  page?: number | null;
  text: string;
  score: number;
}

export interface ComparisonResult {
  documents?: DocumentItem[];
  objective?: string | null;
  methodology?: string | null;
  dataset?: string | null;
  findings?: string | null;
  strengths?: string | null;
  limitations?: string | null;
  [key: string]: unknown;
}

export interface HealthStatus {
  status: "healthy" | "degraded";
  api: string;
  database: string;
}
