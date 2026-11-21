"""Lyric sheet orchestrator returning plain text or HTML."""

from dataclasses import dataclass
from typing import Literal

from app.export.formatting import safe_filename
from app.export.html_export import generate_html_export
from app.export.text_export import generate_text_export


@dataclass
class ExportOptions:
    """Options for lyric sheet generation."""

    title: str = ""
    author: str = ""
    language: str = "hi"
    meter: str = ""
    date: str = ""
    include_meter_pattern: bool = False
    include_analysis_notes: bool = False
    include_rhyme_notes: bool = False
    author_note: str = ""
    format: Literal["txt", "html"] = "txt"


def generate_lyric_sheet(
    poem_lines: list[str],
    options: ExportOptions,
) -> tuple[str, str, str]:
    """
    Generate exported lyric sheet content, MIME type, and suggested filename.
    Returns: (content_string, media_type, suggested_filename)
    """
    opts_dict = {
        "title": options.title,
        "author": options.author,
        "language": options.language,
        "meter": options.meter,
        "date": options.date,
        "author_note": options.author_note,
        "include_meter_pattern": options.include_meter_pattern,
        "include_analysis_notes": options.include_analysis_notes,
    }

    if options.format == "html":
        content = generate_html_export(poem_lines, opts_dict)
        media_type = "text/html; charset=utf-8"
        filename = safe_filename(options.title or "poem", options.language, "html")
    else:
        content = generate_text_export(poem_lines, opts_dict)
        media_type = "text/plain; charset=utf-8"
        filename = safe_filename(options.title or "poem", options.language, "txt")

    return content, media_type, filename
