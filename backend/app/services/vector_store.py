"""FAISS vector store — per-user, per-document indexes."""

import json
from pathlib import Path

import faiss
import numpy as np

from ..config import settings
from . import embeddings


class VectorStore:
    def __init__(self):
        self.base = settings.DATA_DIR / "users"

    def _index_path(self, user_id: str, doc_id: str) -> Path:
        return self.base / user_id / "indexes" / f"{doc_id}.faiss"

    def _meta_path(self, user_id: str, doc_id: str) -> Path:
        return self.base / user_id / "indexes" / f"{doc_id}_meta.json"

    def has_index(self, user_id: str, doc_id: str) -> bool:
        return self._index_path(user_id, doc_id).exists() and self._meta_path(
            user_id, doc_id
        ).exists()

    def index_chunks(self, user_id: str, doc_id: str, chunks: list[str]):
        vecs = embeddings.embed(chunks)
        dim = vecs.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vecs)

        path = self.base / user_id / "indexes"
        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self._index_path(user_id, doc_id)))
        self._meta_path(user_id, doc_id).write_text(
            json.dumps({"chunks": chunks})
        )
        return len(chunks)

    def search(
        self, user_id: str, doc_ids: list[str], query: str, top_k: int = 5
    ) -> list[tuple[str, float]]:
        query_vec = embeddings.embed([query])
        results = []

        for doc_id in doc_ids:
            idx_path = self._index_path(user_id, doc_id)
            if not idx_path.exists():
                continue
            index = faiss.read_index(str(idx_path))
            meta = json.loads(self._meta_path(user_id, doc_id).read_text())
            chunks = meta["chunks"]

            scores, indices = index.search(query_vec, min(top_k, index.ntotal))
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and score > settings.SIMILARITY_THRESHOLD:
                    results.append((chunks[idx], float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def delete(self, user_id: str, doc_id: str):
        self._index_path(user_id, doc_id).unlink(missing_ok=True)
        self._meta_path(user_id, doc_id).unlink(missing_ok=True)


vector_store = VectorStore()
