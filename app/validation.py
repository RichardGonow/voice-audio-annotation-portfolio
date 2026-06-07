import re

SPEAKER_PATTERN = re.compile(r"^SPEAKER_\d{2}$")

VALID_INTENTS = {"greeting", "question", "request", "complaint", "confirmation", "small_talk", "other"}
VALID_EMOTIONS = {"neutral", "happy", "angry", "sad", "anxious", "confused", "other"}
VALID_NOISE_TYPES = {"none", "background_noise", "music", "overlapping_speech", "low_volume", "unclear", "other"}
VALID_QUALITY_FLAGS = {"good", "fair", "poor", "unusable"}

VALID_ACCENT_REGIONS = {
    "standard_mandarin", "northern_mandarin", "northeastern_mandarin",
    "middle_mandarin", "southwestern_mandarin", "cantonese_accent",
    "taiwan_mandarin", "singapore_mandarin", "mixed_accent",
    "unknown", "user_defined",
}
VALID_DIALECT_LABELS = {
    "mandarin", "cantonese", "hokkien", "hakka", "shanghainese_wu",
    "sichuanese", "taiwanese_mandarin", "singapore_mandarin", "mixed",
    "unknown", "user_defined",
}

# Fields that accept free-form custom values in addition to the known enum.
# Unknown values produce a warning rather than an error.
_USER_DEFINED_FIELDS = {"accent_region", "dialect_label"}
VALID_SPEECH_CLARITY = {"clear", "mostly_clear", "partially_unclear", "unclear"}
VALID_BACKGROUND_NOISE_LEVELS = {"none", "low", "medium", "high"}
VALID_RECORDING_QUALITY = {"studio", "good", "acceptable", "poor", "unusable"}
VALID_SPEAKING_RATES = {"slow", "normal", "fast", "variable"}
VALID_INTONATIONS = {"flat", "rising", "falling", "expressive", "variable"}
VALID_SPEECH_ENERGY = {"low", "medium", "high", "variable"}
VALID_DISFLUENCY_PRESENT = {"yes", "no"}
VALID_OVERLAP_SPEECH = {"yes", "no"}

_LABEL_RULES = [
    ("intent",                 VALID_INTENTS),
    ("emotion",                VALID_EMOTIONS),
    ("noise_type",             VALID_NOISE_TYPES),
    ("quality_flag",           VALID_QUALITY_FLAGS),
    ("accent_region",          VALID_ACCENT_REGIONS),
    ("dialect_label",          VALID_DIALECT_LABELS),
    ("speech_clarity",         VALID_SPEECH_CLARITY),
    ("background_noise_level", VALID_BACKGROUND_NOISE_LEVELS),
    ("recording_quality",      VALID_RECORDING_QUALITY),
    ("speaking_rate",          VALID_SPEAKING_RATES),
    ("intonation",             VALID_INTONATIONS),
    ("speech_energy",          VALID_SPEECH_ENERGY),
    ("disfluency_present",     VALID_DISFLUENCY_PRESENT),
    ("overlap_speech",         VALID_OVERLAP_SPEECH),
]


def _make(field: str, message: str, index: int | None) -> dict:
    d = {"field": field, "message": message}
    if index is not None:
        d = {"index": index, **d}
    return d


def _validate_single(a: dict, index: int | None) -> tuple[list, list]:
    """Validate one annotation. Returns (errors, warnings).

    index=None → no 'index' key in results (used by validate_new).
    index=int  → 'index' key included (used by validate_annotations).
    """
    errors, warnings = [], []
    e = lambda f, m: errors.append(_make(f, m, index))
    w = lambda f, m: warnings.append(_make(f, m, index))

    # ── Core field checks ─────────────────────────────────────────────────────
    s = a.get("start_time")
    end = a.get("end_time")
    if s is not None and end is not None and end <= s:
        e("end_time", f"end_time ({end}) must be greater than start_time ({s}).")

    if not str(a.get("transcript", "")).strip():
        e("transcript", "Transcript is empty.")

    spk = a.get("speaker", "")
    if spk and not SPEAKER_PATTERN.match(spk):
        e("speaker", f"Speaker '{spk}' does not match SPEAKER_XX format (e.g. SPEAKER_01).")

    for field, valid_set in _LABEL_RULES:
        val = a.get(field)
        if val and val not in valid_set:
            if field in _USER_DEFINED_FIELDS:
                w(field, f"'{val}' is a custom {field} value — verify it is correct.")
            else:
                e(field, f"'{val}' is not a valid {field} value.")

    # ── annotation_confidence range ───────────────────────────────────────────
    conf = a.get("annotation_confidence")
    conf_int = None
    if conf is not None:
        try:
            conf_int = int(conf)
            if not (1 <= conf_int <= 5):
                raise ValueError
        except (ValueError, TypeError):
            e("annotation_confidence",
              f"annotation_confidence must be an integer 1–5, got {conf!r}.")
            conf_int = None

    # ── Cross-field: disfluency_present=yes → disfluency_type ≠ none ─────────
    disf_present = a.get("disfluency_present")
    disf_type = str(a.get("disfluency_type", "none"))
    if disf_present == "yes":
        types = [t.strip() for t in disf_type.split(",") if t.strip()]
        if not types or all(t == "none" for t in types):
            e("disfluency_type",
              "disfluency_present is 'yes' but disfluency_type is 'none'. "
              "Specify at least one disfluency type.")

    # ── Cross-field: low confidence requires decision_note ───────────────────
    note = str(a.get("decision_note", "")).strip()
    if conf_int is not None and conf_int <= 2 and not note:
        e("decision_note",
          "Low confidence (≤2) annotations must include a decision_note.")

    # ── Warnings: ambiguous quality without explanation ───────────────────────
    clarity = a.get("speech_clarity")
    rec_quality = a.get("recording_quality")

    if clarity == "unclear" and not note:
        w("decision_note",
          "speech_clarity is 'unclear' — consider adding a decision_note.")

    if rec_quality in ("poor", "unusable") and not note:
        w("decision_note",
          f"recording_quality is '{rec_quality}' — consider adding a decision_note.")

    return errors, warnings


def validate_annotations(annotations: list) -> dict:
    """Validate a full annotation list.

    Returns {"errors": [...], "warnings": [...]}.
    Each item includes 'index' (0-based), 'field', 'message'.
    Missing advanced fields in old annotations are skipped (backward compatible).
    """
    all_errors: list = []
    all_warnings: list = []

    for i, a in enumerate(annotations):
        errs, warns = _validate_single(a, index=i)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    # ── Overlap check (sorted by start_time) ─────────────────────────────────
    indexed = sorted(enumerate(annotations), key=lambda x: x[1].get("start_time", 0))
    for j in range(len(indexed) - 1):
        i1, a1 = indexed[j]
        i2, a2 = indexed[j + 1]
        if a1.get("end_time", 0) > a2.get("start_time", 0):
            all_errors.append({
                "index": i2, "field": "start_time",
                "message": (
                    f"Annotation #{i2} overlaps annotation #{i1} "
                    f"({a1['start_time']}s–{a1['end_time']}s)."
                ),
            })

    return {"errors": all_errors, "warnings": all_warnings}


def validate_new(annotation: dict, existing: list) -> dict:
    """Validate a single new annotation against the existing list.

    Returns {"errors": [...], "warnings": [...]}.
    Items do NOT include 'index' (the entry is not yet in the list).
    """
    errors, warnings = _validate_single(annotation, index=None)

    s = annotation.get("start_time")
    e = annotation.get("end_time")
    if s is not None and e is not None:
        for i, a in enumerate(existing):
            if s < a.get("end_time", 0) and e > a.get("start_time", 0):
                errors.append({
                    "field": "start_time",
                    "message": f"Time overlap with annotation #{i} "
                               f"({a['start_time']}s–{a['end_time']}s).",
                })

    return {"errors": errors, "warnings": warnings}
