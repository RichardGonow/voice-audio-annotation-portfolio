"""
Annotation Statistics Report
Reads all .json files from data_set/json_database/ and writes reports/annotation_statistics.md.

Usage:
  python reports/annotation_statistics.py
  python reports/annotation_statistics.py [--output reports/annotation_statistics.md]
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.export import find_dataset_root

_APP_DIR = Path(__file__).parent.parent / "app"
_DATASET_ROOT = find_dataset_root(_APP_DIR)
JSON_DB_DIR = _DATASET_ROOT / "json_database"
DEFAULT_OUTPUT = Path(__file__).parent / "annotation_statistics.md"


def load_all(json_db_dir: Path) -> list[dict]:
    files = []
    for p in sorted(json_db_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            files.append({
                "file": p.name,
                "audio_id": data.get("audio_id", p.name),
                "annotations": data.get("annotations", []),
            })
        except Exception as ex:
            print(f"Warning: could not load {p.name}: {ex}", file=sys.stderr)
    return files


def build_stats(files: list[dict]) -> dict:
    all_a = [a for f in files for a in f["annotations"]]

    durations = [
        a.get("end_time", 0) - a.get("start_time", 0)
        for a in all_a
        if a.get("end_time") is not None and a.get("start_time") is not None
    ]
    total_dur = round(sum(durations), 2)
    avg_dur = round(total_dur / len(durations), 2) if durations else 0.0

    def dist(field):
        return Counter(a.get(field, "unknown") for a in all_a)

    # Disfluency rate: count annotations where disfluency_present == "yes"
    disf_yes = sum(1 for a in all_a if a.get("disfluency_present") == "yes")
    overlap_yes = sum(1 for a in all_a if a.get("overlap_speech") == "yes")
    total = len(all_a)

    confidence_values = [
        int(a["annotation_confidence"])
        for a in all_a
        if a.get("annotation_confidence") is not None
        and str(a["annotation_confidence"]).isdigit()
    ]
    avg_confidence = round(sum(confidence_values) / len(confidence_values), 2) if confidence_values else None

    return {
        "total_files": len(files),
        "total_annotations": total,
        "total_duration_s": total_dur,
        "avg_annotation_duration_s": avg_dur,
        "avg_per_file": round(total / len(files), 2) if files else 0,
        "intent": dist("intent"),
        "emotion": dist("emotion"),
        "accent_region": dist("accent_region"),
        "dialect_label": dist("dialect_label"),
        "speech_clarity": dist("speech_clarity"),
        "background_noise_level": dist("background_noise_level"),
        "recording_quality": dist("recording_quality"),
        "speaking_rate": dist("speaking_rate"),
        "intonation": dist("intonation"),
        "speech_energy": dist("speech_energy"),
        "disfluency_rate_pct": round(disf_yes / total * 100, 1) if total else 0.0,
        "overlap_speech_rate_pct": round(overlap_yes / total * 100, 1) if total else 0.0,
        "avg_annotation_confidence": avg_confidence,
    }


def counter_table(counter: Counter) -> str:
    if not counter:
        return "_No data_"
    rows = ["| Label | Count | % |", "|-------|-------|---|"]
    total = sum(counter.values())
    for label, count in counter.most_common():
        pct = round(count / total * 100, 1)
        rows.append(f"| `{label}` | {count} | {pct}% |")
    return "\n".join(rows)


def duration_str(total_s: float) -> str:
    mins = int(total_s // 60)
    secs = total_s % 60
    return f"{mins}m {secs:.1f}s" if mins else f"{secs:.1f}s"


def render_markdown(stats: dict, generated_at: str) -> str:
    conf_str = str(stats["avg_annotation_confidence"]) if stats["avg_annotation_confidence"] is not None else "N/A"

    sections = [
        "# Annotation Statistics Report",
        "",
        f"Generated: {generated_at}",
        f"Source: `{JSON_DB_DIR}`",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total audio files | {stats['total_files']} |",
        f"| Total annotations | {stats['total_annotations']} |",
        f"| Total annotated duration | {duration_str(stats['total_duration_s'])} |",
        f"| Average annotation duration | {stats['avg_annotation_duration_s']}s |",
        f"| Average annotations per file | {stats['avg_per_file']} |",
        f"| Disfluency rate | {stats['disfluency_rate_pct']}% |",
        f"| Overlap speech rate | {stats['overlap_speech_rate_pct']}% |",
        f"| Average annotation confidence | {conf_str} / 5 |",
        "",
    ]

    distribution_fields = [
        ("Intent Distribution",              "intent"),
        ("Emotion Distribution",             "emotion"),
        ("Accent Region Distribution",       "accent_region"),
        ("Dialect Distribution",             "dialect_label"),
        ("Speech Clarity Distribution",      "speech_clarity"),
        ("Background Noise Distribution",    "background_noise_level"),
        ("Recording Quality Distribution",   "recording_quality"),
        ("Speaking Rate Distribution",       "speaking_rate"),
        ("Intonation Distribution",          "intonation"),
        ("Speech Energy Distribution",       "speech_energy"),
    ]

    for title, key in distribution_fields:
        sections += [f"## {title}", "", counter_table(stats[key]), ""]

    return "\n".join(sections)


def main():
    args = sys.argv[1:]
    output_path = DEFAULT_OUTPUT

    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output_path = Path(args[i + 1])
            i += 2
        else:
            i += 1

    if not JSON_DB_DIR.exists():
        print(f"Directory not found: {JSON_DB_DIR}")
        print("Save at least one annotation via the Streamlit UI first.")
        sys.exit(0)

    files = load_all(JSON_DB_DIR)
    if not files:
        print(f"No .json files found in {JSON_DB_DIR}")
        print("Save at least one annotation via the Streamlit UI first.")
        sys.exit(0)

    stats = build_stats(files)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md = render_markdown(stats, generated_at)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")

    print(f"Statistics written to {output_path}")
    print(f"Files: {stats['total_files']}  "
          f"Annotations: {stats['total_annotations']}  "
          f"Duration: {duration_str(stats['total_duration_s'])}")


if __name__ == "__main__":
    main()
