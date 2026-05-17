"""Sentence-transformer embedding service — loaded once at startup."""

import numpy as np
from sentence_transformers import SentenceTransformer

from ..config import settings

_model: SentenceTransformer | None = None


def load_model():
    global _model
    _model = SentenceTransformer(settings.EMBEDDING_MODEL)


def embed(texts: list[str]) -> np.ndarray:
    if _model is None:
        load_model()
    return _model.encode(texts, normalize_embeddings=True).astype(np.float32)
