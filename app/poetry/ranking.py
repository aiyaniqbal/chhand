"""Rank / score generated stanza candidates for quality selection."""

from app.schemas import GeneratedLine


def score_stanza(lines: list[GeneratedLine]) -> float:
    """
    Compute a simple quality score for a stanza (higher is better).

    Scoring heuristics:
    - Each line with ``validation_status == "matched"`` contributes +2.0.
    - Each line with ``validation_status == "unvalidated"`` contributes +0.5
      (we give it benefit of the doubt).
    - Lines with ``"over"`` or ``"under"`` status contribute 0.0.
    - Empty lines penalise by -1.0.
    """
    score = 0.0
    for line in lines:
        text = line.text.strip()
        if not text:
            score -= 1.0
            continue
        if line.validation_status == "matched":
            score += 2.0
        elif line.validation_status == "unvalidated":
            score += 0.5
        # over / under / invalid → 0.0 contribution
    return score


def rank_stanzas(
    candidates: list[list[GeneratedLine]],
) -> list[list[GeneratedLine]]:
    """
    Return *candidates* sorted by descending quality score.
    Preserves relative order of equal-scoring stanzas (stable sort).
    """
    return sorted(candidates, key=score_stanza, reverse=True)
