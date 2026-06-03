# Voice / Audio Annotation Labeling Guidelines

**Version:** 1.0  
**Project:** Voice Audio Annotation Portfolio  
**Target roles:** AI Data Annotator · Speech Data Labeling Specialist · AI Trainer

---

## 1. Project Goal

This project produces structured annotation data from raw voice recordings for use in AI/ML training pipelines. Annotated data supports tasks including:

- **Automatic Speech Recognition (ASR)** — transcript-based training
- **Intent classification** — spoken intent detection for dialogue systems
- **Emotion recognition** — speaker emotional state labeling
- **Audio quality filtering** — flagging segments unsuitable for model training
- **Speaker diarization** — identifying who speaks when

All annotations must be consistent, reproducible, and verifiable by the QA pipeline.

---

## 2. Annotation Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `audio_id` | Yes | string | Filename of the source audio (e.g. `call_001.wav`) |
| `start_time` | Yes | float (s) | Segment start, in seconds, 2 decimal places |
| `end_time` | Yes | float (s) | Segment end, in seconds; must be > `start_time` |
| `speaker` | Yes | string | Speaker ID in `SPEAKER_XX` format |
| `transcript` | Yes | string | Verbatim transcription, non-empty |
| `intent` | Yes | enum | Communicative intent of the utterance |
| `emotion` | Yes | enum | Perceived emotional tone of the speaker |
| `noise_type` | Yes | enum | Dominant background noise type |
| `quality_flag` | Yes | enum | Usability rating for AI training |
| `notes` | No | string | Free-text for edge cases or ambiguities |

---

## 3. Timestamp Rules

- **Start time**: mark the onset of the **first audible word**, not preceding silence.
- **End time**: mark the end of the **last audible word**, not trailing silence.
- Use **2 decimal places** (e.g. `3.50`, not `3.5`).
- Minimum segment duration: **0.5 seconds**.
- Segments for the same audio file **must not overlap**.
- If two speakers talk simultaneously, mark the segment with `noise_type: overlapping_speech` and transcribe only the foreground speaker.

---

## 4. Transcript Rules

- Transcribe **exactly** what is said. Do not paraphrase, summarize, or correct grammar.
- Include natural disfluencies: hesitations ("uh", "um"), false starts, self-corrections.
- Use standard punctuation appropriate to the utterance type:
  - Statements → `.`
  - Questions → `?`
  - Exclamations → `!`
- Special markers:
  - `[INAUDIBLE]` — speech is present but completely unintelligible
  - `[NOISE]` — a non-speech sound (cough, laugh, door slam) within the segment
  - `[CROSSTALK]` — overlapping speech makes the primary speaker unclear
- Do **not** include speaker labels (e.g. "SPEAKER_01:") inside the transcript field.
- Chinese, English, or mixed-language transcripts are all acceptable; match the actual spoken language.

---

## 5. Speaker Labeling Rules

- Format: `SPEAKER_XX` where `XX` is a **zero-padded two-digit number**.
  - Correct: `SPEAKER_01`, `SPEAKER_02`, `SPEAKER_10`
  - Incorrect: `speaker1`, `SPK01`, `Speaker_1`
- Assign IDs in **order of first appearance** in the audio file.
- Keep IDs consistent across all segments of the same recording.
- If the speaker cannot be identified: use `SPEAKER_00` and add a note.
- For a customer-service scenario, typical convention:
  - `SPEAKER_01` = customer
  - `SPEAKER_02` = agent

---

## 6. Intent Labels

Label the **primary communicative intent** of the utterance. If two intents apply equally, choose the one that best describes the speaker's goal.

| Label | Definition | Example |
|-------|------------|---------|
| `greeting` | Opening social phrase at the start of an interaction | "你好，有什么可以帮您的吗？" |
| `question` | Utterance seeking information; typically rising intonation or explicit question word | "我的订单什么时候发货？" |
| `request` | Asking someone to perform an action | "请帮我修改一下收货地址。" |
| `complaint` | Expressing dissatisfaction or reporting a problem | "这个产品有质量问题，我很不满意。" |
| `confirmation` | Affirming, agreeing, or providing requested information | "我的订单号是 123456。" |
| `small_talk` | Casual conversation not directly related to the task | "今天天气真好。" |
| `other` | Does not fit any category above; add a note explaining why | — |

---

## 7. Emotion Labels

Label the **speaker's emotional state** as perceived from prosody and intonation, **not** from the semantic content of the words.

| Label | Acoustic cues |
|-------|--------------|
| `neutral` | Even tone, moderate pace, no strong affect. **Use as default when uncertain.** |
| `happy` | Higher pitch, faster rate, upbeat energy, warm vocal quality |
| `angry` | Louder, clipped speech, raised pitch, tense articulation |
| `sad` | Slower pace, lower pitch, quieter, trailing off at end of phrases |
| `anxious` | Faster rate, higher pitch, more frequent hesitations, breathy quality |
| `confused` | Rising intonation at unexpected points, pauses mid-sentence, "um" fillers |
| `other` | Recognizably emotional but does not match the above; describe in `notes` |

**Rule**: When two emotions seem equally present (e.g. anxious and confused), choose the stronger one and note the ambiguity.

---

## 8. Noise Type Labels

Label the **dominant** background noise. If multiple noise sources are present, choose the most impactful one for speech recognition.

| Label | Description |
|-------|-------------|
| `none` | No audible background noise; clean recording |
| `background_noise` | General ambient sound (traffic, office hum, air conditioning) |
| `music` | Music playing in the background (with or without vocals) |
| `overlapping_speech` | One or more additional speakers audible simultaneously |
| `low_volume` | Speaker is too quiet; volume is below acceptable threshold |
| `unclear` | Audio is distorted, muffled, or otherwise degraded in an unclassifiable way |
| `other` | A noise not covered above; describe in `notes` |

---

## 9. Quality Flag Labels

Rate the overall **usability of the segment for AI model training**.

| Label | Criteria |
|-------|----------|
| `good` | Speech is clear and intelligible. Transcript confidence ≥ 95%. No significant noise. |
| `fair` | Minor noise or slight clipping. Transcript is reliable. Usable with caution. |
| `poor` | Significant noise, clipping, or overlap. Transcript may contain gaps or errors. |
| `unusable` | Speech is unintelligible or completely obscured. Do not use for training. |

---

## 10. Common Edge Cases

| Situation | Recommended action |
|-----------|-------------------|
| Speaker switches mid-segment | Split into two separate annotations |
| Two speakers fully overlapping | Mark `noise_type: overlapping_speech`; transcribe the dominant speaker; flag `quality_flag: poor` |
| Background music with lyrics | Mark `noise_type: music`; transcribe the speaker's voice only |
| Long silence mid-utterance (> 2 s) | Split into two segments at the silence |
| Laughter or cough within utterance | Insert `[NOISE]` at the position in the transcript |
| Completely inaudible segment | Transcript = `[INAUDIBLE]`; `quality_flag: unusable` |
| Mixed-language utterance | Transcribe as-is in the language spoken; do not translate |
| Child speaker | Add `"notes": "child speaker"` |
| Strong accent making recognition difficult | Lower `quality_flag` and add note; do not skip the segment |

---

## 11. QA Check Rules

All annotation files must pass the automated QA check before submission.

Run: `python qa_report.py <your_annotation.json>`

The following rules are enforced:

| Rule | Check |
|------|-------|
| Time order | `end_time > start_time` for every annotation |
| Non-empty transcript | `transcript` is not blank or whitespace-only |
| Speaker format | `speaker` matches `^SPEAKER_\d{2}$` |
| No overlaps | Adjacent segments in the same file do not overlap in time |
| Valid intent | `intent` is one of the 7 allowed values |
| Valid emotion | `emotion` is one of the 7 allowed values |
| Valid noise_type | `noise_type` is one of the 7 allowed values |
| Valid quality_flag | `quality_flag` is one of the 4 allowed values |

**Fix all QA errors before submitting the annotation file.**
