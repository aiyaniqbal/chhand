"""Aksharbritta (অক্ষরবৃত্ত / পয়ার) meter analysis for Bengali poetry."""

from app.meter.bengali.syllables import syllabify_bengali


def aksharbritta_count(text: str) -> int:
    """
    Count the number of Aksharas in a line of Bengali poetry under Aksharbritta rules.
    In standard Aksharbritta scansion, each orthographic syllable counts as 1 unit.
    """
    syllables = syllabify_bengali(text)
    return len(syllables)


def scan_aksharbritta(text: str, target_count: int = 14) -> dict:
    """
    Scan an Aksharbritta line against a target akshara count (e.g. 14 for Payar: 8 + 6).
    """
    syllables = syllabify_bengali(text)
    count = len(syllables)
    diff = count - target_count

    if diff == 0:
        status = "matched"
        diagnostic = f"Matches target {target_count} aksharas."
    elif diff > 0:
        status = "over"
        diagnostic = f"Line has {count} aksharas ({diff} over target {target_count})."
    else:
        status = "under"
        diagnostic = f"Line has {count} aksharas ({abs(diff)} under target {target_count})."

    # Caesura (yati) positions: in 14-akshara Payar, yati is typically after 8 aksharas
    break_positions = []
    if count >= 8 and target_count == 14:
        break_positions.append(syllables[7].source_end)

    return {
        "count": count,
        "target": target_count,
        "diff": diff,
        "status": status,
        "diagnostic": diagnostic,
        "break_positions": break_positions,
    }
