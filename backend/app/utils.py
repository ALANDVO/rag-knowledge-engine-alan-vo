"""Utility functions for RAG Knowledge Engine."""
import hashlib
import re
import json
from datetime import datetime, timezone
from typing import Any


def generate_id(prefix: str = "id") -> str:
    """Generate a unique ID with prefix."""
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def hash_content(content: str, algorithm: str = "sha256") -> str:
    """Hash content using specified algorithm."""
    hasher = hashlib.new(algorithm)
    hasher.update(content.encode("utf-8"))
    return hasher.hexdigest()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove path components
    filename = filename.split("/")[-1].split("\\")[-1]
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        max_name = 255 - len(ext) - 1
        filename = name[:max_name] + ("." + ext if ext else "")
    return filename


def format_bytes(bytes_value: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} PB"


def parse_json_safely(text: str, default: Any = None) -> Any:
    """Parse JSON with fallback to default."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def utc_now_iso() -> str:
    """Get current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def merge_metadata(base: dict, override: dict) -> dict:
    """Merge two metadata dictionaries, with override taking precedence."""
    result = base.copy()
    result.update(override)
    return result


def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """Extract simple keywords from text (basic implementation)."""
    # Remove punctuation and convert to lowercase
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    # Filter common stop words
    stop_words = {
        "the", "and", "for", "are", "but", "not", "you", "all", "any", "can",
        "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
        "how", "its", "may", "new", "now", "old", "see", "two", "who", "boy",
        "did", "she", "use", "way", "will", "with", "this", "that", "from",
        "they", "have", "been", "were", "what", "when", "where", "which",
        "while", "there", "their", "would", "could", "should", "about",
        "after", "before", "during", "under", "over", "again", "further",
        "then", "once", "here", "there", "when", "where", "why", "how",
        "each", "few", "more", "most", "other", "some", "such", "than",
        "too", "very", "just", "don", "should", "now"
    }
    filtered = [w for w in words if w not in stop_words]
    # Count frequency
    freq: dict[str, int] = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    # Sort by frequency
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_keywords]]