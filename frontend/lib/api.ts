const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// --- RAG ---

export interface DocumentInfo {
  id: string;
  filename: string;
  doc_type: string;
  chunk_count: number;
}

export interface RAGResponse {
  answer: string;
  sources: string[];
}

export async function uploadPDF(file: File): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("file", file);
  return request<DocumentInfo>("/api/rag/upload/pdf", {
    method: "POST",
    body: form,
  });
}

export async function uploadURL(url: string): Promise<DocumentInfo> {
  return request<DocumentInfo>("/api/rag/upload/url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  return request<DocumentInfo[]>("/api/rag/documents");
}

export async function queryRAG(
  question: string,
  documentIds?: string[]
): Promise<RAGResponse> {
  return request<RAGResponse>("/api/rag/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, document_ids: documentIds }),
  });
}

// --- Data Analyst ---

export interface DatasetInfo {
  id: string;
  filename: string;
  row_count: number;
  col_count: number;
  columns: string[];
}

export interface AnalystResponse {
  answer: string;
  chart_url: string | null;
  error: string | null;
}

export async function uploadDataset(file: File): Promise<DatasetInfo> {
  const form = new FormData();
  form.append("file", file);
  return request<DatasetInfo>("/api/analyst/upload", {
    method: "POST",
    body: form,
  });
}

export async function listDatasets(): Promise<DatasetInfo[]> {
  return request<DatasetInfo[]>("/api/analyst/datasets");
}

export async function queryAnalyst(
  question: string,
  datasetId: string
): Promise<AnalystResponse> {
  return request<AnalystResponse>("/api/analyst/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, dataset_id: datasetId }),
  });
}

export function chartURL(path: string): string {
  return `${API_BASE}${path}`;
}
