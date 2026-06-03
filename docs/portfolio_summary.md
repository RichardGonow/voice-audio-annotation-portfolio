# Portfolio Summary

This document summarizes what this project demonstrates as a professional portfolio piece for AI data annotation, speech labeling, and AI trainer roles.

---

## What This Project Shows

### 1. Speech Data Annotation

The annotation interface captures all fields required for production-quality ASR and NLU training data:

- Precise timestamps (start/end in seconds)
- Speaker identification with a structured ID format
- Verbatim transcription
- Intent, emotion, noise type, and audio quality labels
- Free-text notes for edge cases

This mirrors the annotation schema used in real call-center, voice assistant, and dialogue system datasets.

---

### 2. Annotation Schema Design

`data/schema/annotation_schema.json` defines the data contract as JSON Schema draft-07, with:

- `$ref`-based separation of the file envelope from the per-segment definition
- Enum arrays for all categorical fields
- Type constraints for numeric fields
- `required` field lists

A machine-readable schema means any downstream ML pipeline can validate incoming data without reading docs.

---

### 3. Manual Labeling Workflow

The Streamlit UI (`app/main.py`) demonstrates a complete end-to-end labeling session:

1. Upload audio and play it back in-browser
2. Load an existing annotation file to continue work
3. Fill the structured form and submit
4. Review the annotation table, delete mistakes
5. Save to disk or download as JSON/CSV

This reflects the actual workflow of professional annotation platforms, implemented from scratch.

---

### 4. JSON and CSV Export

`app/export.py` produces two standard output formats:

- **JSON** — nested format suitable for ML pipeline ingestion and schema validation
- **CSV** — flat table with `audio_id` column for spreadsheet review and client delivery

Both formats carry the same `audio_id` field to maintain traceability to the source file.

---

### 5. Real-Time Validation

`app/validation.py:validate_new()` checks each annotation before it enters the list:

- `end_time > start_time`
- `transcript` non-empty
- `speaker` matches `SPEAKER_XX` regex
- All enum fields within allowed values
- No time overlap with existing annotations

Errors are surfaced immediately in the UI with field-level messages, exactly as a production annotation tool would behave.

---

### 6. Batch Quality Checking

`qa_report.py` provides a CLI QA pipeline:

- Single-file mode: `python qa_report.py file.json`
- Directory mode: `python qa_report.py data/annotations/` — checks all files and prints aggregate statistics
- Markdown export: `--markdown docs/qa_report.md` — produces a shareable QA report

The QA script imports the same `validate_annotations()` function used by the UI, ensuring the UI and CLI enforce identical rules. Rule changes propagate to both automatically.

---

### 7. Annotation Statistics

`reports/annotation_summary.py` reads all saved files and generates a Markdown report with:

- Total audio files and annotations
- Cumulative annotated duration
- Distribution of intents, emotions, noise types, and quality flags

This is the kind of dataset-level reporting expected when delivering labeled data to ML teams.

---

### 8. Documentation for Labeling Consistency

Three documentation artifacts ensure annotators apply labels consistently:

| Document | Purpose |
|----------|---------|
| `docs/labeling_guideline.md` | Full annotator reference: all fields, decision rules, acoustic cues, QA criteria |
| `docs/edge_cases.md` | 11 common ambiguous situations with explicit handling rules |
| `docs/dataset_card.md` | Dataset card describing source, scale, fields, tasks, and limitations |

Professional annotation projects live and die by documentation. These files demonstrate the ability to translate labeling decisions into written rules that scale across annotators.

---

## Skills Demonstrated

| Skill | Evidence |
|-------|---------|
| Speech data annotation | Structured 9-field schema covering ASR, NLU, and audio QA fields |
| Schema design | JSON Schema draft-07 with `$ref`, enums, and type constraints |
| Annotation tool development | Streamlit UI with real-time validation, save/load, and table management |
| Data export | JSON and CSV with consistent `audio_id` traceability |
| QA automation | CLI script reusing UI validation logic, supporting batch directory mode |
| Dataset reporting | Annotation statistics summary with label distributions |
| Labeling guidelines | Edge case documentation covering 11 real-world scenarios |
| Dataset documentation | Dataset card with source, scale, fields, tasks, and limitations |
| Python module design | Clean separation of UI, validation, and export logic |
