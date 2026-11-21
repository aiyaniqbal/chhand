"""Matrabritta (মাত্রাবৃত্ত / কলাবৃত্ত) meter analysis for Bengali poetry."""

from app.meter.bengali.syllables import syllabify_bengali_dals


def matrabritta_count(text: str) -> int:
    """
    Calculate the total matra count of a Bengali line under Matrabritta rules.
    - Open syllable (মুক্তদল): 1 matra.
    - Closed syllable (রুদ্ধদল, ending in consonant/hasanta/modifier): 2 matras.
    """
    dals = syllabify_bengali_dals(text)
    total = 0
    for s in dals:
        total += 1 if s.is_open else 2
    return total


def scan_matrabritta(text: str, target_matras: int = 12) -> dict:
    """
    Scan a line against a target matra count under Bengali Matrabritta rules.
    """
    dals = syllabify_bengali_dals(text)
    count = 0
    for s in dals:
        count += 1 if s.is_open else 2

    diff = count - target_matras

    if diff == 0:
        status = "matched"
        diagnostic = f"Matches target {target_matras} matras."
    elif diff > 0:
        status = "over"
        diagnostic = f"Line has {count} matras ({diff} over target {target_matras})."
    else:
        status = "under"
        diagnostic = f"Line has {count} matras ({abs(diff)} under target {target_matras})."

    return {
        "count": count,
        "target": target_matras,
        "diff": diff,
        "status": status,
        "diagnostic": diagnostic,
    }
