from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class SyllableDetail(BaseModel):
    """Detailed weight and classification for an individual Devanagari syllable."""

    text: str = Field(..., description="Surface text of the syllable/akshara")
    weight: int = Field(..., ge=1, le=2, description="Calculated matra weight (1 or 2)")
    classification: Literal["laghu", "guru"] = Field(
        ..., description="Laghu (1 matra) or Guru (2 matras)"
    )
    start: int = Field(..., ge=0, description="Start character index in original source string")
    end: int = Field(..., ge=0, description="End character index in original source string")
    reason: str = Field(..., description="Phonological justification for weight assignment")
    cumulative: int = Field(default=0, description="Cumulative matra count after this syllable")


class LineResult(BaseModel):
    """Scan and scansion results for a single charan or line."""

    charan_index: int = Field(..., description="0-indexed charan order")
    original_text: str = Field(..., description="Raw input text")
    normalized_text: str = Field(..., description="Unicode normalized text")
    target_matras: int = Field(..., description="Required matra count for this charan")
    actual_matras: int = Field(..., description="Calculated total matra count")
    difference: int = Field(..., description="actual_matras - target_matras")
    status: Literal["matched", "over", "under", "ambiguous", "invalid"] = Field(
        ..., description="Meter evaluation status"
    )
    syllables: list[SyllableDetail] = Field(
        default_factory=list, description="Sequence of decomposed syllables with weights"
    )
    individual_weights: list[int] = Field(
        default_factory=list, description="List of integer weights"
    )
    cumulative_weights: list[int] = Field(
        default_factory=list, description="Running sum of weights after each syllable"
    )
    character_spans: list[list[int]] = Field(
        default_factory=list, description="[start, end] indices in original text"
    )
    break_positions: list[int] = Field(
        default_factory=list, description="Syllable indices where target was exceeded"
    )
    overflow_span: list[int] | None = Field(
        default=None, description="[start, end] char indices of overflow text if over-count"
    )
    diagnostics: list[str] = Field(
        default_factory=list, description="Human-readable scansion diagnostics"
    )
    pronunciation_notes: list[str] = Field(
        default_factory=list, description="Notes on pronunciation assumptions or ambiguities"
    )


class AnalyzeRequest(BaseModel):
    """Payload for meter scanning endpoint."""

    meter: Literal["doha", "chaupai", "custom"] = Field(
        default="doha", description="Target poetic meter"
    )
    charans: list[str] = Field(default_factory=list, description="List of charan lines to analyze")
    custom_pattern: list[int] | None = Field(
        default=None, description="Custom matra target per charan, e.g. [12, 12, 14, 12]"
    )
    pronunciation_mode: Literal["orthographic", "phonetic", "manual"] = Field(
        default="orthographic", description="Schwa and pronunciation evaluation mode"
    )
    pronunciation_overrides: dict[str, Any] | None = Field(
        default=None, description="Optional manual weight overrides by token or position"
    )


class AnalyzeResponse(BaseModel):
    """Aggregate response for poem analysis."""

    overall_status: Literal["matched", "needs_revision", "incomplete", "ambiguous", "invalid"] = (
        Field(..., description="Aggregate status of poem")
    )
    meter: str = Field(..., description="Meter name")
    target_pattern: list[int] = Field(..., description="Target matra counts per charan")
    lines: list[LineResult] = Field(
        default_factory=list, description="Detailed analysis per charan"
    )
    summary: str = Field(..., description="Summary message of the scansion")


class RewriteRequest(BaseModel):
    """Request to generate meter-verified alternative lines."""

    original_line: str = Field(..., description="The broken or original Hindi line")
    target_matra_count: int = Field(..., gt=0, description="Target matra count required")
    selected_meter: str = Field(default="doha", description="Name of the poetic meter")
    charan_index: int = Field(default=0, description="Index of the charan within the stanza")
    custom_pattern: list[int] | None = Field(
        default=None, description="Custom matra target per charan if selected_meter is custom"
    )
    instructions: str = Field(
        default="", description="Poet guidance or specific meaning to preserve"
    )
    rhyme_requirement: str | None = Field(
        default=None, description="Optional target word or ending to rhyme with"
    )
    max_suggestions: int = Field(
        default=3, ge=1, le=5, description="Maximum number of verified suggestions"
    )
    pronunciation_mode: Literal["orthographic", "phonetic", "manual"] = Field(
        default="orthographic", description="Pronunciation mode for verification"
    )


class Suggestion(BaseModel):
    """A candidate rewrite verified strictly by the deterministic engine."""

    suggested_line: str = Field(..., description="The verified Hindi line")
    text: str | None = Field(default=None, description="Alias for suggested_line")
    replacement_line: str | None = Field(default=None, description="Alias for suggested_line")
    calculated_matra_count: int = Field(..., description="Matra count confirmed by engine")
    actual_matras: int | None = Field(default=None, description="Alias for calculated_matra_count")
    actual_matra_count: int | None = Field(
        default=None, description="Alias for calculated_matra_count"
    )
    target_matra_count: int = Field(..., description="Requested target matra count")
    target_matras: int | None = Field(default=None, description="Alias for target_matra_count")
    verified_status: bool = Field(True, description="Always True; only verified lines are returned")
    verified: bool = Field(True, description="Alias for verified_status")
    verification_status: str = Field(default="matched", description="Engine verification status")
    rhyme_compatibility: bool | None = Field(
        default=None, description="True if compatible with rhyme requirement"
    )
    meaning_note: str = Field(default="", description="Explanation of adjustment made")
    explanation: str | None = Field(default=None, description="Alias for meaning_note")
    syllables: list[SyllableDetail] = Field(
        default_factory=list, description="Verified syllable sequence"
    )
    verification_details: dict[str, Any] = Field(
        default_factory=dict, description="Diagnostic data from meter scan"
    )

    def model_post_init(self, __context: Any) -> None:
        if self.text is None:
            self.text = self.suggested_line
        if self.replacement_line is None:
            self.replacement_line = self.suggested_line
        if self.actual_matras is None:
            self.actual_matras = self.calculated_matra_count
        if self.actual_matra_count is None:
            self.actual_matra_count = self.calculated_matra_count
        if self.target_matras is None:
            self.target_matras = self.target_matra_count
        if self.explanation is None:
            self.explanation = self.meaning_note


class RewriteResponse(BaseModel):
    """Verified suggestions response."""

    suggestions: list[Suggestion] = Field(
        default_factory=list, description="Verified suggestions matching target matras"
    )
    message: str = Field(..., description="Status explanation or guidance")
    attempts_made: int = Field(default=1, description="Number of LLM attempts executed")
    attempts_used: int | None = Field(default=None, description="Alias for attempts_made")
    provider: str = Field(default="gemini", description="AI model provider name")

    def model_post_init(self, __context: Any) -> None:
        if self.attempts_used is None:
            self.attempts_used = self.attempts_made


class RhymeRequest(BaseModel):
    """Payload to find Hindi rhyming words."""

    word: str = Field(..., min_length=1, description="Word or line ending to rhyme with")
    limit: int = Field(default=10, ge=1, le=30, description="Max suggestions to return")
    preference: str | None = Field(
        default=None, description="Optional stylistic preference or meter hint"
    )


class RhymeMatch(BaseModel):
    """An individual rhyming word candidate."""

    word: str = Field(..., description="Rhyming Hindi word")
    match_type: Literal["exact", "approximate"] = Field(
        ..., description="Exact phonetic tail or approximate rhyme"
    )
    rhyme_tail: str = Field(..., description="Extracted rhyming sound in Devanagari")
    score: float = Field(default=1.0, description="Relevance / phonological match score")


class RhymeResponse(BaseModel):
    """Response containing rhyming word matches."""

    original_word: str = Field(..., description="Input word")
    rhyme_tail: str = Field(..., description="Normalized phonetic tail")
    exact_matches: list[str] = Field(default_factory=list, description="Words with exact tail")
    approximate_matches: list[str] = Field(
        default_factory=list, description="Words with approximate rhyme"
    )
    all_matches: list[RhymeMatch] = Field(default_factory=list, description="Structured match list")
    category: str = Field(default="", description="Phonetic category descriptor")


class HealthResponse(BaseModel):
    """Application health, version, and provider readiness status."""

    status: str = "ok"
    version: str = "1.0.0"
    meter_engine: dict[str, Any] | str = Field(
        default_factory=lambda: {"available": True}, description="Meter engine availability"
    )
    llm: dict[str, Any] | None = Field(
        default=None, description="LLM provider configuration status"
    )
    llm_configured: bool = Field(default=False, description="Legacy indicator for LLM availability")
    environment: str = "development"


# ---------------------------------------------------------------------------
# Poetry Generation Schemas
# ---------------------------------------------------------------------------

_SUPPORTED_LANGUAGES = {"hi", "ur", "bn"}
_SUPPORTED_FORMS = {
    "hi": {"doha", "chaupai", "custom", "free_verse"},
    "ur": {"ghazal", "nazm", "free_verse"},
    "bn": {"aksharbritta", "matrabritta", "swarobritta", "free_verse"},
}


class GeneratedLine(BaseModel):
    """A single generated poem line with optional meter metadata."""

    text: str = Field(..., description="The generated line text in its native script")
    transliteration: str | None = Field(
        default=None, description="Optional Latin-script transliteration"
    )
    matra_count: int | None = Field(
        default=None, description="Matra / syllable weight count where applicable"
    )
    validation_status: Literal["matched", "unvalidated", "invalid", "over", "under"] = Field(
        default="unvalidated",
        description="Meter validation outcome for this line",
    )
    validation_note: str = Field(default="", description="Human-readable validation detail")


class PoemValidation(BaseModel):
    """Aggregate validation result for a generated poem."""

    overall_status: (
        Literal["valid", "partial", "verified", "partially_verified", "unvalidated", "invalid"]
        | None
    ) = None
    status: (
        Literal["valid", "partial", "verified", "partially_verified", "unvalidated", "invalid"]
        | None
    ) = None
    validated_lines: int | None = None
    meter_matches: int | None = None
    total_lines: int | None = None
    total_units: int | None = None
    notes: list[str] = Field(default_factory=list, description="Validation messages")

    def model_post_init(self, __context: Any) -> None:
        if self.overall_status is None:
            self.overall_status = self.status or "unvalidated"
        if self.status is None:
            self.status = self.overall_status
        if self.validated_lines is None:
            self.validated_lines = self.meter_matches if self.meter_matches is not None else 0
        if self.meter_matches is None:
            self.meter_matches = self.validated_lines
        if self.total_lines is None:
            self.total_lines = self.total_units if self.total_units is not None else 0
        if self.total_units is None:
            self.total_units = self.total_lines


class GenerateRequest(BaseModel):
    """Request payload for POST /api/generate."""

    language: str = Field(..., description="BCP-47 language code: 'hi', 'ur', or 'bn'")
    poem_form: str = Field(
        ..., description="Requested poem form, e.g. 'doha', 'ghazal', 'free_verse'"
    )
    theme: str = Field(default="", description="Optional thematic prompt or seed")
    num_stanzas: int = Field(default=1, ge=1, le=5, description="Number of stanzas to generate")
    custom_pattern: list[int] | None = Field(
        default=None,
        description="Custom matra pattern per charan — only used when poem_form is 'custom'",
    )
    instructions: str = Field(
        default="", description="Additional stylistic or content instructions"
    )
    pronunciation_mode: Literal["orthographic", "phonetic", "manual"] = Field(
        default="orthographic", description="Pronunciation mode for meter validation (Hindi only)"
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v not in _SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{v}'. Supported: {sorted(_SUPPORTED_LANGUAGES)}"
            )
        return v

    @field_validator("poem_form")
    @classmethod
    def validate_poem_form(cls, v: str, info: Any) -> str:
        lang = (info.data or {}).get("language", "")
        allowed = _SUPPORTED_FORMS.get(lang, set())
        if allowed and v not in allowed:
            raise ValueError(f"Poem form '{v}' not supported for language '{lang}'.")
        return v


class GenerateResponse(BaseModel):
    """Response payload for POST /api/generate."""

    language: str = Field(..., description="BCP-47 language code used")
    poem_form: str = Field(..., description="Poem form that was generated")
    stanzas: list[list[GeneratedLine]] = Field(
        default_factory=list,
        description="Generated poem as a list of stanzas, each stanza a list of lines",
    )
    validation: PoemValidation = Field(..., description="Aggregate meter validation result")
    model_used: str = Field(default="", description="Gemini model that produced this poem")
    generation_note: str = Field(default="", description="Additional generation context")


# ---------------------------------------------------------------------------
# TTS Schemas
# ---------------------------------------------------------------------------


class TTSRequest(BaseModel):
    """Request payload for text-to-speech synthesis."""

    text: str = Field(..., min_length=1, description="Text to synthesize")
    language_code: str = Field(default="hi-IN", description="BCP-47 TTS language code")
    voice_name: str | None = Field(default=None, description="Optional TTS voice identifier")
    speaking_rate: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech rate multiplier")


class TTSResponse(BaseModel):
    """Response payload for text-to-speech synthesis."""

    audio_base64: str = Field(..., description="Base64-encoded audio bytes (WAV/MP3)")
    mime_type: str = Field(default="audio/wav", description="MIME type of the encoded audio")
    duration_seconds: float | None = Field(default=None, description="Approximate audio duration")


# ---------------------------------------------------------------------------
# Export Schemas
# ---------------------------------------------------------------------------


class ExportRequest(BaseModel):
    """Request payload for poem export."""

    text: str = Field(..., min_length=1, description="Poem text to export")
    format: Literal["pdf", "docx", "txt"] = Field(default="pdf", description="Export format")
    title: str = Field(default="", description="Optional poem title")
    author: str = Field(default="", description="Optional poet name")
    language: str = Field(default="hi", description="BCP-47 language code")


class ExportResponse(BaseModel):
    """Response payload for poem export."""

    file_base64: str = Field(..., description="Base64-encoded exported file bytes")
    mime_type: str = Field(..., description="MIME type of the exported file")
    filename: str = Field(..., description="Suggested download filename")


# ---------------------------------------------------------------------------
# Language Info Schema (API representation)
# ---------------------------------------------------------------------------


class LanguageInfo(BaseModel):
    """Public API representation of a supported language."""

    language_code: str = Field(..., description="BCP-47 language code")
    name: str = Field(..., description="English language name")
    native_name: str = Field(..., description="Language name in its own script")
    script: str = Field(..., description="Writing system name")
    direction: Literal["ltr", "rtl"] = Field(..., description="Text direction")
    meter_systems: list[str] = Field(default_factory=list)
    poem_forms: list[str] = Field(default_factory=list)
    scanner_available: bool = False
    rhyme_available: bool = False
    tts_status: Literal["supported", "experimental", "unsupported"] = "unsupported"
    export_available: bool = False
    generator_available: bool = False


# ---------------------------------------------------------------------------
# Urdu and Bengali Analysis Schemas
# ---------------------------------------------------------------------------


class UrduAnalyzeRequest(BaseModel):
    """Request payload for Urdu Arooz analysis."""

    text: str = Field(..., min_length=1, description="Urdu poetic line to analyze")
    bahr: str | None = Field(default=None, description="Optional target Bahr identifier")


class UrduAnalyzeResponse(BaseModel):
    """Response payload for Urdu Arooz analysis."""

    original_text: str
    normalized_text: str
    words: list[str]
    weight_pattern: str
    matched_bahr: str | None = None
    matched_bahr_name: str | None = None
    alternative_bahrs: list[dict[str, Any]] = Field(default_factory=list)
    arkan_mapping: list[str] = Field(default_factory=list)
    explanation: str
    confidence: float
    ambiguity_note: str = ""


class BengaliAnalyzeRequest(BaseModel):
    """Request payload for Bengali Chhanda analysis."""

    text: str = Field(..., min_length=1, description="Bengali poetic line to analyze")
    template: str | None = Field(default="payar", description="Bengali meter template name")


class BengaliAnalyzeResponse(BaseModel):
    """Response payload for Bengali Chhanda analysis."""

    original_text: str
    normalized_text: str
    aksharas: list[str]
    count_value: int
    count_unit: str
    template_name: str
    target_count: int
    difference: int
    status: str
    diagnostic_message: str
    system: str
