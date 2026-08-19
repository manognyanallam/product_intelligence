"""
Settings module — re-exports settings for convenient imports.

Usage:
    from app.core.settings import settings
    print(settings.gemini_api_key)

Reference: architecture_final.md §12 (Security Architecture)
"""
from app.core.config import Settings, settings

__all__ = ["Settings", "settings"]
