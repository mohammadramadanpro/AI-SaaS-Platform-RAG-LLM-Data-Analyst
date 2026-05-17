"""Text chunking for RAG pipeline."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " "],
    length_function=len,
)


def chunk_text(text: str) -> list[str]:
    chunks = _splitter.split_text(text)
    # Filter out tiny/empty chunks
    return [c.strip() for c in chunks if len(c.strip()) > 20]
