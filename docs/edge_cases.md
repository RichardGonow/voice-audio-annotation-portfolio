# Edge Cases in Voice / Audio Annotation

This document covers common ambiguous situations and how to handle them consistently when annotating speech data.

---

## 1. Inaudible or Unclear Speech

**Situation:** A word or phrase cannot be reliably transcribed due to low volume, distortion, or mumbling.

**Rules:**
- Mark the affected word or phrase with `[inaudible]`.
- Do not guess or fabricate content.
- If the entire segment is unintelligible, use `[inaudible]` as the full transcript.
- Set `quality_flag` to `poor` or `unusable` depending on severity.

**Examples:**
```
"我想 [inaudible] 一下那个订单。"
"[inaudible]"
```

---

## 2. Overlapping Speech

**Situation:** Two or more speakers talk at the same time.

**Rules:**
- Create a separate annotation segment for each speaker if they can be distinguished.
- If speakers cannot be separated, annotate as a single segment with the dominant speaker.
- Set `noise_type` to `overlapping_speech`.
- Mark unclear words with `[inaudible]`.
- Overlapping time ranges are only valid across different speakers; within a single speaker track, segments must not overlap.

---

## 3. Background Music

**Situation:** Music plays throughout or during a segment.

**Rules:**
- Set `noise_type` to `music`.
- Transcribe only the speech; do not transcribe song lyrics unless they are clearly part of the speaker's utterance.
- If music severely degrades intelligibility, adjust `quality_flag` accordingly.

---

## 4. Filler Words and Discourse Markers

**Situation:** The speaker uses filler words such as "嗯", "啊", "那个", "就是", "uh", "um", "like".

**Rules:**
- Transcribe fillers verbatim — do not omit or clean them up.
- These are linguistically meaningful for prosody and fluency research.
- Do not mark them as errors or noise.

**Examples:**
```
"嗯，我想查一下，那个，订单状态。"
"Um, I'd like to, uh, check my order."
```

---

## 5. Stuttering and Repetitions

**Situation:** The speaker repeats a syllable, word, or phrase due to stuttering or self-correction.

**Rules:**
- Transcribe all repetitions verbatim using a hyphen for stuttered syllables.
- Do not normalize or merge repetitions.

**Examples:**
```
"我我我想确认一下。"
"I w-want to confirm the order."
```

---

## 6. Silent Segments

**Situation:** A segment contains no speech (pause, hold music, dead air).

**Rules:**
- Do not create an annotation for pure silence unless it is meaningful to the task (e.g., intentional pause in a dialogue).
- If annotating a silence, set `transcript` to `[silence]` and `quality_flag` to `unusable`.
- Avoid creating zero-length or near-zero-length segments (end_time must be > start_time).

---

## 7. Non-Verbal Sounds

**Situation:** The audio contains laughter, coughing, sighing, crying, throat-clearing, or other non-speech sounds produced by a speaker.

**Rules:**
- Transcribe non-verbal sounds in square brackets within the transcript.
- Include the surrounding speech in the same segment if the sound is brief.
- For extended non-verbal sounds, create a separate segment.

**Common tags:**

| Sound | Transcription |
|-------|--------------|
| Laughter | `[笑]` / `[laughter]` |
| Cough | `[咳嗽]` / `[cough]` |
| Sigh | `[叹气]` / `[sigh]` |
| Throat clear | `[清嗓]` / `[throat clear]` |
| Crying | `[哭泣]` / `[crying]` |

**Example:**
```
"这个问题真的很难 [叹气] 我也不知道怎么解决。"
```

---

## 8. Code-Switching (Mixed Languages)

**Situation:** The speaker switches between languages within a single utterance (e.g., Chinese + English).

**Rules:**
- Transcribe each language in its original script/alphabet.
- Do not translate or normalize to a single language.
- Note the language mix in the `notes` field if relevant.

**Example:**
```
"我们需要做一个 user research 来验证这个 assumption。"
```

---

## 9. Proper Nouns and Numbers

**Situation:** The speaker says a product name, person name, phone number, or order ID.

**Rules:**
- Transcribe verbatim as heard.
- For digit strings, write digits as spoken (e.g., "一二三四" not "1234" if spoken digit by digit).
- For spelled-out letters, transcribe as heard: "A B C" not "ABC".

---

## 10. Cropped or Cut-Off Speech

**Situation:** A segment begins or ends mid-sentence due to the audio boundary.

**Rules:**
- Transcribe only the audible portion.
- Use `[...]` at the cut point to indicate truncation.
- Set `notes` to explain if relevant.

**Examples:**
```
"[...] 所以我觉得这个方案是可行的。"
"我想问一下关于退款的 [...]"
```

---

## 11. Emotional Ambiguity

**Situation:** The speaker's emotion is not clearly identifiable from the audio alone.

**Rules:**
- Choose the most likely `emotion` based on acoustic cues (pitch, speed, tone) and content.
- When genuinely uncertain between two emotions, prefer the more neutral option.
- Use `notes` to record uncertainty: `"Possibly anxious or confused — tone ambiguous."`
- Do not mark every uncertain case as `other`; reserve `other` for emotions outside the defined set.
