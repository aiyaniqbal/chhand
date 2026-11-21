"""Language-specific prompt builders for poetry generation."""

from app.schemas import GenerateRequest

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

_HINDI_SYSTEM = (
    "You are a master of Hindi classical poetry. You write in Devanagari script, following the "
    "precise rules of Matra-based Chhand (छंद) prosody as codified in Pingala's treatise. "
    "You understand Doha (13+11+13+11 matra), Chaupai (16×4 matra), and free verse forms. "
    "You generate metrically accurate verse that is grammatically correct, emotionally resonant, "
    "and free of archaic or meaningless filler. "
    "Always respond with structured JSON only — no explanatory prose outside the JSON."
)

_URDU_SYSTEM = (
    "You are a master of Urdu classical poetry (شاعری). You compose in Nastaliq-style Urdu "
    "following the rules of 'Arooz (عروض) prosody and the Bahr (بحر) metrical system. "
    "You are fluent in Ghazal (غزل) conventions: Maqta, Radif, Qafia, and Matla. "
    "For Nazm (نظم) you write progressive thematic verse. "
    "Always respond with structured JSON only — no explanatory prose outside the JSON."
)

_BENGALI_SYSTEM = (
    "You are a master of Bengali (বাংলা) poetry with deep expertise in classical Chhanda "
    "(ছন্দ) prosody, including Aksharbritta (syllable-based), Matrabritta (matra-based), "
    "and Swarobritta (stress-based) meter systems. "
    "You write beautiful, grammatically correct Bengali verse with vivid imagery. "
    "Always respond with structured JSON only — no explanatory prose outside the JSON."
)

SYSTEM_PROMPTS: dict[str, str] = {
    "hi": _HINDI_SYSTEM,
    "ur": _URDU_SYSTEM,
    "bn": _BENGALI_SYSTEM,
}

# ---------------------------------------------------------------------------
# User prompt builders
# ---------------------------------------------------------------------------

_JSON_SCHEMA = """\
{
  "stanzas": [
    {
      "lines": [
        {"text": "<line in native script>", "transliteration": "<optional latin>"}
      ]
    }
  ]
}"""


def build_hindi_prompt(request: GenerateRequest) -> str:
    """Build a Hindi generation prompt with meter-specific guidance."""
    form = request.poem_form
    theme_note = f'Theme / seed: "{request.theme}"' if request.theme else "Choose a timeless theme."
    extra = f"\nAdditional instructions: {request.instructions}" if request.instructions else ""

    if form == "doha":
        meter_note = (
            "Compose a Doha (दोहा): 2 couplets, each couplet has 4 charans.\n"
            "Charan matra pattern: 13 | 11 | 13 | 11 (विषम 13, सम 11).\n"
            "Even charans (2nd, 4th) must end with a laghu+guru foot and rhyme with each other."
        )
    elif form == "chaupai":
        meter_note = (
            "Compose a Chaupai (चौपाई): each charan must have exactly 16 matras.\n"
            "No Jagana (।ऽ।) or Tagana (ऽऽ।) foot allowed at the end of a charan."
        )
    elif form == "free_verse":
        meter_note = "Compose free verse (मुक्त छंद) Hindi poetry — no strict meter required."
    else:
        meter_note = (
            f"Compose a '{form}' poem in Hindi. Follow the standard prosodic rules for this form."
        )

    return (
        f"TASK: Generate {request.num_stanzas} stanza(s) of Hindi poetry.\n"
        f"{meter_note}\n"
        f"{theme_note}{extra}\n\n"
        f"Return ONLY valid JSON matching this schema:\n{_JSON_SCHEMA}"
    )


def build_urdu_prompt(request: GenerateRequest) -> str:
    """Build an Urdu generation prompt with Bahr-aware guidance."""
    form = request.poem_form
    theme_note = (
        f'Theme / seed: "{request.theme}"' if request.theme else "Choose a classical theme."
    )
    extra = f"\nAdditional instructions: {request.instructions}" if request.instructions else ""

    if form == "ghazal":
        form_note = (
            "Compose a Ghazal (غزل).\n"
            "Rules: The first couplet (Matla) ends both lines with the same Radif and Qafia. "
            "Subsequent couplets only end the second line with Radif+Qafia. "
            "The final couplet (Maqta) may contain the poet's pen-name. "
            "Each sher (couplet) must be semantically complete."
        )
    elif form == "nazm":
        form_note = (
            "Compose a Nazm (نظم) — a progressive thematic poem with consistent Bahr throughout. "
            "Each verse should build on the previous one thematically."
        )
    else:
        form_note = f"Compose Urdu free verse (آزاد نظم) — {request.num_stanzas} stanza(s)."

    return (
        f"TASK: Generate {request.num_stanzas} stanza(s) of Urdu poetry.\n"
        f"{form_note}\n"
        f"{theme_note}{extra}\n\n"
        f"Return ONLY valid JSON matching this schema:\n{_JSON_SCHEMA}"
    )


def build_bengali_prompt(request: GenerateRequest) -> str:
    """Build a Bengali generation prompt with Chhanda-aware guidance."""
    form = request.poem_form
    theme_note = (
        f'Theme / seed: "{request.theme}"' if request.theme else "Choose an evocative theme."
    )
    extra = f"\nAdditional instructions: {request.instructions}" if request.instructions else ""

    form_notes: dict[str, str] = {
        "aksharbritta": (
            "Compose Aksharbritta (অক্ষরবৃত্ত) — syllable-count-based verse. "
            "Each line must contain the same number of syllables (typically 14: 8+6 or 6+8)."
        ),
        "matrabritta": (
            "Compose Matrabritta (মাত্রাবৃত্ত) — matra-weight-based verse. "
            "Each foot (পর্ব) should have equal matra totals."
        ),
        "swarobritta": (
            "Compose Swarobritta (স্বরবৃত্ত) — stress-based verse. "
            "Each line has 4 stresses (ঝোঁক) with 1-3 unstressed syllables between them."
        ),
        "free_verse": ("Compose free verse (গদ্যকবিতা / মুক্তছন্দ) Bengali poetry — no strict meter."),
    }
    form_note = form_notes.get(form, f"Compose a '{form}' poem in Bengali.")

    return (
        f"TASK: Generate {request.num_stanzas} stanza(s) of Bengali poetry.\n"
        f"{form_note}\n"
        f"{theme_note}{extra}\n\n"
        f"Return ONLY valid JSON matching this schema:\n{_JSON_SCHEMA}"
    )


_BUILDERS = {
    "hi": build_hindi_prompt,
    "ur": build_urdu_prompt,
    "bn": build_bengali_prompt,
}


def build_generation_prompt(request: GenerateRequest) -> tuple[str, str]:
    """
    Return ``(system_prompt, user_prompt)`` for the given generation request.

    Falls back to a generic system prompt + Hindi-style structure for unknown
    language codes (should not occur after request validation).
    """
    system_prompt = SYSTEM_PROMPTS.get(request.language, SYSTEM_PROMPTS["hi"])
    builder = _BUILDERS.get(request.language, build_hindi_prompt)
    user_prompt = builder(request)
    return system_prompt, user_prompt
