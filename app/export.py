import csv
import io
import json
from pathlib import Path


def annotations_to_json(audio_id: str, annotations: list) -> bytes:
    payload = {"audio_id": audio_id, "annotations": annotations}
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


def annotations_to_csv(audio_id: str, annotations: list) -> bytes:
    if not annotations:
        return b""
    output = io.StringIO()
    fieldnames = ["audio_id"] + list(annotations[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for a in annotations:
        writer.writerow({"audio_id": audio_id, **a})
    return output.getvalue().encode("utf-8")


def save_annotations_to_disk(audio_id: str, annotations: list, base_dir: Path) -> tuple[Path, Path]:
    """Save annotations as JSON and CSV to base_dir. Returns (json_path, csv_path)."""
    base_dir.mkdir(parents=True, exist_ok=True)
    safe_id = audio_id.replace("/", "_").replace("\\", "_")
    json_path = base_dir / f"{safe_id}.annotations.json"
    csv_path = base_dir / f"{safe_id}.annotations.csv"
    json_path.write_bytes(annotations_to_json(audio_id, annotations))
    csv_path.write_bytes(annotations_to_csv(audio_id, annotations))
    return json_path, csv_path


def find_dataset_root(anchor: Path, max_levels: int = 6) -> Path:
    """Walk up from anchor looking for an existing data_set directory.

    If not found after max_levels steps, falls back to creating data_set
    two levels above anchor (i.e. the outer project root when anchor is app/).
    """
    current = anchor.resolve()
    for _ in range(max_levels):
        candidate = current / "data_set"
        if candidate.is_dir():
            return candidate
        parent = current.parent
        if parent == current:  # reached drive root
            break
        current = parent
    # Fallback: outer project root = app/ -> inner_project/ -> outer_project/
    fallback = anchor.resolve().parent.parent / "data_set"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def save_annotations_json(audio_id: str, annotations: list, output_dir: Path) -> tuple[Path, bool]:
    """Save annotations as JSON (UTF-8) to output_dir.

    Returns (saved_path, overwritten).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_id = audio_id.replace("/", "_").replace("\\", "_")
    path = output_dir / f"{safe_id}.annotations.json"
    overwritten = path.exists()
    payload = {"audio_id": audio_id, "annotations": annotations}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path, overwritten


def save_annotations_csv(audio_id: str, annotations: list, output_dir: Path) -> tuple[Path, bool]:
    """Save annotations as CSV (UTF-8-sig for Excel) to output_dir.

    Returns (saved_path, overwritten).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_id = audio_id.replace("/", "_").replace("\\", "_")
    path = output_dir / f"{safe_id}.annotations.csv"
    overwritten = path.exists()
    if not annotations:
        path.write_text("", encoding="utf-8-sig")
        return path, overwritten
    output = io.StringIO()
    fieldnames = ["audio_id"] + list(annotations[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for a in annotations:
        writer.writerow({"audio_id": audio_id, **a})
    path.write_text(output.getvalue(), encoding="utf-8-sig")
    return path, overwritten
