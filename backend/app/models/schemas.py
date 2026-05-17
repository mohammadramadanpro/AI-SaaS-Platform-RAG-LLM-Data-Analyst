"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel


# --- Auth ---
class UserCreate(BaseModel):
    email: str


class UserResponse(BaseModel):
    id: str
    email: str


# --- RAG ---
class RAGQueryRequest(BaseModel):
    question: str
    document_ids: list[str] | None = None  # None = search all user docs


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[str]


class DocumentResponse(BaseModel):
    id: str
    filename: str
    doc_type: str
    chunk_count: int


class URLUploadRequest(BaseModel):
    url: str


# --- Data Analyst ---
class AnalystQueryRequest(BaseModel):
    question: str
    dataset_id: str


class AnalystQueryResponse(BaseModel):
    answer: str
    chart_url: str | None = None
    error: str | None = None


class DatasetResponse(BaseModel):
    id: str
    filename: str
    row_count: int
    col_count: int
    columns: list[str]
