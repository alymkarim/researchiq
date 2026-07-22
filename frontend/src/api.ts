import type {
  Analysis,
  ComparisonResult,
  DocumentItem,
  HealthStatus,
  SearchResult,
} from "./types";


const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");


export class ApiError extends Error {
  status: number;

  constructor(message: string, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}


async function extractErrorMessage(
  response: Response,
): Promise<string> {
  const fallback = `Request failed with status ${response.status}.`;

  try {
    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
      const data: unknown = await response.json();

      if (
        data &&
        typeof data === "object" &&
        "detail" in data
      ) {
        const detail = (data as { detail?: unknown }).detail;

        if (typeof detail === "string") {
          return detail;
        }

        if (Array.isArray(detail)) {
          return detail
            .map((item) => {
              if (
                item &&
                typeof item === "object" &&
                "msg" in item
              ) {
                return String(
                  (item as { msg: unknown }).msg,
                );
              }

              return String(item);
            })
            .join(" ");
        }
      }

      if (
        data &&
        typeof data === "object" &&
        "message" in data
      ) {
        return String(
          (data as { message: unknown }).message,
        );
      }

      return JSON.stringify(data);
    }

    const text = await response.text();

    return text || fallback;
  } catch {
    return fallback;
  }
}


async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(
      `${API_URL}${path}`,
      options,
    );
  } catch {
    throw new ApiError(
      "The ResearchIQ backend could not be reached. "
        + "The Render service may be waking up. "
        + "Wait about 30 seconds and try again.",
    );
  }

  if (!response.ok) {
    const message = await extractErrorMessage(response);

    throw new ApiError(
      message,
      response.status,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  try {
    return await response.json() as T;
  } catch {
    throw new ApiError(
      "The server returned an invalid response.",
      response.status,
    );
  }
}


export async function getHealth(): Promise<HealthStatus> {
  return apiFetch<HealthStatus>("/api/health");
}


export async function getDocuments(): Promise<DocumentItem[]> {
  return apiFetch<DocumentItem[]>("/api/documents");
}


export async function getDocument(
  id: number,
): Promise<DocumentItem> {
  return apiFetch<DocumentItem>(
    `/api/documents/${id}`,
  );
}


export async function uploadDocuments(
  files: File[],
): Promise<DocumentItem[]> {
  if (files.length === 0) {
    throw new ApiError(
      "Please select at least one PDF.",
      400,
    );
  }

  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  return apiFetch<DocumentItem[]>(
    "/api/documents/upload",
    {
      method: "POST",
      body: formData,
    },
  );
}


export async function deleteDocument(
  id: number,
): Promise<void> {
  await apiFetch<void>(
    `/api/documents/${id}`,
    {
      method: "DELETE",
    },
  );
}


export async function analyseDocument(
  id: number,
): Promise<Analysis> {
  return apiFetch<Analysis>(
    `/api/analysis/${id}`,
    {
      method: "POST",
    },
  );
}


export async function searchPapers(
  query: string,
  documentIds: number[],
): Promise<SearchResult[]> {
  const payload = {
    query,
    document_ids: documentIds,
    limit: 5,
  };

  const result = await apiFetch<
    SearchResult[] | { results: SearchResult[] }
  >(
    "/api/search",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  if (Array.isArray(result)) {
    return result;
  }

  return result.results || [];
}


export async function comparePapers(
  documentIds: number[],
): Promise<ComparisonResult> {
  if (documentIds.length < 2) {
    throw new ApiError(
      "Select at least two papers to compare.",
      400,
    );
  }

  return apiFetch<ComparisonResult>(
    "/api/comparison",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        document_ids: documentIds,
      }),
    },
  );
}


export { API_URL };