"""
Configuration loader for the AI Product Intelligence Platform.

Loads environment variables from .env file and provides typed settings.
Reference: architecture_final.md §12 (Security Architecture)
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    See .env.example for the full list of available settings.
    """
    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_embedding_model: str = "text-embedding-004"

    # ChromaDB
    chroma_db_path: str = "./chromadb_data"
    chroma_collection_product_cache: str = "product_cache"
    chroma_collection_document_chunks: str = "document_chunks"
    chroma_collection_embeddings: str = "embeddings"

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://192.168.1.11:3000,http://192.168.1.11:3001,https://product-intel.vercel.app"
    log_level: str = "INFO"

    # Upload limits
    max_upload_size_mb: int = 10

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_analyze: int = 10
    rate_limit_upload: int = 5
    rate_limit_history: int = 30
    rate_limit_health: int = 60

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        origins = [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]
        default_local = [
            "http://localhost:3000",
            "http://localhost:3001",
            "https://product-intelligence-zpj7.onrender.com",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://192.168.1.11:3000",
            "http://192.168.1.11:3001",
        ]
        for loc in default_local:
            if loc not in origins:
                origins.append(loc)
        return origins

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
