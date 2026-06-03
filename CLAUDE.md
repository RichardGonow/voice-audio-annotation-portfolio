# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Commands

```bash
# Launch the annotation UI
streamlit run app/main.py

# Run QA check — single file
python qa_report.py data_set/json_database/<file>.annotations.json

# Run QA check — entire directory
python qa_report.py data_set/json_database/

# Generate Markdown QA report
python qa_report.py data_set/json_database/ --markdown docs/qa_report.md

# Install dependencies
pip install -r requirements.txt
```

---

# Project

voice-audio-annotation-portfolio

# Goal

Build a portfolio-grade speech/audio annotation tool for AI data annotation and speech labeling workflows.

# Current Status

Stage 1 Completed

Implemented:

- Audio playback
- Manual annotation
- JSON export
- CSV export
- JSON database save
- CSV database save
- Validation module
- QA report generation
- Streamlit UI

# Dataset Storage

JSON:

```
data_set/json_database/
```

CSV:

```
data_set/csv_database/
```

The `data_set/` directory lives one level above the application root (outer project directory). Path resolution in `app/export.py:find_dataset_root()` walks up from `app/` to locate or create it automatically.

# Annotation Fields

- `audio_id` — filename of the source audio (top-level envelope field)
- `start_time` — segment start in seconds (float)
- `end_time` — segment end in seconds (float)
- `speaker` — speaker identifier, format `SPEAKER_XX`
- `transcript` — verbatim speech content (required)
- `intent` — communicative intent label
- `emotion` — perceived emotional tone label
- `noise_type` — background interference type label
- `quality_flag` — overall audio quality label
- `notes` — optional free-text annotator comment

# Validation Rules

- `start_time` < `end_time`
- `transcript` required (non-empty)
- `speaker` format: `SPEAKER_XX` (e.g. `SPEAKER_01`)
- `intent`, `emotion`, `noise_type`, `quality_flag` must be within allowed value sets
- Overlap detection: no two annotations may share overlapping time ranges

Two entry points, same rules:
- `validate_new(annotation, existing)` — used by the UI for real-time per-entry feedback
- `validate_annotations(list)` — used by `qa_report.py` for batch file validation

# Allowed Label Values

Changes to any allowed-value set must be updated in three places to stay consistent:

| Location | Purpose |
|----------|---------|
| `app/validation.py` — `VALID_*` constants | Runtime validation (UI + QA script) |
| `app/main.py` — `INTENTS / EMOTIONS / NOISE_TYPES / QUALITY_FLAGS` | Dropdown options in the form |
| `data/schema/annotation_schema.json` — `enum` arrays | Machine-readable schema |

# Architecture

Single-page Streamlit app. All UI logic in `app/main.py`; shared modules in `app/`.

### Data flow

1. User uploads audio → `st.audio()` plays in-browser (no server-side audio processing).
2. User fills the annotation form → `app/validation.py:validate_new()` checks the entry before appending to `st.session_state.annotations`.
3. Save buttons call `app/export.py:save_annotations_json()` / `save_annotations_csv()`, which write to `data_set/json_database/` and `data_set/csv_database/`.
4. Browser download buttons call `app/export.py:annotations_to_json()` / `annotations_to_csv()` and return bytes to the browser.
5. `qa_report.py` reads a saved JSON file, calls `app/validation.py:validate_annotations()`, and prints the report.

### Error format

`validate_new` returns `[{"field": str, "message": str}]` — no index, entry not yet in list.
`validate_annotations` returns `[{"index": int, "field": str, "message": str}]` — 0-based index, 1-based display.

# Coding Guidelines

- Use `pathlib` for all file paths — no hardcoded backslash strings
- Keep Streamlit frontend simple — no custom components or JavaScript
- No database
- No authentication
- No cloud deployment yet
- No automatic speech recognition (Whisper or similar)
- No waveform visualization (deferred)
- Preserve compatibility with `qa_report.py` — JSON output format must not change
- Changes to validation rules must update `validation.py`, `main.py` dropdowns, and `annotation_schema.json`

# Next Development Stage

Stage 2

Goals:

- Annotation management (edit existing entries in-place)
- Load existing annotations from file or dropdown
- Delete annotations by index
- Batch QA across all files in a directory
- Annotation statistics (label distribution report)
- Dataset card documentation
- Portfolio documentation (edge cases, schema guide)

# Important Notes

This project is intended as a portfolio for:

- Speech Data Annotation
- Audio Labeling
- AI Trainer
- Data Quality Assurance
- LLM Data Operations

Future additions should prioritize annotation workflow quality over model training. Do not add ML model inference, ASR, or speaker diarization without explicit instruction.
