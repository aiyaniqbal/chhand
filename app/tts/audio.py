"""Audio processing utilities for WAV and PCM validation and conversion."""

import io
import wave


def validate_wav(data: bytes) -> bool:
    """Check if the provided byte sequence contains a valid RIFF/WAVE header."""
    if not data or len(data) < 44:
        return False
    if not data.startswith(b"RIFF"):
        return False
    if data[8:12] != b"WAVE":
        return False
    try:
        with wave.open(io.BytesIO(data), "rb") as wf:
            return wf.getnchannels() > 0 and wf.getframerate() > 0
    except Exception:
        return False


def wav_duration_seconds(data: bytes) -> float:
    """Calculate the duration of a valid WAV byte sequence in seconds."""
    if not validate_wav(data):
        return 0.0
    try:
        with wave.open(io.BytesIO(data), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return round(frames / float(rate), 2)
    except Exception:
        return 0.0


def pcm_to_wav(
    pcm: bytes,
    sample_rate: int = 24000,
    channels: int = 1,
    sampwidth: int = 2,
) -> bytes:
    """
    Wrap raw signed 16-bit PCM bytes into a standard RIFF/WAV container.
    Default parameters conform to Gemini 3.8 Flash TTS standard (24kHz, mono, 16-bit).
    """
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)
    return buf.getvalue()
