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

INTENTS = ["greeting", "question", "request", "complaint", "confirmation", "small_talk", "other"]
EMOTIONS = ["neutral", "happy", "angry", "sad", "anxious", "confused", "other"]
NOISE_TYPES = ["none", "background_noise", "music", "overlapping_speech", "low_volume", "unclear", "other"]
QUALITY_FLAGS = ["good", "fair", "poor", "unusable"]

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
        st.session_state.audio_id = uploaded.name
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
        }
        errors = validate_new(annotation, st.session_state.annotations)
        if errors:
            for err in errors:
                st.error(f"[{err['field']}] {err['message']}")
        else:
            st.session_state.annotations.append(annotation)
            st.success(f"Annotation #{len(st.session_state.annotations)} added.")

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

        # ── Save paths info ───────────────────────────────────────────────────
        st.caption(f"JSON database: `{JSON_DB_DIR}`")
        st.caption(f"CSV database:  `{CSV_DB_DIR}`")

        # ── Save to database ──────────────────────────────────────────────────
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

        # ── Browser download + manage ─────────────────────────────────────────
        c_dl_json, c_dl_csv, c_save, c_clear = st.columns(4)

        c_dl_json.download_button(
            "Browser Download JSON",
            data=annotations_to_json(aid, st.session_state.annotations),
            file_name=f"{aid}.annotations.json",
            mime="application/json",
            use_container_width=True,
        )
        c_dl_csv.download_button(
            "Browser Download CSV",
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
