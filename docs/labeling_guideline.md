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

---

## 12. Accent and Dialect Annotation

### `accent_region`

Label the speaker's regional speech variety based on phonological features (tonal contours, consonant articulation, vowel quality). Do not infer from content or topic.

| Label | When to use |
|-------|-------------|
| `standard_mandarin` | Neutral Putonghua with no strong regional features |
| `northern_mandarin` | Beijing or northern China features (erhua, light 4th tone) |
| `northeastern_mandarin` | Dongbei characteristics (flat tones, specific vowel mergers) |
| `southwestern_mandarin` | Sichuan/Yunnan area (retroflex neutralization, tonal differences) |
| `cantonese_accent` | L1 Cantonese speaker using Mandarin (tonal substitutions, final consonants) |
| `taiwan_mandarin` | Taiwan-style Mandarin (light tones, specific vocabulary, rising 3rd tone) |
| `singapore_mandarin` | Singapore Mandarin (contact features, code-switching patterns) |
| `mixed_accent` | Clear features from two or more regions, not assignable to one |
| `unknown` | Cannot determine with confidence; use as default when uncertain |

**Common confusion:** `southwestern_mandarin` vs `standard_mandarin` — retroflex neutralization (zh/ch/sh → z/c/s) is the primary differentiator. If only one or two features are present, prefer `standard_mandarin` and note the observation.

### `dialect_label`

Label the **language variety or dialect** being spoken in the segment. This field captures what language system is being used, not just accent features.

| Label | When to use |
|-------|-------------|
| `mandarin` | Standard Mandarin / Putonghua |
| `cantonese` | Yue Chinese (广东话 / 粤语) |
| `hokkien` | Min Nan / Hokkien (闽南话) |
| `hakka` | Hakka Chinese (客家话) |
| `shanghainese_wu` | Wu Chinese including Shanghainese |
| `sichuanese` | Sichuan dialect (川话) |
| `taiwanese_mandarin` | Mandarin as spoken in Taiwan (distinct from Standard Mandarin) |
| `singapore_mandarin` | Singapore Mandarin (Singaporean variety) |
| `mixed` | Speaker switches between two dialects/languages mid-segment |
| `unknown` | Cannot identify with confidence |

**Common confusion:** `mandarin` vs `taiwanese_mandarin` — label `taiwanese_mandarin` only if Taiwanese-specific lexical items or tonal patterns are clearly present. When in doubt, use `mandarin`.

---

## 13. Audio Quality Assessment

### `speech_clarity`

Rate the **intelligibility of the speech** independent of recording equipment quality.

| Label | Criteria |
|-------|----------|
| `clear` | All words are easily intelligible. No effort required from listener. |
| `mostly_clear` | Occasional word requires replay. Overall meaning fully recoverable. |
| `partially_unclear` | Portions require replay or remain uncertain. Transcript contains `[INAUDIBLE]`. |
| `unclear` | Most of the speech is unintelligible. Transcript cannot be reliably produced. |

### `background_noise_level`

Rate the **intensity of background noise** relative to the speaker's voice.

| Label | Criteria |
|-------|----------|
| `none` | No background noise detected |
| `low` | Noise is present but clearly below speech level. Does not impede transcription. |
| `medium` | Noise is at a level that requires focus. May cause occasional transcription uncertainty. |
| `high` | Noise approaches or exceeds speech level. Transcription is significantly impaired. |

### `recording_quality`

Rate the **overall technical quality of the recording**.

| Label | Criteria |
|-------|----------|
| `studio` | Professional quality. No noise, clipping, or artifacts. |
| `good` | Clean consumer-grade recording. Minor imperfections do not affect usability. |
| `acceptable` | Noticeable issues (slight noise, mild compression). Usable for training with caution. |
| `poor` | Significant technical issues. Transcript may contain errors. Flagged for review. |
| `unusable` | Recording is too degraded to produce a reliable transcript. |

**Note:** `recording_quality` assesses the equipment and environment. `speech_clarity` assesses the speaker. A quiet speaker in a studio may have `recording_quality: studio` but `speech_clarity: partially_unclear`.

---

## 14. Prosody Annotation

### `speaking_rate`

Label the **perceived speed** of speech delivery.

| Label | When to use |
|-------|-------------|
| `slow` | Noticeably deliberate pace; pauses between most phrases |
| `normal` | Conversational speed; typical for the language variety |
| `fast` | Rapid speech; words may run together; compressed vowels |
| `variable` | Rate changes significantly within the segment |

### `intonation`

Label the **dominant intonation pattern** of the segment.

| Label | When to use |
|-------|-------------|
| `flat` | Monotone delivery; little pitch variation |
| `rising` | Sentence ends on rising pitch (questions, uncertainty, continuation) |
| `falling` | Sentence ends on falling pitch (statements, commands, finality) |
| `expressive` | Wide pitch range; animated, emphatic delivery |
| `variable` | Intonation pattern shifts within the segment; use for longer turns |

### `speech_energy`

Label the **perceived loudness and vocal effort** of the speaker.

| Label | When to use |
|-------|-------------|
| `low` | Quiet or whispered; requires volume boost to hear clearly |
| `medium` | Normal conversational volume |
| `high` | Loud or emphatic; shouting, heightened emotion |
| `variable` | Energy level shifts within the segment |

**Common confusion:** `speech_energy: high` vs `emotion: angry` — energy describes acoustic output; emotion describes affective state. A calm lecturer may have `high` energy without being `angry`.

---

## 15. Disfluency Annotation

### `disfluency_present`

- `yes` — any of the disfluency types listed below are audible in the segment
- `no` — speech is fluent throughout

### `disfluency_type`

When `disfluency_present: yes`, specify all applicable types as a comma-separated string.

| Type | Description | Example |
|------|-------------|---------|
| `filler` | Non-lexical filler sounds | "嗯", "那个", "就是", "uh", "um" |
| `repetition` | Exact or near-exact repetition of a word or phrase | "我我我想说" |
| `self_correction` | Speaker repairs an error mid-utterance | "他昨天，上周去了北京" |
| `hesitation` | Pause or prolonged sound indicating uncertainty | "我想……去" |
| `false_start` | Utterance abandoned before completion | "我觉——我认为这样不对" |
| `none` | No disfluency (only when `disfluency_present: no`) |

**Rule:** If `disfluency_present: yes`, at least one type other than `none` must be listed. The QA check will flag `disfluency_type: none` when `disfluency_present: yes`.

**Transcript rule:** All disfluencies must appear verbatim in the transcript. Do not clean or remove them.

---

## 16. Overlap Speech Annotation

### `overlap_speech`

- `yes` — a second speaker's voice is audible simultaneously with the primary speaker at any point during the segment
- `no` — only one speaker is audible throughout

**When `overlap_speech: yes`:**
- Transcribe only the **dominant (foreground) speaker**
- Insert `[CROSSTALK]` in the transcript where the overlap makes the primary speaker unclear
- Set `noise_type: overlapping_speech`
- Lower `quality_flag` and `speech_clarity` accordingly

**Example:**
```
"我想跟你说[CROSSTALK]，这个问题很重要。"
```

---

## 17. Annotation Confidence

### `annotation_confidence`

Rate your personal confidence that all labels in this annotation are correct.

| Score | Meaning |
|-------|---------|
| 5 | Fully confident. Audio is clear, all labels are unambiguous. |
| 4 | Mostly confident. One minor label may be debatable. |
| 3 | Moderate uncertainty. At least one label required judgment. |
| 2 | Low confidence. Multiple labels are uncertain. **decision_note required.** |
| 1 | Very uncertain. Annotation is a best guess. **decision_note required.** |

**QA rule:** If `annotation_confidence ≤ 2`, the `decision_note` field must not be empty. The QA script will report this as an error.

---

## 18. Decision Notes

### `decision_note`

Free-text field for recording the reasoning behind non-obvious annotation decisions.

**When to fill:**
- `annotation_confidence` is 3 or below
- `speech_clarity` is `unclear` (QA will issue a warning if empty)
- `recording_quality` is `poor` or `unusable` (QA will issue a warning if empty)
- Any label could reasonably be argued either way
- A novel edge case not covered in this guideline

**Format guidance:**
- State what was uncertain and what evidence led to the decision
- Keep under 2–3 sentences
- Reference `docs/annotation_decision_log.md` for known case types

**Example:**
```
"Retroflex neutralization suggests southwestern accent, but speaker may be casual register standard Mandarin. Labeled southwestern_mandarin pending second review."
```
