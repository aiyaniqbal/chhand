"""Bengali syllable (Akshara / Dal) segmentation and property tracking."""

from dataclasses import dataclass

from app.meter.bengali.characters import (
    ANUSVARA,
    HASANTA,
    MODIFIERS,
    NUKTA,
    VISARGA,
    is_consonant,
    is_hasanta,
    is_independent_vowel,
    is_vowel_sign,
)
from app.meter.bengali.normalize import normalize_bengali


@dataclass
class BengaliSyllable:
    """A single Bengali orthographic syllable (Akshara)."""

    text: str
    is_open: bool
    is_conjunct: bool
    source_start: int
    source_end: int


def syllabify_bengali(text: str) -> list[BengaliSyllable]:
    """
    Segment Bengali text into orthographic Akshara units.
    Preserves exact character offsets in the input string.
    """
    norm = normalize_bengali(text)
    syllables: list[BengaliSyllable] = []

    i = 0
    n = len(norm)

    while i < n:
        ch = norm[i]

        # Skip whitespace and punctuation
        if ch in {" ", "\t", "\n", "।", "॥", ",", ";", ".", "!", "?", "-", ":", '"', "'"}:
            i += 1
            continue

        start = i

        # Case 1: Independent vowel
        if is_independent_vowel(ch):
            i += 1
            # Modifiers
            while i < n and (norm[i] in MODIFIERS or is_hasanta(norm[i])):
                i += 1
            syllables.append(
                BengaliSyllable(
                    text=norm[start:i],
                    is_open=True,
                    is_conjunct=False,
                    source_start=start,
                    source_end=i,
                )
            )
            continue

        # Case 2: Consonant cluster
        if is_consonant(ch):
            is_conj = False
            i += 1
            if i < n and norm[i] == NUKTA:
                i += 1
            while i < n:
                if is_hasanta(norm[i]):
                    if i + 1 < n and is_consonant(norm[i + 1]):
                        # Consonant conjunct (যুক্তাক্ষর)
                        is_conj = True
                        i += 2
                        if i < n and norm[i] == NUKTA:
                            i += 1
                    else:
                        # Hasanta at end of syllable/word (হসন্তান্ত রুদ্ধদল)
                        i += 1
                        break
                elif is_vowel_sign(norm[i]):
                    i += 1
                    break
                else:
                    break

            # Check trailing modifiers (ং, ঃ, ঁ)
            while i < n and norm[i] in MODIFIERS:
                i += 1

            subtext = norm[start:i]
            is_open = not subtext.endswith(HASANTA) and not any(
                m in subtext for m in (ANUSVARA, VISARGA)
            )

            syllables.append(
                BengaliSyllable(
                    text=subtext,
                    is_open=is_open,
                    is_conjunct=is_conj,
                    source_start=start,
                    source_end=i,
                )
            )
            continue

        # Other character
        i += 1

    return syllables


def syllabify_bengali_dals(text: str) -> list[BengaliSyllable]:
    """
    Segment Bengali text into spoken pulse / syllable units (Dal / দল) for
    Swarabritta and Matrabritta analysis.
    In spoken Bengali, an unvocalized consonant at the end of a multi-character
    word joins the preceding akshara as a closed coda (রুদ্ধদল).
    """
    norm = normalize_bengali(text)
    words = [w for w in norm.split() if w.strip()]
    dals: list[BengaliSyllable] = []

    current_offset = 0
    for word in words:
        w_idx = norm.find(word, current_offset)
        if w_idx != -1:
            current_offset = w_idx
        aksharas = syllabify_bengali(word)
        if not aksharas:
            continue

        if len(aksharas) > 1:
            last_akshara = aksharas[-1]
            # If the last akshara is a single consonant without vowel sign or hasanta
            if (
                len(last_akshara.text) <= 2
                and is_consonant(last_akshara.text[0])
                and not any(is_vowel_sign(c) for c in last_akshara.text)
                and not is_hasanta(last_akshara.text[-1])
            ):
                # Merge into the preceding akshara as a closed coda
                prev = aksharas[-2]
                merged_text = prev.text + last_akshara.text
                aksharas[-2] = BengaliSyllable(
                    text=merged_text,
                    is_open=False,
                    is_conjunct=prev.is_conjunct,
                    source_start=prev.source_start + current_offset,
                    source_end=last_akshara.source_end + current_offset,
                )
                aksharas.pop()

        for a in aksharas:
            dals.append(
                BengaliSyllable(
                    text=a.text,
                    is_open=a.is_open,
                    is_conjunct=a.is_conjunct,
                    source_start=a.source_start + current_offset,
                    source_end=a.source_end + current_offset,
                )
            )
        current_offset += len(word)

    return dals
