"""
Utility helper functions for the AI Product Intelligence Platform.

Reference: architecture_final.md §8 (API Design)
"""
import re
import hashlib
from typing import Optional
from datetime import datetime, timedelta


def normalize_mpn(mpn: str) -> str:
    """
    Normalize a Manufacturer Part Number to uppercase with trimmed whitespace.
    
    Args:
        mpn: Raw MPN string
    
    Returns:
        Normalized MPN
    """
    return mpn.strip().upper()


def extract_mpn_pattern(text: str) -> Optional[str]:
    """
    Extract a potential MPN from free text using regex patterns.
    
    Common MPN patterns:
    - Alphanumeric with optional hyphens (e.g., SN74LS00N, LM358N)
    - Starts with letters, ends with alphanumeric
    
    Args:
        text: Free text that may contain an MPN
    
    Returns:
        Extracted MPN if found, None otherwise
    """
    # Common MPN patterns: alphanumeric, 4-20 chars, optional hyphens
    pattern = r'\b[A-Z][A-Z0-9]{2,5}[A-Z0-9-]{1,15}\b'
    match = re.search(pattern, text.upper())
    return match.group(0) if match else None


def generate_cache_key(mpn: str, brand: str) -> str:
    """
    Generate a deterministic cache key for a product.
    
    Args:
        mpn: Manufacturer Part Number
        brand: Brand name
    
    Returns:
        SHA-256 hash as cache key
    """
    key = f"{normalize_mpn(mpn)}:{brand.strip().upper()}"
    return hashlib.sha256(key.encode()).hexdigest()


def is_within_ttl(timestamp: str, ttl_hours: int = 24) -> bool:
    """
    Check if a timestamp is within the TTL window.
    
    Args:
        timestamp: ISO 8601 timestamp string
        ttl_hours: TTL in hours (default: 24)
    
    Returns:
        True if timestamp is within TTL, False otherwise
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return datetime.utcnow() - dt < timedelta(hours=ttl_hours)
    except (ValueError, TypeError):
        return False


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to a maximum length while preserving word boundaries.
    
    Args:
        text: Text to truncate
        max_length: Maximum character length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...'
