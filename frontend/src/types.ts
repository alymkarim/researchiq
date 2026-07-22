export interface Analysis {
  id?: number;
  summary?: string | null;
  keywords?: string[] | string | null;
  strengths?: string[] | string | null;
  limitations?: string[] | string | null;
  methodology?: string | null;
  findings?: string | null;
  [key: string]: unknown;
}

export interface DocumentItem {
  id: number;
  filename: string;
  title: string;
  authors?: string | null;
  abstract?: string | null;
  created_at?: string;
  analysis?: Analysis | null;
}

export interface SearchResult {
  document_id?: number;
  document_title?: string;
  filename?: string;
  page?: number;
  score?: number;
  text?: string;
  snippet?: string;
}

export interface ComparisonResult {
  summary?: string;
  similarities?: string[] | string;
  differences?: string[] | string;
  methodology?: string;
  findings?: string;
  limitations?: string;
  [key: string]: unknown;
}
