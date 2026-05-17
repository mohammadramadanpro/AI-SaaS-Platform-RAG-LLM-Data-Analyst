"""Application configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI SaaS Platform"
    DEBUG: bool = False

    # Paths
    DATA_DIR: Path = Path("data")
    CACHE_DIR: Path = Path("cache")

    # LLM
    LLM_PROVIDER: str = "huggingface"  # "huggingface" or "ollama"
    HF_TOKEN: str = ""
    HF_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral:7b-instruct-v0.3-q4_K_M"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 1024

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # RAG
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.3

    # Rate limiting
    RATE_LIMIT_PER_HOUR: int = 20

    # File limits
    MAX_PDF_SIZE_MB: int = 10
    MAX_CSV_SIZE_MB: int = 50

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///data/app.db"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
