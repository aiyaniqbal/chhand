"""Urdu diacritic (Harakat) extraction and manipulation."""

from app.meter.urdu.characters import HARAKAT, is_diacritic


def extract_diacritics(text: str) -> list[tuple[int, str, str]]:
    """
    Extract all diacritics in the text with their character index and name.
    Returns list of (index, character, name) tuples.
    """
    results: list[tuple[int, str, str]] = []
    for idx, ch in enumerate(text):
        if is_diacritic(ch):
            results.append((idx, ch, HARAKAT.get(ch, "diacritic")))
    return results


def has_diacritics(text: str) -> bool:
    """Return True if the text contains at least one Harakat / diacritic mark."""
    return any(is_diacritic(ch) for ch in text)


def strip_diacritics(text: str) -> str:
    """Return a copy of the text with all diacritics removed."""
    return "".join(ch for ch in text if not is_diacritic(ch))
