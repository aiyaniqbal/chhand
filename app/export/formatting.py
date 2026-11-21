"""Formatting utilities for lyric sheet and plain text poetry export."""

import re
from datetime import UTC, datetime


def clean_poem_title(title: str) -> str:
    """Clean and title-case a poem title, defaulting to 'Untitled Poem' if empty."""
    clean = title.strip()
    return clean if clean else "Untitled Poem"


def format_author_line(author: str) -> str:
    """Format poet / author attribution line."""
    clean = author.strip()
    return f"— {clean}" if clean else ""


def format_date(date_str: str | None = None) -> str:
    """Format an optional ISO date or return current formatted UTC date."""
    if date_str:
        return date_str.strip()
    return datetime.now(UTC).strftime("%B %d, %Y")


def group_lines_into_stanzas(lines: list[str], stanza_size: int = 2) -> list[list[str]]:
    """Group flat lines into stanzas (couplets by default)."""
    clean_lines = [line.strip() for line in lines if line.strip()]
    stanzas: list[list[str]] = []
    current: list[str] = []

    for line in clean_lines:
        current.append(line)
        if len(current) == stanza_size:
            stanzas.append(current)
            current = []

    if current:
        stanzas.append(current)

    return stanzas


def safe_filename(title: str, language: str, ext: str) -> str:
    """
    Generate an ASCII-safe filename for downloaded lyric sheets and HTTP headers.
    Example: 'poem_hi.txt' or 'morning_song_ur.html'
    """
    # Keep only ASCII letters, numbers, hyphens, and underscores
    ascii_title = "".join(
        c for c in title if c.isascii() and (c.isalnum() or c in (" ", "-", "_"))
    ).strip()
    safe_title = re.sub(r"[-\s]+", "_", ascii_title).strip("_")
    if not safe_title:
        safe_title = "poem"

    safe_ext = ext.lstrip(".")
    return f"{safe_title}_{language}.{safe_ext}".lower()
