# Chhand (छंद)

> AI-Powered, Meter-Aware Hindi Poetry & Lyric Co-Writer

[![Tests](https://github.com/aiyan/chhand/actions/workflows/tests.yml/badge.svg)](https://github.com/aiyan/chhand/actions/workflows/tests.yml)
**Live Application:** Deployed on Vercel Serverless

---

## 1. Project Overview

**Chhand (छंद)** is a production-minded Hindi poetry and lyric co-writing studio built for poets, lyricists, song-writers, and computational linguists. It combines a rigorous, deterministic Devanagari meter engine based on classical Pingala Chhand Shastra with an AI-assisted rewrite and rhyming workflow.

### Core Engineering Principle
> **AI proposes. The deterministic engine verifies. The human decides.**
>
> The AI must never mark its own generated poetry as meter-correct. Every candidate must pass through the Python meter engine before it can be presented as a verified suggestion. The meter scanner functions completely independently without an LLM API key.

---

## 2. Problem Statement

Composing classical Hindi poetry in metered forms (such as *Doha* and *Chaupai*) requires strict adherence to matra counts (*मात्रा काल*):
- **Doha (दोहा)**: 4 charans structured as **13 | 11 | 13 | 11** matras.
- **Chaupai (चौपाई)**: 4 charans structured as **16 | 16 | 16 | 16** matras.

Large Language Models (LLMs) notoriously struggle with tokenization of Indic scripts: a single Devanagari akshara may span 3 to 6 sub-word tokens or bytes. Consequently, LLMs consistently miscount matras, hallucinate prosodic weights, and produce rhythmically broken verse when asked to generate metered poetry.

---

## 3. Proposed Solution

Chhand separates **creative generation** from **prosodic verification**:
1. **Deterministic Devanagari Engine**: Implements authentic Pingala Chhand Shastra rules—Unicode normalization, akshara segmentation, conjunct phonology, and laghu/guru weight calculations without probabilistic guesses.
2. **Interactive Scansion Studio**: Displays syllable-level scansion marks (`•` laghu, `—` guru, `|` caesura) directly beneath the writer's Devanagari text, with hairline visual indicators and instant error diagnosis.
3. **Generate-and-Verify AI Loop**: When a line breaks meter, the LLM proposes candidate rewrites that preserve semantic intent. Each candidate is independently scanned by the deterministic engine. Only candidates that achieve the exact target count are displayed.
4. **Phonetic Rhyme Assistant**: Offers dictionary-backed ending sound matches without requiring an LLM connection.

---

## 4. Target Users

- **Hindi Poets & Shayars**: Composing traditional Dohas, Chaupais, or custom matrik verse with exact rhythmic discipline.
- **Lyricists & Songwriters**: Crafting song verses and hooks that must fit strict musical time signatures and rhythmic cadences.
- **Students & Computational Linguists**: Learning or researching Devanagari prosody, syllable weights, and schwa phonology.
- **Content Creators**: Writing rhymed couplets and social poetry in authentic Devanagari.

---

## 5. Key Features

- **Devanagari Scansion Engine**: Unicode-aware segmentation of independent vowels, consonants, matras, halants, anusvara, visarga, and conjuncts.
- **Laghu/Guru Classification**: Calculates matra weights (1 or 2) per syllable with source character offset mapping.
- **Interactive Poems Studio**: Four-charan couplet editor, current vs. target matra totals, caesura dividers, and break highlighting.
- **Meter Library (`#meters`)**: Dedicated library with Doha, Chaupai, and Custom cards, interactive scansion detail modal with authentic verified poetry, and a Custom Meter Builder.
- **Rhyme Discovery Studio (`#rhymes`)**: Dedicated search workspace with exact and approximate phonetic matches, copy actions, "Use in poem" transition, and dictionary rhyme family cards (`-ूर`, `-ार`, `-ान`, etc.).
- **Deterministic AI Verification Loop**: Multi-candidate generation, rejection of incorrect candidates, retry caps, duplicate filtering, and accept/reject controls.
- **Zero-Dependency Frontend**: Responsive, lightweight HTML5, CSS3, and ES modules—no React, Vite, or node build dependencies required.
- **Offline Reliability**: Scanning and rhyming operate 100% locally without external API dependencies.

---

## 6. Architecture Diagram

```text
              CHHAND FRONTEND
              Poems / Meters / Rhymes
                       |
                       v
                  FastAPI API
                       |
          +------------+------------+
          |                         |
          v                         v
    METER ENGINE                AI ENGINE
    Devanagari NLP              LLM Provider
    Syllabification             Candidate Generation
    Laghu/Guru                         |
    Matra Counting                    v
    Meter Validation           Generated Candidates
          |                         |
          |                         v
          |                  METER VERIFICATION
          |                         |
          +------------+------------+
                       |
                       v
               VERIFIED RESULTS
                       |
                       v
                HUMAN APPROVAL
                  Accept / Reject
```

---

## 7. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, HTTPX, python-dotenv, Uvicorn
- **Frontend**: Vanilla ES6+ JavaScript, CSS3 (Custom Properties), Semantic HTML5
- **Typography**: Tiro Devanagari Hindi, IBM Plex Sans, IBM Plex Mono, Noto Sans Devanagari
- **Testing & Quality**: Pytest, Pytest-asyncio, Ruff (linting and formatting)
- **Deployment**: Vercel Serverless Functions (`api/index.py`) + Static Asset CDN

---

## 8. System Workflow

```text
Writer Enters Hindi Verse in Devanagari
                  │
                  ▼
   Unicode Normalization (NFC + Pos Map)
                  │
                  ▼
      Akshara Syllable Segmentation
                  │
                  ▼
     Laghu (1) / Guru (2) Assignment
                  │
                  ▼
       Meter Template Comparison
    (Doha 13|11, Chaupai 16, Custom)
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
Matched Exact           Meter Violation (Over / Under)
  [✓ In Meter]                │
                              ▼
                    Poet Requests "Fit This Meter"
                              │
                              ▼
                    LLM Proposes Candidates
                              │
                              ▼
               Deterministic Verification Engine
                  ┌───────────┴───────────┐
                  ▼                       ▼
           Violates Meter          Passes Exact Count
             [REJECT]                    │
                                         ▼
                                Deduplicate & Rank
                                         │
                                         ▼
                               Verified Suggestions
                                         │
                                         ▼
                              Poet Accepts or Rejects
```

---

## 9. Meter Engine Explanation

The engine in `app/meter/` implements authentic Pingala Chhand Shastra rules:

### Devanagari Grapheme Classification
- **Independent Vowels**: Short (`अ`, `इ`, `उ`, `ऋ`, `ऌ`) and Long (`आ`, `ई`, `ऊ`, `ए`, `ऐ`, `ओ`, `औ`).
- **Dependent Vowel Signs (Matras)**: Short (`ि`, `ु`, `ृ`) and Long (`ा`, `ी`, `ू`, `े`, `ै`, `ो`, `ौ`).
- **Modifiers**: Virama/Halant (`्`), Anusvara (`ं`), Chandrabindu (`ँ`), Visarga (`ः`), Nukta (`़`).

### Matra Weight Assignment
| Sound Type | Weight (मात्रा) | Justification |
|---|:---:|---|
| Short Vowel (ह्रस्व) | 1 (Laghu `•`) | Natural short vocalic duration |
| Long Vowel (दीर्घ) | 2 (Guru `—`) | Doubled vocalic duration |
| Short Vowel with Chandrabindu (अनुनासिक) | 1 (Laghu `•`) | Vocalic nasalization without coda closure |
| Short Vowel with Anusvara (अनुस्वार) | 2 (Guru `—`) | Consonantal nasal closure (अंग्/अम्) |
| Short Vowel with Visarga (विसर्ग) | 2 (Guru `—`) | Post-vocalic aspirate closure |
| Short Vowel closed by Coda Consonant | 2 (Guru `—`) | Halant coda consonant closes syllable |
| Short Vowel preceding Consonant Cluster | 2 (Guru `—`) | Conjunct onset lengthens preceding syllable (*संयोगे गुरु*) |

---

## 10. Generate-and-Verify Workflow

1. **Extraction**: The system isolates the broken charan along with its active target count, current syllable breakdown, and diagnosis.
2. **Contextual Prompting**: The LLM is instructed to generate natural Hindi lines in Devanagari that preserve emotional tone, meaning, and optional rhyme requirements.
3. **Independent Verification**: Every candidate returned by the LLM is scanned by `app.meter.scanner.scan_line()`.
4. **Rejection Filter**:
   - Candidates whose total matras do not equal the target are rejected immediately.
   - Candidates with unresolved phonetic ambiguities in phonetic mode are rejected.
   - Duplicate suggestions are removed.
5. **Retry Loop**: If fewer than the requested verified suggestions are found, the engine retries up to `MAX_RETRIES` (default: 3) with temperature variation.
6. **Delivery**: The user receives only verified lines with explicit `verified_status: true`.

---

## 11. API Endpoints

Once the application is running, OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

### Core Endpoints

#### `GET /api/health`
Checks backend and meter engine status without disclosing credentials.
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "meter_engine": "online",
  "llm_configured": false,
  "environment": "development"
}
```

#### `POST /api/analyze`
Scans charans according to the selected meter template or custom pattern.
```json
{
  "meter": "doha",
  "charans": [
    "मन का दीपक जब जले",
    "मिटे अँधेरा दूर"
  ],
  "pronunciation_mode": "orthographic"
}
```

#### `POST /api/rewrite`
Generates candidate lines and verifies them against the deterministic meter engine.
```json
{
  "original_line": "साथ रहेगा फिर नूर",
  "target_matra_count": 11,
  "selected_meter": "doha",
  "charan_index": 1,
  "instructions": "Keep natural tone",
  "rhyme_requirement": "दूर"
}
```

#### `POST /api/rhyme`
Extracts phonetic rhyme tail and finds exact and approximate Hindi matches from the dictionary.
```json
{
  "word": "नूर",
  "limit": 10
}
```

#### `GET /api/rhyme/families`
Returns all dictionary ending families with word counts and sample word chips.
```json
{
  "total_families": 16,
  "families": [
    {
      "ending": "-ूर",
      "count": 10,
      "sample": ["दूर", "नूर", "ज़रूर", "मशहूर"]
    }
  ]
}
```

---

## 12. Local Installation

```bash
# 1. Clone repository
git clone https://github.com/aiyan/chhand.git
cd chhand

# 2. Create virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements-dev.txt
```

---

## 13. Local Setup

### One-Click Runners
- **Windows (Command Prompt / Explorer)**: Double-click or run `run.bat`.
- **Windows (PowerShell)**: Run `.\run.ps1`.
- **Linux / macOS**: Run `./scripts/dev.sh`.

### Manual Launch
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000` in any modern web browser.

---

## 14. Environment Variables

Create `.env` by copying `.env.example`:

```env
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-2.5-flash
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
MAX_RETRIES=3
LLM_TIMEOUT_SECONDS=25
```

> **Note:** The application functions fully offline without an API key. Meter scanning, diagnostics, custom builder, and rhyme dictionary search require zero credentials. Only AI rewrites require an LLM key.

---

## 15. Test Commands

```bash
# Run complete automated test suite
python -m pytest

# Run linter
python -m ruff check .

# Run formatter check
python -m ruff format --check .
```

---

## 16. Deployment Steps (Vercel)

The repository includes a production Vercel configuration (`vercel.json`):
1. **Serverless Entry**: `api/index.py` routes `/api/*` requests to FastAPI.
2. **Static Asset Serving**: Root static files are served directly from `public/`.
3. **Deploy via Vercel CLI**:
   ```bash
   npm i -g vercel
   vercel
   ```
4. **Environment Variables on Vercel Dashboard**:
   Add `LLM_API_KEY`, `LLM_MODEL`, and `LLM_BASE_URL` in the project settings if AI rewriting is desired in production.

---

## 17. Data Sources & Benchmark Datasets

The repository includes curated, public-domain Hindi poetry benchmark datasets in `data/`:
- **`sample_dohas.json`**: 17 Dohas by Kabir Das (*Kabir Granthavali*), Rahim (*Rahim Dohavali*), Bihari Lal (*Bihari Satsai*), and Tulsidas.
- **`sample_chaupais.json`**: 6 Chaupais from Tulsidas's *Ramcharitmanas* (Bal Kanda) and *Hanuman Chalisa*.
- **`broken_examples.json`**: 10 deliberately broken lines covering overcounts, undercounts, truncated words, and unsupported scripts with expected diagnostics.
- **`rhyme_words.txt`**: 200+ curated classical Hindi poetry words indexed by phonetic rhyme tail.

---

## 18. Linguistic Assumptions & Rules

1. **Orthographic vs. Phonetic Mode**:
   - **Orthographic Mode (Default)**: Follows classical written Pingala Chhand rules where inherent final schwas carry 1 matra unless closed by halant.
   - **Phonetic Mode**: Applies conservative schwa deletion for modern colloquial recitation and flags pronunciation ambiguities.
2. **Visarga Handling**: Visarga (`ः`) closes the preceding short vowel, imparting Guru (2 matras) weight.
3. **Anunasika vs. Anusvara**: Chandrabindu (`ँ`) is treated as pure vocalic nasalization (Laghu 1), while Anusvara (`ं`) is treated as a consonant coda closure (Guru 2).
4. **Conjunct Onset**: Word-initial conjuncts (e.g., `क्या`, `प्रेम`, `स्थान`) do not lengthen non-existent preceding vowels; mid-word conjuncts lengthen the preceding syllable (*संयोगे गुरु*).

---

## 19. Current Limitations

- **Dialectal Metric Shortening**: In historical Awadhi and Braj poetry, poets occasionally shortened long vowels (ह्रस्वीकरण) or lengthened short vowels (दीर्घीकरण) to fit musical meter. Manual pronunciation overrides (`pronunciation_overrides`) are provided for these exceptions.
- **Urdu & Bengali**: Urdu Aruz meters and Bengali payar are intentionally scheduled for the finale build.

---

## 20. Built-Now vs. Finale Roadmap

| Feature | MVP (Built Now) | Live Finale (Nov 21) |
|---|:---:|:---:|
| Hindi Devanagari Meter Scanner | ✅ Complete | Enhanced |
| Doha (13 \| 11) & Chaupai (16 \| 16) | ✅ Complete | Enhanced |
| Interactive Custom Meter Builder | ✅ Complete | Enhanced |
| AI Generate-and-Verify Loop | ✅ Complete | Multi-model |
| Hindi Rhyme Discovery Studio | ✅ Complete | Expanded Dictionary |
| Accept / Reject Suggestion Controls | ✅ Complete | History & Versioning |
| Urdu Aruz Metrical Engine | ⏳ Finale | ✅ Built for Finale |
| Bengali Script & Payar Support | ⏳ Finale | ✅ Built for Finale |
| Text-to-Speech (TTS) Recitation | ⏳ Finale | ✅ Built for Finale |
| Scansion Sheet PDF / Lyric Export | ⏳ Finale | ✅ Built for Finale |
| Fine-tuned LoRA Model Swap-in | ⏳ Finale | ✅ Built for Finale |

---

## License

MIT License. Copyright (c) 2026 Chhand Contributors.
