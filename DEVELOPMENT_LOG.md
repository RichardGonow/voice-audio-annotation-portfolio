# Development Log

---

## Stage 1 MVP

**Date:** 2026-06-03

**Completed:**

- Streamlit UI
- Audio playback
- Annotation form
- JSON export
- CSV export
- Validation module
- QA report
- Local database storage

**Issues Encountered:**

- Browser download path cannot be controlled
- Switched to local database save mechanism

**Current Status:** Stage 1 Complete

---

## Stage 2: Audio Tutor Portfolio Upgrade

**Date:** 2026-06-05

**Completed:**

- Accent annotation (`accent_region`, 9 regional labels)
- Dialect annotation (`dialect_label`, 10 language/dialect labels)
- Audio quality assessment (`speech_clarity`, `background_noise_level`, `recording_quality`)
- Prosody annotation (`speaking_rate`, `intonation`, `speech_energy`)
- Disfluency annotation (`disfluency_present`, `disfluency_type`)
- Overlap speech annotation (`overlap_speech`)
- Confidence score (`annotation_confidence`, slider 1–5)
- Decision notes (`decision_note`, free text)
- `validation.py` refactored: errors + warnings + cross-field rules
- `qa_report.py` updated: warnings support, batch mode, Markdown output
- `reports/annotation_statistics.py` added
- `docs/annotation_decision_log.md` added (5 decision examples)
- `docs/labeling_guideline.md` extended to 18 sections
- `README.md` fully updated for Stage 2
- `CLAUDE.md` updated with Stage 2 field list and coding rules

**Current Status:** Stage 2 Complete

---

## Stage 3A: Portfolio Dataset Collection

**Date:** 2026-06-07

**Completed:**

- Collected 21 audio recordings (self-recorded Mandarin speech)
- Completed 21 annotations across all audio files
- Approximately 19 minutes of annotated speech
- Validated annotation workflow end-to-end
- Finalized portfolio dataset

**Current Status:** Portfolio-ready
