"""Prompts for meter-aware rewriting and rhyme generation."""

from app.schemas import LineResult, RewriteRequest


def build_rewrite_system_prompt() -> str:
    return (
        "You are an expert Hindi poet and prosody co-writer assisting a poet in Chhand.\n"
        "Your task is to propose candidate line rewrites that preserve the emotional intent and meaning\n"
        "of the user's line while attempting to match a required matra count (मात्रा काल).\n\n"
        "RULES:\n"
        "1. Write natural, elegant, literary Hindi in Devanagari script.\n"
        "2. Preserve the core semantic meaning and poetic tone of the original line.\n"
        "3. Pay close attention to the matra count diagnosis. Adjust word choices, verb endings,\n"
        "   or word order to fit the target matra count.\n"
        "4. Avoid unnatural filler words or artificial padding.\n"
        "5. If a rhyme requirement is provided, ensure the line concludes with a compatible rhyming sound.\n"
        "6. Return ONLY a valid JSON object matching the requested schema.\n"
        "7. Note: A separate deterministic Python meter engine will scan your candidates. Only candidates\n"
        "   that strictly match the target matra count will be presented to the poet."
    )


def build_rewrite_user_prompt(
    request: RewriteRequest,
    current_scan: LineResult,
) -> str:
    diagnosis_str = "\n".join(f"- {d}" for d in current_scan.diagnostics)
    syllable_summary = " ".join(f"{s.text}({s.weight})" for s in current_scan.syllables)
    rhyme_inst = (
        f"Optional rhyme requirement: Must rhyme with '{request.rhyme_requirement}'."
        if request.rhyme_requirement
        else "No specific rhyme constraint."
    )
    poet_inst = (
        f"Poet's guidance/meaning notes: '{request.instructions}'"
        if request.instructions
        else "Preserve the original meaning closely."
    )

    return (
        f"Meter: {request.selected_meter} (Charan index: {request.charan_index})\n"
        f'Original line: "{request.original_line}"\n'
        f"Current matra count: {current_scan.actual_matras}\n"
        f"Target matra count: {request.target_matra_count}\n"
        f"Current scansion: {syllable_summary}\n"
        f"Engine diagnosis:\n{diagnosis_str}\n"
        f"{poet_inst}\n"
        f"{rhyme_inst}\n\n"
        f"Provide {request.max_suggestions + 2} diverse candidate lines in natural Hindi.\n"
        "Return JSON in this exact structure:\n"
        "{\n"
        '  "candidates": [\n'
        "    {\n"
        '      "line": "suggested Hindi line in Devanagari",\n'
        '      "note": "brief explanation of adjustment (e.g. dropped extra verb ending, used synonym)"\n'
        "    }\n"
        "  ]\n"
        "}"
    )


def build_rhyme_prompt(word: str, count: int = 10) -> str:
    return (
        f"Generate {count} common, meaningful Hindi poetic words in Devanagari that rhyme with '{word}'.\n"
        "Return JSON in this exact structure:\n"
        "{\n"
        '  "rhymes": ["word1", "word2", "word3"]\n'
        "}"
    )
