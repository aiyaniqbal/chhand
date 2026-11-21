"""Lyric sheet export API endpoint."""

from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.export.lyric_sheet import ExportOptions, generate_lyric_sheet

router = APIRouter(tags=["Export"])


class ExportRequestPayload(BaseModel):
    """Payload for poem export."""

    lines: list[str] = Field(default_factory=list, description="Poetic lines to export")
    text: str | None = Field(
        default=None, description="Optional full poem text (split by newlines if lines empty)"
    )
    format: Literal["txt", "html"] = Field(
        default="txt", description="Export format: 'txt' or 'html'"
    )
    title: str = Field(default="", description="Poem title")
    author: str = Field(default="", description="Poet or pen name")
    language: str = Field(default="hi", description="BCP-47 language code: 'hi', 'ur', 'bn'")
    meter: str = Field(default="", description="Optional poetic meter name")
    author_note: str = Field(default="", description="Optional poet footnote")


@router.post("/export")
async def export_poem_endpoint(payload: ExportRequestPayload) -> Response:
    """
    Generate and download a professional lyric sheet in plain text (.txt) or print-ready HTML.
    """
    lines = payload.lines
    if not lines and payload.text:
        lines = [line.strip() for line in payload.text.split("\n") if line.strip()]

    if not lines:
        raise HTTPException(
            status_code=422,
            detail="Poem contains no lines to export.",
        )

    options = ExportOptions(
        title=payload.title,
        author=payload.author,
        language=payload.language,
        meter=payload.meter,
        author_note=payload.author_note,
        format=payload.format,
    )

    try:
        content, media_type, filename = generate_lyric_sheet(lines, options)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Export generation failed: {exc}",
        ) from exc

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }

    return Response(
        content=content,
        media_type=media_type,
        headers=headers,
    )
