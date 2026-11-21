"""Urdu Qafiya (rhyme) and Radif (refrain) extraction for Ghazal analysis."""


def extract_radif(lines: list[str]) -> str | None:
    """
    Identify common refrain (Radif) at the end of multiple hemistichs.
    In Ghazal, the Matla has Radif in both misras, and subsequent couplets in the second misra.
    """
    if len(lines) < 2:
        return None

    words_per_line = [[w for w in line.strip().split() if w] for line in lines]
    if any(len(w) == 0 for w in words_per_line):
        return None

    # Check for trailing common words
    common_trailing: list[str] = []
    min_len = min(len(w) for w in words_per_line)

    for i in range(1, min_len + 1):
        trailing_word = words_per_line[0][-i]
        if all(w[-i] == trailing_word for w in words_per_line):
            common_trailing.insert(0, trailing_word)
        else:
            break

    return " ".join(common_trailing) if common_trailing else None


def extract_qafiya(lines: list[str]) -> dict:
    """
    Extract Qafiya candidates and check rhyme consistency across lines.
    """
    radif = extract_radif(lines)
    radif_word_count = len(radif.split()) if radif else 0

    rhyme_words: list[str] = []
    for line in lines:
        words = [w for w in line.strip().split() if w]
        if len(words) > radif_word_count:
            rhyme_words.append(words[-(radif_word_count + 1)])

    # In Urdu prosody, Harf-e-Ravi is the primary rhyming consonant letter at the end
    ending_sounds = [w[-1] if len(w) >= 1 else w for w in rhyme_words]
    is_consistent = len(set(ending_sounds)) == 1 if ending_sounds else False

    return {
        "radif": radif,
        "rhyme_words": rhyme_words,
        "is_consistent": is_consistent,
        "rhyme_ending": ending_sounds[0] if ending_sounds else None,
    }
