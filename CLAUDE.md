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

# Generate annotation statistics report
python reports/annotation_statistics.py

# Install dependencies
pip install -r requirements.txt
```

---

# Project

voice-audio-annotation-portfolio

# Goal

Build a portfolio-grade speech/audio annotation tool for multilingual audio annotation, speech data labeling, and AI tutor roles.

# Current Status

Stage 3A Complete

## Dataset

- 21 audio files
- 21 annotations
- Approximately 19 minutes total duration
- Self-recorded Mandarin Chinese speech

## Stage 3A (Complete)

- Collected 21 self-recorded audio files
- Completed 21 annotations across all files
- Validated full annotation workflow end-to-end
- Portfolio dataset finalized and ready

## Stage 1 (Complete)

- Audio playback
- Manual annotation (9 core fields)
- JSON export and CSV export
- Local database save (data_set/json_database/, data_set/csv_database/)
- validation.py
- qa_report.py
- Streamlit UI
- JSON Schema draft-07

## Stage 2 (Complete)

- Accent annotation (accent_region, 9 labels)
- Dialect annotation (dialect_label, 10 labels)
- Audio quality fields (speech_clarity, background_noise_level, recording_quality)
- Prosody fields (speaking_rate, intonation, speech_energy)
- Disfluency fields (disfluency_present, disfluency_type)
- Overlap speech flag
- Annotation confidence score (1–5)
- Decision notes field
- validation.py: errors + warnings + cross-field rules
- qa_report.py: errors + warnings, batch mode, Markdown output
- reports/annotation_statistics.py
- docs/annotation_decision_log.md
- docs/labeling_guideline.md updated (18 sections)

# Dataset Storage

JSON:

```
data_set/json_database/
```

CSV:

```
data_set/csv_database/
```

The `data_set/` directory lives one level above the application root (outer project). Path resolution in `app/export.py:find_dataset_root()` walks up from `app/` to locate or create it automatically.

# Annotation Fields

## Core Fields

- `audio_id` — filename of the source audio (top-level envelope field)
- `start_time` — segment start in seconds (float)
- `end_time` — segment end in seconds (float)
- `speaker` — speaker identifier, format `SPEAKER_XX`
- `transcript` — verbatim speech content (required)
- `intent` — communicative intent label
- `emotion` — perceived emotional tone label
- `noise_type` — background interference type label
- `quality_flag` — overall audio quality label
- `notes` — optional free-text comment

## Advanced Fields (Stage 2)

- `accent_region` — regional accent (9 values, default: unknown)
- `dialect_label` — language/dialect variety (10 values, default: mandarin)
- `speech_clarity` — intelligibility (4 values, default: clear)
- `background_noise_level` — noise intensity (4 values, default: none)
- `recording_quality` — technical quality (5 values, default: good)
- `speaking_rate` — pace of speech (4 values, default: normal)
- `intonation` — pitch pattern (5 values, default: variable)
- `speech_energy` — vocal effort (4 values, default: medium)
- `disfluency_present` — yes/no (default: no)
- `disfluency_type` — comma-separated string (default: none)
- `overlap_speech` — yes/no (default: no)
- `annotation_confidence` — integer 1–5 (default: 4)
- `decision_note` — free-text reasoning (default: empty)

# Validation Rules

## Errors (block annotation)

- `start_time` < `end_time`
- `transcript` required (non-empty)
- `speaker` format: `SPEAKER_XX`
- All enum fields within allowed value sets
- `annotation_confidence` must be integer 1–5
- `disfluency_present: yes` → `disfluency_type` must include a non-`none` type
- `annotation_confidence ≤ 2` → `decision_note` must not be empty
- No overlapping time ranges between annotations

## Warnings (noted, do not block)

- `speech_clarity: unclear` without a `decision_note`
- `recording_quality: poor` or `unusable` without a `decision_note`

# Allowed Label Values

Changes to any allowed-value set must be updated in three places:

| Location | Purpose |
|----------|---------|
| `app/validation.py` — `VALID_*` constants | Runtime validation |
| `app/main.py` — label lists | Dropdown options |
| `data/schema/annotation_schema.json` — `enum` arrays | Machine-readable schema |

# Architecture

Single-page Streamlit app. All UI logic in `app/main.py`; shared modules in `app/`.

### Data flow

1. User uploads audio → `st.audio()` plays in-browser.
2. User fills form → `validate_new()` checks entry before appending to `st.session_state.annotations`. Returns `{"errors": [...], "warnings": [...]}`.
3. Save buttons → `app/export.py:save_annotations_json()` / `save_annotations_csv()` write to `data_set/`.
4. Browser download buttons → `annotations_to_json()` / `annotations_to_csv()` return bytes to browser.
5. `qa_report.py` → `validate_annotations()` → prints errors and warnings.

### Error format

`validate_new` returns `{"errors": [...], "warnings": [...]}` — no `index` key.
`validate_annotations` returns `{"errors": [...], "warnings": [...]}` — items include `index` (0-based).

# Coding Guidelines

- Use `pathlib` for all file paths — no hardcoded backslash strings
- Keep Streamlit frontend simple — no custom components or JavaScript injection
- No database (SQLite, PostgreSQL, etc.)
- No authentication or login system
- **Do not add automatic speech recognition (Whisper or similar) yet**
- **Do not add Whisper yet**
- No waveform visualization yet (deferred to Stage 3)
- No cloud deployment yet
- Preserve compatibility with `qa_report.py` — JSON output format must not change
- Changes to validation rules must update `validation.py`, `main.py` label lists, and `annotation_schema.json`
- **Prioritize annotation quality, schema design, QA, and documentation**
- **This project should remain portfolio-oriented**

# Future Ideas (Optional)

- Annotation statistics automation
- Edge case collection
- Inter-annotator agreement experiments
- Subtitle export (SRT/WebVTT)

These are optional portfolio enhancements and are not required for project completion.

# Important Notes

This project is intended as a portfolio for:

- Speech Data Annotation
- Multilingual Audio Labeling
- AI Trainer
- Data Quality Assurance
- LLM / AI Tutor Data Operations

Future additions should prioritize annotation workflow quality, schema depth, and documentation clarity over model training integration. Do not add ML model inference, ASR, or speaker diarization without explicit instruction.
