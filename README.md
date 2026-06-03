# Voice / Audio Annotation Portfolio

A local audio annotation tool built with Python and Streamlit, demonstrating a complete professional speech data labeling workflow. Built as a portfolio project targeting **AI Data Annotation**, **Speech Data Labeling**, and **AI Trainer** roles.

---

## 1. Project Overview

This tool simulates the annotation pipeline used in real AI/ML projects for:

- **ASR (Automatic Speech Recognition)** training data preparation
- **Intent classification** for dialogue and call-center systems
- **Emotion recognition** model training
- **Audio quality control** for large-scale speech datasets

Every component — the annotation interface, export formats, schema definition, labeling guidelines, validation, and QA scripts — reflects the actual deliverables expected in professional annotation work.

---

## 2. Current Features

| Feature | Detail |
|---------|--------|
| Audio upload & playback | Upload `.wav` / `.mp3`; play in-browser via Streamlit |
| Structured annotation form | 9 fields per segment: timestamps, speaker, transcript, intent, emotion, noise type, quality, notes |
| Real-time validation | Catches format errors (speaker ID, time order, overlap) before adding |
| Annotation table | View, review, and delete individual entries in the current session |
| Save to database | Writes JSON to `data_set/json_database/` and CSV to `data_set/csv_database/` |
| Load existing annotations | Upload a `.annotations.json` file or select from previously saved files |
| Browser download | Download JSON or CSV directly to your machine |
| Single-file QA | CLI validates any annotation JSON file and prints errors by field |
| JSON Schema | Machine-readable field contract at `data/schema/annotation_schema.json` |
| Labeling guidelines | Full annotator guide at `docs/labeling_guideline.md` |

---

## 3. Project Structure

```
voice-audio-annotation-portfolio/           ← outer project root
├── data_set/
│   ├── json_database/                      ← JSON files saved from the UI
│   └── csv_database/                       ← CSV files saved from the UI
│
└── voice-audio-annotation-portfolio/       ← application root
    ├── app/
    │   ├── main.py                         # Streamlit UI — entry point
    │   ├── export.py                       # Export, save, and path-resolution logic
    │   └── validation.py                   # Annotation validation (shared by UI and QA)
    ├── data/
    │   ├── annotations/                    # Legacy save directory (Save to data/annotations)
    │   └── schema/
    │       └── annotation_schema.json      # JSON Schema draft-07
    ├── docs/
    │   ├── labeling_guideline.md
    │   ├── edge_cases.md
    │   ├── portfolio_summary.md
    │   └── dataset_card.md
    ├── examples/
    │   ├── sample_annotation.json          # 3-segment demo (1 intentional error)
    │   └── sample_annotation.csv
    ├── reports/
    │   └── annotation_summary.py
    ├── qa_report.py                        # CLI QA check script
    ├── requirements.txt
    └── README.md
```

---

## 4. Installation

```bash
pip install -r requirements.txt
```

Requirements: Python 3.10+, `streamlit`, `pandas`.

---

## 5. Running the Application

```bash
streamlit run app/main.py
```

The browser opens automatically at `http://localhost:8501`.

---

## 6. Annotation Workflow

1. **Section 1 — Upload Audio** — drag and drop a `.wav` or `.mp3` file. The in-browser player appears immediately. The `audio_id` is auto-filled from the filename and can be edited.
2. **Section 2 — Load Existing Annotations** — upload a `.annotations.json` file or pick from the saved-files dropdown to resume a previous session.
3. **Section 3 — Add Annotation** — fill timestamps, speaker ID, transcript, and select labels from dropdowns. Click **Add Annotation**. The entry is validated before being added.
4. Repeat step 3 for each speech segment in the audio.
5. **Section 4 — Save or Export** — save to the database, download to your browser, or clear the session.

---

## 7. JSON Export

Two options are available in Section 4:

**Save JSON to Database** — writes to `data_set/json_database/` on the server:

```
data_set/json_database/R20250925-152105.WAV.annotations.json
```

**Browser Download JSON** — downloads to your local machine via the browser.

Example JSON output:

```json
{
  "audio_id": "sample_001.wav",
  "annotations": [
    {
      "start_time": 0.5,
      "end_time": 3.2,
      "speaker": "SPEAKER_01",
      "transcript": "你好，我想查询一下我的订单状态。",
      "intent": "question",
      "emotion": "neutral",
      "noise_type": "none",
      "quality_flag": "good",
      "notes": ""
    }
  ]
}
```

Encoding: UTF-8, `ensure_ascii=False` — Chinese and other non-ASCII characters are stored as-is.

---

## 8. CSV Export

**Save CSV to Database** — writes to `data_set/csv_database/` on the server:

```
data_set/csv_database/R20250925-152105.WAV.annotations.csv
```

**Browser Download CSV** — downloads to your local machine via the browser.

Encoding: UTF-8-sig (with BOM) — opens correctly in Excel without garbled Chinese characters.

Each row contains one annotation segment with `audio_id` as the first column.

---

## 9. Database Storage

Saved files are stored outside the application directory so they persist independently of the codebase:

```
D:\Ai\Project\voice-audio-annotation-portfolio\
└── data_set\
    ├── json_database\      ← all .annotations.json files
    └── csv_database\       ← all .annotations.csv files
```

File naming format:

```
{audio_id}.annotations.json
{audio_id}.annotations.csv
```

The `data_set` directory is located automatically at startup using path resolution from `app/main.py`. If the directory does not exist, it is created automatically.

If a file with the same name already exists, it is overwritten and the UI displays: `Existing file overwritten.`

---

## 10. QA Validation

### Single file

```bash
python qa_report.py data_set/json_database/example.annotations.json
```

Sample output (file with one error):

```
Voice Annotation QA Report
==========================

File: data_set/json_database/example.annotations.json
audio_id: sample_001.wav
Total annotations: 3
Errors: 1

  [ERROR] annotation #1 - speaker: Speaker 'speaker1' does not match SPEAKER_XX format (e.g. SPEAKER_01).
```

Exit code `0` = all checks passed. Exit code `1` = errors found.

### Batch check (entire directory)

```bash
python qa_report.py data_set/json_database/
```

### Generate a Markdown QA report

```bash
python qa_report.py data_set/json_database/ --markdown docs/qa_report.md
```

### Validation rules

- `end_time` must be greater than `start_time`
- `transcript` must not be empty
- `speaker` must match `SPEAKER_XX` format (e.g. `SPEAKER_01`)
- `intent`, `emotion`, `noise_type`, `quality_flag` must be within the allowed value sets
- No time overlap between annotations

---

## 11. Labeling Schema

Each annotation segment contains the following fields:

| Field | Type | Description | Allowed Values |
|-------|------|-------------|----------------|
| `start_time` | float (s) | Segment start time | ≥ 0.0 |
| `end_time` | float (s) | Segment end time | > `start_time` |
| `speaker` | string | Speaker identifier | `SPEAKER_01` … `SPEAKER_99` |
| `transcript` | string | Verbatim speech content | Non-empty |
| `intent` | enum | Communicative intent | `greeting` `question` `request` `complaint` `confirmation` `small_talk` `other` |
| `emotion` | enum | Perceived emotional tone | `neutral` `happy` `angry` `sad` `anxious` `confused` `other` |
| `noise_type` | enum | Background interference type | `none` `background_noise` `music` `overlapping_speech` `low_volume` `unclear` `other` |
| `quality_flag` | enum | Overall audio quality | `good` `fair` `poor` `unusable` |
| `notes` | string | Annotator comments | Optional free text |

The schema is also defined as JSON Schema draft-07 at `data/schema/annotation_schema.json` for machine-readable validation.

---

## 12. Project Highlights

**Speech Data Annotation** — A structured 9-field annotation schema covering the core requirements of ASR, intent classification, emotion recognition, and audio quality datasets.

**Annotation Schema Design** — `annotation_schema.json` (JSON Schema draft-07) defines the data contract explicitly. Any downstream ML pipeline can validate ingested files against it without reading documentation.

**Quality Assurance** — `qa_report.py` imports the same `validate_annotations()` function used by the UI. Rule changes in `validation.py` propagate to both the form and the QA CLI automatically, with no divergence possible.

**Batch Processing Ready** — The QA script accepts a directory path and checks all `.json` files in one run, printing per-file errors and aggregate statistics. Output can be written to a Markdown report.

**Streamlit UI** — The complete annotation lifecycle — upload → label → validate → save → load → QA — is covered in a single local tool with no database or cloud dependency.

---

## 13. Roadmap

### Stage 1 — Completed

- [x] Audio upload and in-browser playback
- [x] 9-field structured annotation form
- [x] Real-time validation (speaker format, time order, overlap, empty transcript)
- [x] JSON and CSV export (browser download)
- [x] Save to `data_set/json_database/` and `data_set/csv_database/`
- [x] Load existing annotations from file or saved dropdown
- [x] Delete annotation by index
- [x] Single-file QA CLI (`qa_report.py`)
- [x] JSON Schema draft-07 (`data/schema/annotation_schema.json`)
- [x] Labeling guidelines (`docs/labeling_guideline.md`)

### Stage 2 — Planned

- [ ] Annotation Management — edit existing entries without deleting and re-adding
- [ ] Batch QA — directory-level QA with aggregate pass/fail statistics
- [ ] Annotation Statistics — label distribution report across all saved files
- [ ] Dataset Card — formal dataset documentation (source, scale, fields, tasks, limitations)
- [ ] Edge Case Documentation — annotator guide for inaudible speech, overlaps, non-verbal sounds

---

## Tech Stack

- Python 3.10+
- [Streamlit](https://streamlit.io/) — annotation UI
- [pandas](https://pandas.pydata.org/) — tabular display and CSV export

> **Note:** `examples/sample_annotation.json` contains one intentional format error
> (`"speaker": "speaker1"` instead of `"SPEAKER_02"`) to demonstrate QA detection capability.
