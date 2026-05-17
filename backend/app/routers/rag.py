"""RAG chatbot endpoints — upload documents, ask questions."""

import json
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import Document, get_db, generate_id
from ..models.schemas import (
    DocumentResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    URLUploadRequest,
)
from ..services import chunker, document_parser, llm
from ..services.vector_store import vector_store

router = APIRouter(prefix="/api/rag", tags=["RAG"])

RAG_SYSTEM_PROMPT = """You are a helpful assistant. Answer questions ONLY based on the provided context.
If the answer is not in the context, say "I don't have enough information to answer this."
Do not make up information. Be concise and accurate."""


@router.post("/upload/pdf", response_model=DocumentResponse)
async def upload_pdf(
    file: UploadFile,
    user_id: str = "demo_user",
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    content = await file.read()
    if len(content) > settings.MAX_PDF_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File too large (max {settings.MAX_PDF_SIZE_MB}MB)")

    doc_id = generate_id()
    doc_dir = settings.DATA_DIR / "users" / user_id / "documents"
    doc_dir.mkdir(parents=True, exist_ok=True)
    file_path = doc_dir / f"{doc_id}.pdf"
    file_path.write_bytes(content)

    text = document_parser.parse_pdf(str(file_path))
    if not text.strip():
        file_path.unlink()
        raise HTTPException(400, "Could not extract text from PDF")

    chunks = chunker.chunk_text(text)
    chunk_count = vector_store.index_chunks(user_id, doc_id, chunks)

    doc = Document(
        id=doc_id,
        user_id=user_id,
        filename=file.filename,
        doc_type="pdf",
        source=str(file_path),
        chunk_count=chunk_count,
    )
    db.add(doc)
    await db.commit()

    return DocumentResponse(
        id=doc_id, filename=file.filename, doc_type="pdf", chunk_count=chunk_count
    )


@router.post("/upload/url", response_model=DocumentResponse)
async def upload_url(
    req: URLUploadRequest,
    user_id: str = "demo_user",
    db: AsyncSession = Depends(get_db),
):
    try:
        text = document_parser.parse_url(req.url)
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch URL: {e}")

    if not text.strip():
        raise HTTPException(400, "No text content found at URL")

    doc_id = generate_id()
    chunks = chunker.chunk_text(text)
    chunk_count = vector_store.index_chunks(user_id, doc_id, chunks)

    doc = Document(
        id=doc_id,
        user_id=user_id,
        filename=req.url,
        doc_type="url",
        source=req.url,
        chunk_count=chunk_count,
    )
    db.add(doc)
    await db.commit()

    return DocumentResponse(
        id=doc_id, filename=req.url, doc_type="url", chunk_count=chunk_count
    )


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    user_id: str = "demo_user",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.user_id == user_id)
    )
    docs = result.scalars().all()
    return [
        DocumentResponse(
            id=d.id, filename=d.filename, doc_type=d.doc_type, chunk_count=d.chunk_count
        )
        for d in docs
    ]


@router.post("/query", response_model=RAGQueryResponse)
async def query_documents(
    req: RAGQueryRequest,
    user_id: str = "demo_user",
    db: AsyncSession = Depends(get_db),
):
    # Get document IDs to search
    if req.document_ids:
        doc_ids = req.document_ids
    else:
        result = await db.execute(
            select(Document.id).where(Document.user_id == user_id)
        )
        doc_ids = [row[0] for row in result.all()]

    if not doc_ids:
        raise HTTPException(400, "No documents uploaded yet")

    indexed_ids = [d for d in doc_ids if vector_store.has_index(user_id, d)]
    if not indexed_ids:
        return RAGQueryResponse(
            answer=(
                "Your account has document records, but the search index files are missing "
                "(this often happens if `backend/data/` was removed while the database still lists uploads). "
                "Re-upload the PDF or URL to rebuild the index."
            ),
            sources=[],
        )

    # Retrieve relevant chunks
    results = vector_store.search(
        user_id, indexed_ids, req.question, settings.RETRIEVAL_TOP_K
    )
    if not results:
        return RAGQueryResponse(
            answer=(
                "I couldn't find any relevant information in your documents. "
                "Try rephrasing closer to the source wording, or lower SIMILARITY_THRESHOLD in backend `.env` if matches are too strict."
            ),
            sources=[],
        )

    context_chunks = [chunk for chunk, _ in results]
    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""Context:
{context}

Question: {req.question}

Answer based ONLY on the context above:"""

    answer = await llm.generate(prompt, system=RAG_SYSTEM_PROMPT)

    return RAGQueryResponse(answer=answer.strip(), sources=context_chunks[:3])
