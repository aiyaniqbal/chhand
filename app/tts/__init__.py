"""Text-to-Speech recitation package using Gemini."""

from app.tts.audio import pcm_to_wav, validate_wav, wav_duration_seconds
from app.tts.gemini import get_available_voices, get_recitation_styles, synthesize_line
from app.tts.languages import (
    SUPPORTED_LANGUAGES,
    get_tts_lang_code,
    get_tts_status,
    is_tts_supported,
)

__all__ = [
    "SUPPORTED_LANGUAGES",
    "get_available_voices",
    "get_recitation_styles",
    "get_tts_lang_code",
    "get_tts_status",
    "is_tts_supported",
    "pcm_to_wav",
    "synthesize_line",
    "validate_wav",
    "wav_duration_seconds",
]
