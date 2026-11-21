"""Print-ready HTML lyric sheet generator with native script typography."""

import html

from app.export.formatting import (
    clean_poem_title,
    format_author_line,
    format_date,
    group_lines_into_stanzas,
)


def generate_html_export(poem_lines: list[str], options: dict) -> str:
    """
    Generate self-contained, print-ready HTML for a lyric sheet.
    Includes Google Fonts and bidirectional typography (RTL for Urdu).
    """
    language = options.get("language", "hi")
    direction = "rtl" if language == "ur" else "ltr"
    title = clean_poem_title(options.get("title", ""))
    author = options.get("author", "").strip()
    meter = options.get("meter", "").strip()
    date_val = format_date(options.get("date"))
    author_note = options.get("author_note", "").strip()

    # Font definitions per language
    font_family_map = {
        "hi": "'Tiro Devanagari Hindi', 'Noto Sans Devanagari', serif",
        "ur": "'Noto Nastaliq Urdu', 'Noto Naskh Arabic', serif",
        "bn": "'Noto Sans Bengali', 'Tiro Bangla', serif",
    }
    font_family = font_family_map.get(language, "'IBM Plex Sans', sans-serif")

    stanzas = group_lines_into_stanzas(poem_lines, stanza_size=2)
    stanzas_html_parts: list[str] = []

    for stanza in stanzas:
        lines_html = "".join(
            f'<div class="verse-line">{html.escape(line)}</div>' for line in stanza
        )
        stanzas_html_parts.append(f'<div class="stanza">{lines_html}</div>')

    stanzas_html = "\n".join(stanzas_html_parts)

    meta_parts: list[str] = []
    if author:
        meta_parts.append(f'<div class="meta-author">{html.escape(author)}</div>')
    if meter:
        meta_parts.append(f'<div class="meta-meter">{html.escape(meter.capitalize())}</div>')
    meta_parts.append(f'<div class="meta-date">{html.escape(date_val)}</div>')
    meta_html = "\n".join(meta_parts)

    note_html = ""
    if author_note:
        note_html = f'<div class="author-note"><em>Note:</em> {html.escape(author_note)}</div>'

    attribution_html = ""
    if author:
        attribution_html = (
            f'<div class="author-attribution">{html.escape(format_author_line(author))}</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="{html.escape(language)}" dir="{direction}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} — Lyric Sheet</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=Noto+Nastaliq+Urdu:wght@400;600&family=Noto+Sans+Bengali:wght@400;600&family=Noto+Sans+Devanagari:wght@400;600&family=Tiro+Devanagari+Hindi&display=swap" rel="stylesheet">
  <style>
    @page {{
      size: A4 portrait;
      margin: 25mm 20mm 20mm 20mm;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: {font_family};
      background: #ffffff;
      color: #1a1a1a;
      line-height: 1.8;
      padding: 40px 20px;
    }}
    .sheet-container {{
      max-width: 650px;
      margin: 0 auto;
      text-align: center;
    }}
    header {{
      margin-bottom: 40px;
      padding-bottom: 20px;
      border-bottom: 1px solid #e0d8cc;
    }}
    h1.poem-title {{
      font-size: 28px;
      font-weight: 600;
      letter-spacing: 0.05em;
      margin-bottom: 12px;
      color: #1a2744;
    }}
    .meta-wrap {{
      font-size: 14px;
      color: #666666;
      display: flex;
      justify-content: center;
      gap: 20px;
      font-family: 'IBM Plex Sans', sans-serif;
    }}
    .poem-body {{
      margin: 30px 0;
      font-size: 20px;
    }}
    .stanza {{
      margin-bottom: 28px;
    }}
    .verse-line {{
      margin-bottom: 6px;
      min-height: 1.6em;
    }}
    footer {{
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #f0eae0;
      font-size: 14px;
      color: #666666;
    }}
    .author-attribution {{
      font-size: 16px;
      margin-top: 15px;
      font-weight: 500;
    }}
    .author-note {{
      font-size: 13px;
      font-style: italic;
      margin-top: 15px;
      color: #777777;
    }}
    @media print {{
      body {{
        padding: 0;
      }}
      .no-print {{
        display: none !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="sheet-container">
    <header>
      <h1 class="poem-title">{html.escape(title)}</h1>
      <div class="meta-wrap">
        {meta_html}
      </div>
    </header>

    <main class="poem-body">
      {stanzas_html}
    </main>

    <footer>
      {attribution_html}
      {note_html}
    </footer>
  </div>
</body>
</html>"""
