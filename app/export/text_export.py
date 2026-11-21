"""Plain text lyric sheet generation."""

from app.export.formatting import (
    clean_poem_title,
    format_author_line,
    format_date,
    group_lines_into_stanzas,
)


def generate_text_export(poem_lines: list[str], options: dict) -> str:
    """
    Format poetry lines into a publication-style plain text lyric sheet.
    """
    title = clean_poem_title(options.get("title", ""))
    author = options.get("author", "").strip()
    meter = options.get("meter", "").strip()
    date_val = format_date(options.get("date"))
    author_note = options.get("author_note", "").strip()

    output_lines: list[str] = []

    # Header
    output_lines.append(title.upper())
    output_lines.append("=" * len(title))
    if author:
        output_lines.append(f"By {author}")
    if meter:
        output_lines.append(f"Meter: {meter.capitalize()}")
    output_lines.append(f"Date: {date_val}")
    output_lines.append("")
    output_lines.append("-" * 40)
    output_lines.append("")

    # Body stanzas
    stanzas = group_lines_into_stanzas(poem_lines, stanza_size=2)
    for stanza in stanzas:
        for line in stanza:
            output_lines.append(line)
        output_lines.append("")

    # Footer
    if author:
        output_lines.append(format_author_line(author))
    if author_note:
        output_lines.append("")
        output_lines.append(f"Note: {author_note}")

    return "\n".join(output_lines).strip() + "\n"
