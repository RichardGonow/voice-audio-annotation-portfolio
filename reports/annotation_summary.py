"""
Annotation Summary Report
Usage:
  python reports/annotation_summary.py
  python reports/annotation_summary.py data/annotations/
  python reports/annotation_summary.py data/annotations/ --output reports/annotation_summary.md
Writes a Markdown summary to reports/annotation_summary.md by default.
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data" / "annotations"
DEFAULT_OUTPUT = Path(__file__).parent / "annotation_summary.md"


def load_all(data_dir: Path) -> list:
    files = []
    for p in sorted(data_dir.glob("*.annotations.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            files.append({
                "file": p.name,
                "audio_id": data.get("audio_id", p.name),
                "annotations": data.get("annotations", []),
            })
        except Exception as e:
            print(f"Warning: could not load {p.name}: {e}", file=sys.stderr)
    return files


def build_summary(files: list) -> dict:
    all_annotations = []
    for f in files:
        all_annotations.extend(f["annotations"])

    total_duration = sum(
        a.get("end_time", 0) - a.get("start_time", 0)
        for a in all_annotations
    )

    return {
        "total_files": len(files),
        "total_annotations": len(all_annotations),
        "total_duration_s": round(total_duration, 2),
        "avg_per_audio": round(len(all_annotations) / len(files), 2) if files else 0,
        "intent": Counter(a.get("intent", "") for a in all_annotations),
        "emotion": Counter(a.get("emotion", "") for a in all_annotations),
        "noise_type": Counter(a.get("noise_type", "") for a in all_annotations),
        "quality_flag": Counter(a.get("quality_flag", "") for a in all_annotations),
    }


def counter_table(counter: Counter) -> str:
    if not counter:
        return "_No data_\n"
    lines = ["| Label | Count |", "|-------|-------|"]
    for label, count in counter.most_common():
        if label:
            lines.append(f"| `{label}` | {count} |")
    return "\n".join(lines)


def render_markdown(summary: dict, generated_at: str) -> str:
    total_s = summary["total_duration_s"]
    mins = int(total_s // 60)
    secs = total_s % 60
    duration_str = f"{mins}m {secs:.1f}s" if mins else f"{secs:.1f}s"

    lines = [
        "# Annotation Summary Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total audio files | {summary['total_files']} |",
        f"| Total annotations | {summary['total_annotations']} |",
        f"| Total annotated duration | {duration_str} |",
        f"| Average annotations per audio | {summary['avg_per_audio']} |",
        "",
        "## Intent Distribution",
        "",
        counter_table(summary["intent"]),
        "",
        "## Emotion Distribution",
        "",
        counter_table(summary["emotion"]),
        "",
        "## Noise Type Distribution",
        "",
        counter_table(summary["noise_type"]),
        "",
        "## Quality Flag Distribution",
        "",
        counter_table(summary["quality_flag"]),
    ]
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    data_dir = DEFAULT_DATA_DIR
    output_path = DEFAULT_OUTPUT

    i = 0
    positional = []
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output_path = Path(args[i + 1])
            i += 2
        else:
            positional.append(args[i])
            i += 1

    if positional:
        data_dir = Path(positional[0])

    if not data_dir.exists():
        print(f"Error: directory not found — {data_dir}")
        sys.exit(1)

    files = load_all(data_dir)
    if not files:
        print(f"No .annotations.json files found in {data_dir}")
        sys.exit(0)

    summary = build_summary(files)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md = render_markdown(summary, generated_at)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")

    print(f"Summary written to {output_path}")
    print(f"Files: {summary['total_files']}  "
          f"Annotations: {summary['total_annotations']}  "
          f"Duration: {summary['total_duration_s']}s")


if __name__ == "__main__":
    main()
