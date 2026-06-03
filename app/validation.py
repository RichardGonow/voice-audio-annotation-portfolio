import re

SPEAKER_PATTERN = re.compile(r"^SPEAKER_\d{2}$")

VALID_INTENTS = {"greeting", "question", "request", "complaint", "confirmation", "small_talk", "other"}
VALID_EMOTIONS = {"neutral", "happy", "angry", "sad", "anxious", "confused", "other"}
VALID_NOISE_TYPES = {"none", "background_noise", "music", "overlapping_speech", "low_volume", "unclear", "other"}
VALID_QUALITY_FLAGS = {"good", "fair", "poor", "unusable"}

_LABEL_RULES = [
    ("intent", VALID_INTENTS),
    ("emotion", VALID_EMOTIONS),
    ("noise_type", VALID_NOISE_TYPES),
    ("quality_flag", VALID_QUALITY_FLAGS),
]


def validate_annotations(annotations: list) -> list:
    """Validate a full annotation list. Returns list of error dicts with index."""
    errors = []

    for i, a in enumerate(annotations):
        s, e = a.get("start_time"), a.get("end_time")

        if s is not None and e is not None and e <= s:
            errors.append({
                "index": i, "field": "end_time",
                "message": f"end_time ({e}) must be greater than start_time ({s}).",
            })

        if not str(a.get("transcript", "")).strip():
            errors.append({"index": i, "field": "transcript", "message": "Transcript is empty."})

        spk = a.get("speaker", "")
        if spk and not SPEAKER_PATTERN.match(spk):
            errors.append({
                "index": i, "field": "speaker",
                "message": f"Speaker '{spk}' does not match SPEAKER_XX format (e.g. SPEAKER_01).",
            })

        for field, valid_set in _LABEL_RULES:
            val = a.get(field)
            if val and val not in valid_set:
                errors.append({
                    "index": i, "field": field,
                    "message": f"'{val}' is not a valid {field} value.",
                })

    # overlap check (sorted by start_time)
    indexed = sorted(enumerate(annotations), key=lambda x: x[1].get("start_time", 0))
    for j in range(len(indexed) - 1):
        i1, a1 = indexed[j]
        i2, a2 = indexed[j + 1]
        if a1.get("end_time", 0) > a2.get("start_time", 0):
            errors.append({
                "index": i2, "field": "start_time",
                "message": (
                    f"Annotation #{i2} overlaps annotation #{i1} "
                    f"({a1['start_time']}s–{a1['end_time']}s)."
                ),
            })

    return errors


def validate_new(annotation: dict, existing: list) -> list:
    """Validate a single new annotation against existing ones. Returns error dicts (no index)."""
    errors = []
    s = annotation.get("start_time")
    e = annotation.get("end_time")

    if s is not None and e is not None and e <= s:
        errors.append({"field": "end_time", "message": f"end_time ({e}s) must be greater than start_time ({s}s)."})

    if not str(annotation.get("transcript", "")).strip():
        errors.append({"field": "transcript", "message": "Transcript is empty."})

    spk = annotation.get("speaker", "")
    if spk and not SPEAKER_PATTERN.match(spk):
        errors.append({"field": "speaker", "message": f"Speaker '{spk}' does not match SPEAKER_XX format."})

    for field, valid_set in _LABEL_RULES:
        val = annotation.get(field)
        if val and val not in valid_set:
            errors.append({"field": field, "message": f"'{val}' is not a valid {field} value."})

    for i, a in enumerate(existing):
        if s < a.get("end_time", 0) and e > a.get("start_time", 0):
            errors.append({
                "field": "start_time",
                "message": f"Time overlap with annotation #{i} ({a['start_time']}s–{a['end_time']}s).",
            })

    return errors
