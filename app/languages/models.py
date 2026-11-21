"""Pydantic models for language capability information."""

from typing import Literal

from pydantic import BaseModel, Field


class LanguageCapability(BaseModel):
    """Full capability descriptor for a supported language."""

    language_code: str = Field(..., description="BCP-47 language code (e.g. 'hi', 'ur', 'bn')")
    name: str = Field(..., description="English name of the language")
    native_name: str = Field(..., description="Language name written in its own script")
    script: str = Field(..., description="Writing system name (e.g. 'Devanagari')")
    direction: Literal["ltr", "rtl"] = Field(..., description="Text direction")
    meter_systems: list[str] = Field(
        default_factory=list, description="Supported prosodic / meter system names"
    )
    poem_forms: list[str] = Field(
        default_factory=list, description="Supported poem form identifiers"
    )
    scanner_available: bool = Field(
        default=False, description="True when a deterministic meter scanner exists"
    )
    rhyme_available: bool = Field(
        default=False, description="True when a rhyme suggester is available"
    )
    tts_status: Literal["supported", "experimental", "unsupported"] = Field(
        default="unsupported", description="TTS readiness level"
    )
    tts_lang_code: str = Field(default="", description="BCP-47 TTS voice language code")
    export_available: bool = Field(
        default=False, description="True when export (PDF/DOCX) is supported"
    )
    generator_available: bool = Field(
        default=False, description="True when AI poetry generation is available"
    )
