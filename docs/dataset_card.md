# Dataset Card

## Dataset Overview

| Field | Value |
|-------|-------|
| Dataset name | Voice Audio Annotation Portfolio Dataset |
| Version | Stage 2 |
| Language | Mandarin Chinese (primary); English supported |
| Annotation tool | This repository (`app/main.py`) |
| Schema version | JSON Schema draft-07 (`data/schema/annotation_schema.json`) |

---

## Data Source

This dataset consists of audio files uploaded and annotated by the user through the local annotation tool. No external corpus is bundled with this repository.

**Intended sources for demonstration:**
- Self-recorded voice samples
- Publicly available speech samples (CC0 / public domain)
- Synthetic test audio generated for QA purposes

**Not included:**
- Third-party proprietary audio
- Audio with personal identifying information
- Scraped or bulk-downloaded data

---

## Data Scale

Scale varies by user. The tool supports annotation of any number of audio files stored in `data/annotations/`. The `reports/annotation_summary.py` script provides current counts at any time.

| Metric | Notes |
|--------|-------|
| Files | One JSON file per audio clip |
| Segments per file | Typically 2–20 per audio clip |
| Segment duration | Typically 1–30 seconds each |
| Total annotated duration | Depends on user's annotation session |

---

## Annotation Fields

| Field | Type | Description |
|-------|------|-------------|
| `audio_id` | string | Filename of the source audio (top-level, not per-segment) |
| `start_time` | float (s) | Segment start time in seconds |
| `end_time` | float (s) | Segment end time in seconds |
| `speaker` | string | Speaker identifier, format `SPEAKER_01`–`SPEAKER_99` |
| `transcript` | string | Verbatim transcription of spoken content |
| `intent` | enum | Communicative intent of the utterance |
| `emotion` | enum | Perceived emotional tone |
| `noise_type` | enum | Type of background interference |
| `quality_flag` | enum | Overall audio quality assessment |
| `notes` | string | Optional free-text annotator comments |

### Allowed Values

**intent:** `greeting` `question` `request` `complaint` `confirmation` `small_talk` `other`

**emotion:** `neutral` `happy` `angry` `sad` `anxious` `confused` `other`

**noise_type:** `none` `background_noise` `music` `overlapping_speech` `low_volume` `unclear` `other`

**quality_flag:** `good` `fair` `poor` `unusable`

---

## Applicable Tasks

This annotation format is designed to support:

- **ASR (Automatic Speech Recognition)** — transcripts with precise timestamps
- **Intent classification** — utterance-level intent labels for dialogue systems
- **Emotion / sentiment recognition** — segment-level emotion labels
- **Speaker diarization QA** — speaker ID with structured format
- **Audio quality filtering** — `quality_flag` for dataset cleaning pipelines
- **Noise robustness research** — `noise_type` for conditioning models on acoustic conditions

---

## Privacy and Limitations

- **No PII guarantee:** The tool does not enforce removal of personal information from transcripts. Annotators are responsible for anonymizing names, phone numbers, and other identifying content if required.
- **Single annotator:** All annotations in a session come from one annotator. Inter-annotator agreement metrics are not currently computed.
- **No ASR assistance:** Transcripts are entered entirely manually. There is no automatic transcription — accuracy depends entirely on the annotator.
- **Session-based:** Annotations persist only if saved via "Save to disk". Browser refresh without saving loses all session work.

---

## Not Suitable For

- Large-scale data collection without additional workflow controls
- Production ML training without review by a second annotator
- Legal or medical transcription requiring certified accuracy
- Any use case requiring speaker identity verification

---

## Annotation Guidelines

See `docs/labeling_guideline.md` for the full annotator reference guide and `docs/edge_cases.md` for handling ambiguous scenarios.
