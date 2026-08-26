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
  snippet?: string;
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
  keywords?: string | string[] | null;
  shared_keywords?: string[];
  papers?: unknown[];
  similarities?: string[];
  [key: string]: unknown;
}

export interface HealthStatus {
  status: "healthy" | "degraded";
  api: string;
  database: string;
}


export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}


export interface DiscoveredPaper {
  title: string;
  authors: string;
  abstract?: string;
  year?: number;
  url: string;
  pdf_url?: string;
  doi?: string;
  arxiv_id?: string;
  citation_count?: number;
  source: string;
}


export interface Note {
  id: number;
  document_id: number;
  content: string;
  page_number?: number | null;
  created_at: string;
  updated_at: string;
}


export interface Annotation {
  id: number;
  document_id: number;
  page_number: number;
  highlight_text: string;
  comment?: string | null;
  color: string;
  created_at: string;
}


export interface WordCloudItem {
  text: string;
  value: number;
  size: number;
}


export interface NetworkNode {
  id: string;
  label: string;
  size: number;
}


export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
}


export interface TimelineStep {
  step: number;
  description: string;
}
