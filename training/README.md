# Chhand Fine-Tuning & Adaptation Architecture

This directory contains the dataset preparation, validation, evaluation, and supervised fine-tuning tools for creating language-adapted poetry models for Chhand.

---

## 1. Architectural Distinction

In Chhand, **model tuning** and **production inference** are strictly separated:

1. **Standard Inference**: Uses the official Google GenAI SDK (`google-genai`) with Google AI Studio API keys.
2. **Supervised Fine-Tuning**: Built for Google Cloud Gemini Enterprise / Vertex AI Agent Platform using Application Default Credentials (ADC) and Google Cloud Storage.
3. **Deterministic Scanners**: A fine-tuned model proposes creative verse, but **never certifies its own meter**. Deterministic Python engines (Hindi Chhand, Urdu Arooz, Bengali Chhanda) independently verify all output.

If Google Cloud tuning credentials are not configured, Chhand seamlessly falls back to the base Gemini foundation model (`gemini-3.8-flash`) through `app.llm.model_router`.

---

## 2. Dataset Structure

All records follow `training/schema.json`:

```json
{
  "language": "hi",
  "script": "Devanagari",
  "task": "meter_aware_poetry_rewrite",
  "input": {
    "original_text": "बड़ा भया तो क्या भया जैसे पेड़ खजूर बहुत",
    "meter": "doha",
    "target_pattern": [13, 11, 13, 11],
    "meaning": "Greatness without benefit to others is futile",
    "style": "natural poetic Hindi"
  },
  "expected_output": {
    "text": "बड़ा भया तो क्या भया जैसे पेड़ खजूर",
    "validation_status": "reviewed"
  },
  "provenance": {
    "author": "कबीर दास",
    "source": "कबीर ग्रंथावली (दोहा)",
    "license": "Public Domain"
  }
}
```

### Supported Languages & Datasets

- **Hindi (`training/datasets/hindi.jsonl`)**: Classical Doha and Chaupai from Kabir, Rahim, Tulsidas, and Surdas.
- **Urdu (`training/datasets/urdu.jsonl`)**: Classical Ghazal hemistichs scanned against Hazaj, Ramal, and Mutaqarib Bahrs from Mir, Ghalib, and Dard.
- **Bengali (`training/datasets/bengali.jsonl`)**: Classical Payar, Chaturdashpadi, and Matrabritta verses from Krittibas, Michael Madhusudan Dutt, and Rabindranath Tagore.
- **Validation (`training/validation/validation.jsonl`)**: Held-out split across all three languages.

---

## 3. Data Preparation & Validation Tools

### Validate Dataset
Validate schema compliance, missing fields, duplicates, and provenance:
```bash
python training/validate_dataset.py --path training/datasets/hindi.jsonl
python training/validate_dataset.py --path training/datasets/urdu.jsonl
python training/validate_dataset.py --path training/datasets/bengali.jsonl
python training/validate_dataset.py --path training/validation/validation.jsonl
```

### Prepare Dataset
Normalize Unicode scripts and deduplicate records:
```bash
python training/prepare_dataset.py --input raw_data.jsonl --output training/datasets/hindi.jsonl
```

### Offline Evaluation
Run deterministic meter scanners against target lines to measure meter accuracy:
```bash
python training/evaluate_model.py --path training/validation/validation.jsonl
```

---

## 4. Google Cloud Tuning Workflow

### Prerequisites
1. A Google Cloud Project with Vertex AI API enabled.
2. Google Cloud Storage bucket containing the training and validation JSONL files.
3. Authenticated credentials via `gcloud auth application-default login`.

### Dry-Run Validation (Default)
Validates configuration without incurring compute or billing:
```bash
python training/submit_tuning_job.py --train-uri gs://your-bucket/chhand/hindi.jsonl
```

### Live Job Submission
Requires explicit `--execute` flag and active GCP billing:
```bash
python training/submit_tuning_job.py \
  --train-uri gs://your-bucket/chhand/hindi.jsonl \
  --val-uri gs://your-bucket/chhand/validation.jsonl \
  --name chhand-hindi-doha-adapter-v1 \
  --execute
```

---

## 5. Model Routing in Application Runtime

When a tuned model is produced, set its resource name in `.env`:

```env
ENABLE_FINE_TUNED_MODEL=true
GEMINI_TUNED_HINDI_MODEL=projects/YOUR_PROJECT/locations/us-central1/models/YOUR_MODEL_ID
```

`app.llm.model_router.get_model_for_language(language)` will automatically route Hindi requests to the tuned endpoint while routing other languages to the base model.
