import type {
  Analysis,
  ComparisonResult,
  DocumentItem,
  SearchResult,
} from "./types";

const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, options);

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const data = await response.json();
      message = data.detail || data.message || JSON.stringify(data);
    } catch {
      const text = await response.text();
      if (text) message = text;
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function getDocuments(): Promise<DocumentItem[]> {
  return apiFetch<DocumentItem[]>("/api/documents");
}

export async function uploadDocuments(
  files: File[],
): Promise<DocumentItem[]> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  return apiFetch<DocumentItem[]>("/api/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export async function deleteDocument(id: number): Promise<void> {
  await apiFetch<void>(`/api/documents/${id}`, {
    method: "DELETE",
  });
}

export async function analyseDocument(id: number): Promise<Analysis> {
  return apiFetch<Analysis>(`/api/analysis/${id}`, {
    method: "POST",
  });
}

export async function searchPapers(
  query: string,
  documentIds: number[],
): Promise<SearchResult[]> {
  const payload = {
    query,
    document_ids: documentIds,
  };

  const result = await apiFetch<SearchResult[] | { results: SearchResult[] }>(
    "/api/search",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );

  return Array.isArray(result) ? result : result.results || [];
}

export async function comparePapers(
  documentIds: number[],
): Promise<ComparisonResult> {
  return apiFetch<ComparisonResult>("/api/comparison", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_ids: documentIds }),
  });
}

export { API_URL };
