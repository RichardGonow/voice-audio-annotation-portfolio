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

| Metric | Value |
|--------|-------|
| Total audio files | 21 |
| Total annotations | 21 |
| Total duration | ~19 minutes |
| Primary language | Mandarin Chinese |
| Audio source | Self-recorded speech |

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
| `accent_region` | enum | Regional accent label (9 values) |
| `dialect_label` | enum | Language/dialect variety (10 values) |
| `speech_clarity` | enum | Intelligibility assessment (4 values) |
| `background_noise_level` | enum | Noise intensity (4 values) |
| `recording_quality` | enum | Technical recording quality (5 values) |
| `speaking_rate` | enum | Pace of speech (4 values) |
| `intonation` | enum | Pitch pattern (5 values) |
| `speech_energy` | enum | Vocal effort level (4 values) |
| `disfluency_present` | enum | Whether disfluency is present (`yes` / `no`) |
| `disfluency_type` | string | Comma-separated disfluency types |
| `overlap_speech` | enum | Whether simultaneous speech occurs (`yes` / `no`) |
| `annotation_confidence` | integer | Annotator confidence score (1–5) |
| `decision_note` | string | Free-text reasoning for ambiguous decisions |

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
- **Accent annotation** — regional accent labeling for Mandarin speech varieties
- **Dialect annotation** — language/dialect classification across Chinese speech varieties
- **Audio QA** — structured quality assessment at segment level
- **Speech quality evaluation** — clarity, noise level, and recording quality scoring
- **Prosody annotation** — speaking rate, intonation, and speech energy labeling
- **Disfluency annotation** — detection and classification of speech disfluencies
- **Human annotation workflows** — demonstrates a complete professional annotation lifecycle
- **AI training data curation** — confidence scoring and decision notes for data quality operations

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

## Portfolio Context

This dataset was created as part of the Voice / Audio Annotation Portfolio project.

The project demonstrates:

- Audio annotation workflows
- Speech data labeling
- Annotation quality assurance
- Structured schema design
- Documentation and QA processes

Target roles:

- AI Data Annotator
- Audio Annotation Specialist
- Speech Data Labeler
- AI Trainer
- Data Quality Operations

---

## Annotation Guidelines

See `docs/labeling_guideline.md` for the full annotator reference guide and `docs/edge_cases.md` for handling ambiguous scenarios.

---

## Related Documents

- `docs/labeling_guideline.md`
- `docs/annotation_decision_log.md`
