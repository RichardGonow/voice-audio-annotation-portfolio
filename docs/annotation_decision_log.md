# Annotation Decision Log

This document records the reasoning behind annotation decisions made in ambiguous or edge-case audio scenarios. Each entry follows the same format to ensure decisions are reproducible, auditable, and useful for inter-annotator calibration.

Use this log when:
- `annotation_confidence` is 3 or below
- `speech_clarity` is `unclear` or `partially_unclear`
- `recording_quality` is `poor` or `unusable`
- The audio contains overlapping speech or heavy disfluency
- Any label choice required non-trivial judgment

---

## Format

Each entry includes:
- **Case** — file and annotation index
- **Audio issue** — what made this annotation difficult
- **Annotation decision** — the labels chosen and why
- **Reasoning** — the specific judgment applied
- **Confidence score** — 1–5 (1 = very uncertain, 5 = fully confident)

---

## Case 1 — Accent Ambiguity

**Case:** `sample_001.wav`, annotation #1

**Audio issue:** The speaker uses a mixture of standard Mandarin phonology with occasional southwestern tonal features. Retroflex consonants are partially neutralized. It is unclear whether this is a southwestern regional accent or simply an informal speech style.

**Annotation decision:**
- `accent_region`: `southwestern_mandarin`
- `dialect_label`: `mandarin`
- `annotation_confidence`: 3
- `decision_note`: Retroflex neutralization and tonal contour suggest southwestern Mandarin, but speaker may be a standard Mandarin speaker in casual register. Labeled southwestern_mandarin pending second annotator review.

**Reasoning:** When accent features are present but not dominant, label the region that accounts for the most observed phonological deviations. If uncertain between two regions, choose the one with stronger acoustic evidence and note the alternative.

---

## Case 2 — Low Audio Clarity

**Case:** `sample_002.wav`, annotation #3

**Audio issue:** Recording shows consistent low-volume signal throughout the segment. Speaker is audible but requires concentration to follow. Some words in the middle of the utterance are only partially recoverable.

**Annotation decision:**
- `speech_clarity`: `partially_unclear`
- `recording_quality`: `poor`
- `quality_flag`: `poor`
- `transcript`: `我觉得这个方案[INAUDIBLE]，我们应该再考虑一下。`
- `annotation_confidence`: 2
- `decision_note`: Central portion of utterance (approx. 1.8s–2.5s) is below intelligibility threshold. Transcript around the gap is recoverable. Labeled poor rather than unusable because surrounding context is reliable.

**Reasoning:** Use `[INAUDIBLE]` only for the specific span that is unrecoverable. Avoid labeling the entire segment unusable if surrounding context is transcribable. Set `annotation_confidence` to 2 to require decision_note and trigger QA warning.

---

## Case 3 — Background Noise Assessment

**Case:** `sample_003.wav`, annotation #2

**Audio issue:** Intermittent background music is audible at low volume for the first half of the segment, then fades. The music does not contain lyrics. Speaker's voice remains clearly intelligible throughout.

**Annotation decision:**
- `noise_type`: `music`
- `background_noise_level`: `low`
- `speech_clarity`: `mostly_clear`
- `quality_flag`: `fair`
- `annotation_confidence`: 4
- `decision_note`: Background music is non-vocal and low intensity. Transcript is fully recoverable. Downgraded from good to fair to flag for downstream filtering.

**Reasoning:** Presence of any music warrants `noise_type: music` regardless of volume. `background_noise_level: low` reflects that the music does not impede transcription. `quality_flag: fair` rather than `good` because the noise may affect ASR model training even if it does not affect human transcription.

---

## Case 4 — Disfluency Annotation

**Case:** `sample_004.wav`, annotation #1

**Audio issue:** Speaker produces a clear false start followed by a filler word before completing the sentence. The disfluency is natural and does not indicate any audio quality issue.

**Annotation decision:**
- `transcript`: `我想，那个，我想说的是，这个方案可以优化。`
- `disfluency_present`: `yes`
- `disfluency_type`: `filler,false_start`
- `speech_clarity`: `clear`
- `annotation_confidence`: 5
- `decision_note`: (empty — high confidence, no ambiguity)

**Reasoning:** Disfluencies must be transcribed verbatim. "那个" functions as a filler. The initial "我想" that was abandoned constitutes a false start. Both are present, so `disfluency_type` lists both. High confidence because the speech is clear and the disfluency types are unambiguous.

---

## Case 5 — Overlapping Speech

**Case:** `sample_005.wav`, annotation #4

**Audio issue:** Two speakers talk simultaneously for approximately 1.5 seconds. Both voices are partially audible, but the primary speaker's voice is louder. The secondary speaker's content cannot be reliably transcribed.

**Annotation decision:**
- `noise_type`: `overlapping_speech`
- `overlap_speech`: `yes`
- `transcript`: `我现在不太方便[CROSSTALK]，等一下再说。`
- `speech_clarity`: `partially_unclear`
- `quality_flag`: `poor`
- `annotation_confidence`: 3
- `decision_note`: Primary speaker (SPEAKER_01) is dominant and transcribed. Secondary speaker is audible but content is indistinguishable. [CROSSTALK] inserted at overlap point. Segment flagged poor due to overlap duration.

**Reasoning:** When overlap occurs, transcribe only the dominant (louder/clearer) speaker. Insert `[CROSSTALK]` at the exact position where the overlap makes the primary speaker unclear. Set `overlap_speech: yes` regardless of whether the overlap affects transcription quality.

---

## Using This Log

Entries in this log should be referenced in `decision_note` fields of the exported JSON by case identifier. Example:

```json
{
  "decision_note": "See annotation_decision_log.md Case 3 for background noise assessment rationale."
}
```

New cases should be added when a novel type of ambiguity arises that is not covered by existing entries.
