import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.export import (
    annotations_to_csv,
    annotations_to_json,
    find_dataset_root,
    save_annotations_csv,
    save_annotations_json,
    save_annotations_to_disk,
)
from app.validation import validate_new

# ── Core label lists ──────────────────────────────────────────────────────────
INTENTS = ["greeting", "question", "request", "complaint", "confirmation", "small_talk", "other"]
EMOTIONS = ["neutral", "happy", "angry", "sad", "anxious", "confused", "other"]
NOISE_TYPES = ["none", "background_noise", "music", "overlapping_speech", "low_volume", "unclear", "other"]
QUALITY_FLAGS = ["good", "fair", "poor", "unusable"]

# ── Advanced label lists ──────────────────────────────────────────────────────
ACCENT_REGIONS = [
    "user_defined", "standard_mandarin", "northern_mandarin", "northeastern_mandarin",
    "middle_mandarin", "southwestern_mandarin", "cantonese_accent",
    "taiwan_mandarin", "singapore_mandarin", "mixed_accent",
]
DIALECT_LABELS = [
    "mandarin", "cantonese", "hokkien", "hakka", "shanghainese_wu",
    "sichuanese", "taiwanese_mandarin", "singapore_mandarin", "mixed", "user_defined",
]
SPEECH_CLARITY = ["clear", "mostly_clear", "partially_unclear", "unclear"]
BACKGROUND_NOISE_LEVELS = ["none", "low", "medium", "high"]
RECORDING_QUALITY = ["studio", "good", "acceptable", "poor", "unusable"]
SPEAKING_RATES = ["slow", "normal", "fast", "variable"]
INTONATIONS = ["flat", "rising", "falling", "expressive", "variable"]
SPEECH_ENERGY = ["low", "medium", "high", "variable"]
DISFLUENCY_PRESENT = ["no", "yes"]
DISFLUENCY_TYPES = ["none", "filler", "repetition", "self_correction", "hesitation", "false_start"]
OVERLAP_SPEECH = ["no", "yes"]

# ── Save directories ──────────────────────────────────────────────────────────
ANNOTATIONS_DIR = Path(__file__).parent.parent / "data" / "annotations"
_DATASET_ROOT = find_dataset_root(Path(__file__).parent)
JSON_DB_DIR = _DATASET_ROOT / "json_database"
CSV_DB_DIR = _DATASET_ROOT / "csv_database"


def main():
    st.set_page_config(
        page_title="Voice / Audio Annotation Portfolio",
        page_icon="🎙️",
        layout="wide",
    )
    st.title("Voice / Audio Annotation Portfolio")

    if "annotations" not in st.session_state:
        st.session_state.annotations = []
    if "audio_id" not in st.session_state:
        st.session_state.audio_id = ""

    # ── Section 1: Audio upload ───────────────────────────────────────────────
    st.header("1. Upload Audio")

    uploaded = st.file_uploader(
        "Choose a .wav or .mp3 file",
        type=["wav", "mp3"],
        help="Uploaded audio will be played back in the browser.",
    )

    if uploaded:
        new_id = uploaded.name
        if new_id != st.session_state.audio_id:
            st.session_state.annotations = []
            st.session_state.audio_id = new_id
        st.audio(uploaded)

    col_id, _ = st.columns([1, 2])
    audio_id = col_id.text_input(
        "audio_id",
        value=st.session_state.audio_id,
        placeholder="e.g. sample_001.wav",
        help="Auto-filled from the uploaded filename. You can edit it.",
    )
    st.session_state.audio_id = audio_id

    st.divider()

    # ── Section 2: Load existing annotations ─────────────────────────────────
    st.header("2. Load Existing Annotations")

    col_upload, col_saved = st.columns(2)

    with col_upload:
        st.subheader("Upload a JSON file")
        load_file = st.file_uploader(
            "Choose a .annotations.json file",
            type=["json"],
            key="load_uploader",
            help="Replaces the current session annotations.",
        )
        if load_file is not None:
            if st.button("Load from uploaded file"):
                try:
                    data = json.load(load_file)
                    st.session_state.annotations = data.get("annotations", [])
                    if not st.session_state.audio_id:
                        st.session_state.audio_id = data.get("audio_id", "")
                    st.success(f"Loaded {len(st.session_state.annotations)} annotations.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Failed to load file: {ex}")

    with col_saved:
        st.subheader("Load from saved files")
        ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)
        saved_files = sorted(ANNOTATIONS_DIR.glob("*.annotations.json"))
        if saved_files:
            selected = st.selectbox(
                "Select a saved annotation file",
                options=[f.name for f in saved_files],
            )
            if st.button("Load selected file"):
                path = ANNOTATIONS_DIR / selected
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    st.session_state.annotations = data.get("annotations", [])
                    if not st.session_state.audio_id:
                        st.session_state.audio_id = data.get("audio_id", "")
                    st.success(f"Loaded {len(st.session_state.annotations)} annotations from {selected}.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Failed to load {selected}: {ex}")
        else:
            st.info("No saved files found in data/annotations/.")

    st.divider()

    # ── Section 3: Annotation form ────────────────────────────────────────────
    st.header("3. Add Annotation")

    with st.form("annotation_form", clear_on_submit=True):

        # Core fields
        c1, c2 = st.columns(2)
        start_time = c1.number_input("start_time (s)", min_value=0.0, step=0.1, format="%.2f")
        end_time = c2.number_input("end_time (s)", min_value=0.0, step=0.1, format="%.2f")

        speaker = st.text_input("speaker", placeholder="SPEAKER_01")
        transcript = st.text_area("transcript *", placeholder="Verbatim transcription of the spoken content…")

        c3, c4 = st.columns(2)
        intent = c3.selectbox("intent", INTENTS)
        emotion = c4.selectbox("emotion", EMOTIONS)

        c5, c6 = st.columns(2)
        noise_type = c5.selectbox("noise_type", NOISE_TYPES)
        quality_flag = c6.selectbox("quality_flag", QUALITY_FLAGS)

        notes = st.text_input("notes (optional)")

        # Advanced fields
        with st.expander("Advanced Audio Annotation"):
            ca1, ca2 = st.columns(2)
            accent_region = ca1.selectbox("accent_region", ACCENT_REGIONS,
                                          index=ACCENT_REGIONS.index("user_defined"))
            dialect_label = ca2.selectbox("dialect_label", DIALECT_LABELS,
                                          index=DIALECT_LABELS.index("mandarin"))

            accent_custom = ca1.text_input(
                "Custom accent region",
                placeholder="e.g. 湖南口音、中原官话 (当上方选 user_defined 时生效)",
                key="accent_custom",
            )
            dialect_custom = ca2.text_input(
                "Custom dialect label",
                placeholder="e.g. 湘语、晋语 (当上方选 user_defined 时生效)",
                key="dialect_custom",
            )

            ca3, ca4 = st.columns(2)
            speech_clarity = ca3.selectbox("speech_clarity", SPEECH_CLARITY,
                                           index=SPEECH_CLARITY.index("clear"))
            background_noise_level = ca4.selectbox("background_noise_level", BACKGROUND_NOISE_LEVELS,
                                                   index=BACKGROUND_NOISE_LEVELS.index("none"))

            ca5, ca6 = st.columns(2)
            recording_quality = ca5.selectbox("recording_quality", RECORDING_QUALITY,
                                              index=RECORDING_QUALITY.index("good"))
            speaking_rate = ca6.selectbox("speaking_rate", SPEAKING_RATES,
                                          index=SPEAKING_RATES.index("normal"))

            ca7, ca8 = st.columns(2)
            intonation = ca7.selectbox("intonation", INTONATIONS,
                                       index=INTONATIONS.index("variable"))
            speech_energy = ca8.selectbox("speech_energy", SPEECH_ENERGY,
                                          index=SPEECH_ENERGY.index("medium"))

            ca9, ca10 = st.columns(2)
            disfluency_present = ca9.selectbox("disfluency_present", DISFLUENCY_PRESENT,
                                               index=DISFLUENCY_PRESENT.index("no"))
            overlap_speech = ca10.selectbox("overlap_speech", OVERLAP_SPEECH,
                                            index=OVERLAP_SPEECH.index("no"))

            disfluency_type = st.multiselect(
                "disfluency_type",
                DISFLUENCY_TYPES,
                default=["none"],
                help="Select all that apply.",
            )

            annotation_confidence = st.slider(
                "annotation_confidence",
                min_value=1, max_value=5, value=4,
                help="1 = very uncertain, 5 = fully confident",
            )

            decision_note = st.text_area(
                "decision_note (optional)",
                placeholder="Explain any ambiguous labeling decisions…",
            )

        submitted = st.form_submit_button("Add Annotation", type="primary", use_container_width=True)

    if submitted:
        annotation = {
            "start_time": round(start_time, 2),
            "end_time": round(end_time, 2),
            "speaker": speaker.strip(),
            "transcript": transcript.strip(),
            "intent": intent,
            "emotion": emotion,
            "noise_type": noise_type,
            "quality_flag": quality_flag,
            "notes": notes.strip(),
            # Advanced fields — use custom text when user_defined is selected
            "accent_region": (accent_custom.strip() or "user_defined")
                             if accent_region == "user_defined" else accent_region,
            "dialect_label": (dialect_custom.strip() or "user_defined")
                             if dialect_label == "user_defined" else dialect_label,
            "speech_clarity": speech_clarity,
            "background_noise_level": background_noise_level,
            "recording_quality": recording_quality,
            "speaking_rate": speaking_rate,
            "intonation": intonation,
            "speech_energy": speech_energy,
            "disfluency_present": disfluency_present,
            "disfluency_type": ",".join(disfluency_type) if disfluency_type else "none",
            "overlap_speech": overlap_speech,
            "annotation_confidence": annotation_confidence,
            "decision_note": decision_note.strip(),
        }
        result = validate_new(annotation, st.session_state.annotations)
        if result["errors"]:
            for err in result["errors"]:
                st.error(f"[{err['field']}] {err['message']}")
        else:
            st.session_state.annotations.append(annotation)
            st.success(f"Annotation #{len(st.session_state.annotations)} added.")
            for warn in result["warnings"]:
                st.warning(f"[{warn['field']}] {warn['message']}")

    st.divider()

    # ── Section 4: Annotation table + manage + export ─────────────────────────
    count = len(st.session_state.annotations)
    st.header(f"4. Annotations ({count})")

    if count:
        df = pd.DataFrame(st.session_state.annotations)
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)

        with st.expander("Delete an annotation"):
            del_index = st.number_input(
                "Annotation number to delete (1-based)",
                min_value=1,
                max_value=count,
                step=1,
                key="del_index",
            )
            if st.button("Delete", key="btn_delete"):
                st.session_state.annotations.pop(int(del_index) - 1)
                st.success(f"Annotation #{del_index} deleted.")
                st.rerun()

        st.divider()

        aid = st.session_state.audio_id or "unknown"

        st.caption(f"JSON database: `{JSON_DB_DIR}`")
        st.caption(f"CSV database:  `{CSV_DB_DIR}`")

        c_json_db, c_csv_db = st.columns(2)

        if c_json_db.button("Save JSON to Database", type="primary", use_container_width=True):
            try:
                path, overwritten = save_annotations_json(aid, st.session_state.annotations, JSON_DB_DIR)
                msg = f"JSON saved to: {path}"
                if overwritten:
                    msg += "\n\nExisting file overwritten."
                st.success(msg)
            except Exception as ex:
                st.error(f"Save failed: {ex}")

        if c_csv_db.button("Save CSV to Database", type="primary", use_container_width=True):
            try:
                path, overwritten = save_annotations_csv(aid, st.session_state.annotations, CSV_DB_DIR)
                msg = f"CSV saved to: {path}"
                if overwritten:
                    msg += "\n\nExisting file overwritten."
                st.success(msg)
            except Exception as ex:
                st.error(f"Save failed: {ex}")

        c_dl_json, c_dl_csv, c_save, c_clear = st.columns(4)

        c_dl_json.download_button(
            "Download JSON",
            data=annotations_to_json(aid, st.session_state.annotations),
            file_name=f"{aid}.annotations.json",
            mime="application/json",
            use_container_width=True,
        )
        c_dl_csv.download_button(
            "Download CSV",
            data=annotations_to_csv(aid, st.session_state.annotations),
            file_name=f"{aid}.annotations.csv",
            mime="text/csv",
            use_container_width=True,
        )

        if c_save.button("Save to data/annotations", use_container_width=True):
            try:
                json_path, csv_path = save_annotations_to_disk(aid, st.session_state.annotations, ANNOTATIONS_DIR)
                st.success(f"Saved: {json_path.name}, {csv_path.name}")
            except Exception as ex:
                st.error(f"Save failed: {ex}")

        if c_clear.button("Clear All Annotations", use_container_width=True):
            st.session_state.annotations = []
            st.rerun()

    else:
        st.info("No annotations yet. Fill in the form above and click **Add Annotation**.")


if __name__ == "__main__":
    main()
