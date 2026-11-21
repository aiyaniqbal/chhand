"""Urdu syllabification and syllable weight determination."""

from dataclasses import dataclass
from typing import Literal

from app.meter.urdu.characters import is_consonant, is_diacritic, is_long_vowel, is_word_boundary
from app.meter.urdu.lexicon import lookup_word_pattern
from app.meter.urdu.normalize import normalize_urdu


@dataclass
class UrduSyllable:
    """A syllable candidate in Urdu prosody."""

    text: str
    weight: Literal["short", "long", "overlong", "ambiguous"]
    source_start: int
    source_end: int


def _estimate_word_syllables(word: str, start_offset: int) -> list[UrduSyllable]:
    """Estimate syllables for a single word."""
    clean = word.strip()
    if not clean:
        return []

    # Check lexicon first
    pattern = lookup_word_pattern(clean)
    if pattern:
        # Map pattern letters (S, L) to syllables
        sylls: list[UrduSyllable] = []
        n = len(pattern)
        word_len = len(clean)
        for i, code in enumerate(pattern):
            # Approximate character spans for each syllable
            s_start = start_offset + (i * word_len) // n
            s_end = start_offset + ((i + 1) * word_len) // n
            weight_str: Literal["short", "long", "overlong", "ambiguous"]
            if code == "S":
                weight_str = "short"
            elif code == "L":
                weight_str = "long"
            elif code == "O":
                weight_str = "overlong"
            else:
                weight_str = "ambiguous"

            subtext = clean[(i * word_len) // n : ((i + 1) * word_len) // n] or clean
            sylls.append(
                UrduSyllable(
                    text=subtext,
                    weight=weight_str,
                    source_start=s_start,
                    source_end=s_end,
                )
            )
        return sylls

    # Heuristic decomposition if not in lexicon
    sylls = []
    i = 0
    w_len = len(clean)
    while i < w_len:
        ch = clean[i]
        curr_start = start_offset + i
        curr_text = ch

        if is_long_vowel(ch):
            sylls.append(
                UrduSyllable(
                    text=curr_text,
                    weight="long",
                    source_start=curr_start,
                    source_end=curr_start + 1,
                )
            )
            i += 1
        elif is_consonant(ch):
            # Check if followed by long vowel
            if i + 1 < w_len and is_long_vowel(clean[i + 1]):
                curr_text = clean[i : i + 2]
                sylls.append(
                    UrduSyllable(
                        text=curr_text,
                        weight="long",
                        source_start=curr_start,
                        source_end=curr_start + 2,
                    )
                )
                i += 2
            elif i + 1 < w_len and is_diacritic(clean[i + 1]):
                curr_text = clean[i : i + 2]
                sylls.append(
                    UrduSyllable(
                        text=curr_text,
                        weight="short",
                        source_start=curr_start,
                        source_end=curr_start + 2,
                    )
                )
                i += 2
            else:
                # Standalone consonant
                sylls.append(
                    UrduSyllable(
                        text=curr_text,
                        weight="short",
                        source_start=curr_start,
                        source_end=curr_start + 1,
                    )
                )
                i += 1
        else:
            i += 1

    return (
        sylls
        if sylls
        else [
            UrduSyllable(
                text=clean,
                weight="ambiguous",
                source_start=start_offset,
                source_end=start_offset + w_len,
            )
        ]
    )


def syllabify_urdu(text: str) -> list[UrduSyllable]:
    """Segment an Urdu line into syllables with short/long weights and character offsets."""
    norm = normalize_urdu(text)
    syllables: list[UrduSyllable] = []

    i = 0
    while i < len(norm):
        if is_word_boundary(norm[i]):
            i += 1
            continue

        w_start = i
        while i < len(norm) and not is_word_boundary(norm[i]):
            i += 1
        w_end = i
        word = norm[w_start:w_end]

        word_sylls = _estimate_word_syllables(word, w_start)
        syllables.extend(word_sylls)

    return syllables
