"""
Voice Annotation QA Report
Usage:
  python qa_report.py <file.json>                            # single file
  python qa_report.py <directory/>                           # all .json files in directory
  python qa_report.py <path> --markdown <output.md>          # also write Markdown report
Exit 0 = all checks passed (errors=0); Exit 1 = errors found.
Warnings do not affect the exit code.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.validation import validate_annotations


def check_file(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    audio_id = data.get("audio_id", path.name)
    annotations = data.get("annotations", [])
    result = validate_annotations(annotations)
    return {
        "path": path,
        "audio_id": audio_id,
        "total": len(annotations),
        "errors": result["errors"],
        "warnings": result["warnings"],
    }


def print_file_result(result: dict) -> None:
    print(f"File: {result['path']}")
    print(f"audio_id: {result['audio_id']}")
    print(f"Total annotations: {result['total']}")
    print(f"Errors: {len(result['errors'])}")
    print(f"Warnings: {len(result['warnings'])}")
    for e in result["errors"]:
        print(f"  [ERROR] annotation #{e['index']} - {e['field']}: {e['message']}")
    for w in result["warnings"]:
        print(f"  [WARNING] annotation #{w['index']} - {w['field']}: {w['message']}")
    if not result["errors"] and not result["warnings"]:
        print("  QA Passed. No validation errors or warnings found.")
    print()


def render_markdown(results: list, target: Path) -> str:
    clean = [r for r in results if not r["errors"] and not r["warnings"]]
    with_errors = [r for r in results if r["errors"]]
    with_warnings = [r for r in results if r["warnings"]]
    total_annotations = sum(r["total"] for r in results)
    total_errors = sum(len(r["errors"]) for r in results)
    total_warnings = sum(len(r["warnings"]) for r in results)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# Voice Annotation QA Report",
        "",
        f"Generated: {generated_at}",
        f"Input: `{target}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total files | {len(results)} |",
        f"| Clean files (no errors or warnings) | {len(clean)} |",
        f"| Files with errors | {len(with_errors)} |",
        f"| Files with warnings | {len(with_warnings)} |",
        f"| Total annotations | {total_annotations} |",
        f"| Total errors | {total_errors} |",
        f"| Total warnings | {total_warnings} |",
        "",
        "## Results by File",
        "",
    ]

    for r in results:
        if r["errors"]:
            status = f"FAIL ({len(r['errors'])} error(s))"
        elif r["warnings"]:
            status = f"WARN ({len(r['warnings'])} warning(s))"
        else:
            status = "PASS"

        lines.append(f"### `{r['path'].name}` — {status}")
        lines.append("")
        lines.append(f"- audio_id: `{r['audio_id']}`")
        lines.append(f"- Annotations: {r['total']}")

        if r["errors"]:
            lines.append("")
            lines.append("**Errors**")
            lines.append("")
            lines.append("| # | Field | Message |")
            lines.append("|---|-------|---------|")
            for e in r["errors"]:
                lines.append(f"| {e['index']} | `{e['field']}` | {e['message']} |")

        if r["warnings"]:
            lines.append("")
            lines.append("**Warnings**")
            lines.append("")
            lines.append("| # | Field | Message |")
            lines.append("|---|-------|---------|")
            for w in r["warnings"]:
                lines.append(f"| {w['index']} | `{w['field']}` | {w['message']} |")

        lines.append("")

    return "\n".join(lines)


def run_single(path: Path, markdown_out: Path) -> int:
    print("Voice Annotation QA Report")
    print("==========================")
    print()
    result = check_file(path)
    print_file_result(result)
    if markdown_out:
        md = render_markdown([result], path)
        markdown_out.parent.mkdir(parents=True, exist_ok=True)
        markdown_out.write_text(md, encoding="utf-8")
        print(f"Markdown report written to {markdown_out}")
    return 1 if result["errors"] else 0


def run_directory(dirpath: Path, markdown_out: Path) -> int:
    files = sorted(dirpath.glob("*.json"))
    if not files:
        print(f"No .json files found in {dirpath}")
        return 0

    results = []
    for f in files:
        try:
            results.append(check_file(f))
        except Exception as ex:
            print(f"Warning: could not process {f.name}: {ex}", file=sys.stderr)

    with_errors = [r for r in results if r["errors"]]
    with_warnings = [r for r in results if r["warnings"]]
    total_annotations = sum(r["total"] for r in results)
    total_errors = sum(len(r["errors"]) for r in results)
    total_warnings = sum(len(r["warnings"]) for r in results)

    print("Voice Annotation Batch QA Report")
    print("=================================")
    print()
    print(f"Directory:             {dirpath}")
    print(f"Total files:           {len(results)}")
    print(f"Files with errors:     {len(with_errors)}")
    print(f"Files with warnings:   {len(with_warnings)}")
    print(f"Total annotations:     {total_annotations}")
    print(f"Total errors:          {total_errors}")
    print(f"Total warnings:        {total_warnings}")
    print()

    for r in results:
        if r["errors"] or r["warnings"]:
            print_file_result(r)

    if markdown_out:
        md = render_markdown(results, dirpath)
        markdown_out.parent.mkdir(parents=True, exist_ok=True)
        markdown_out.write_text(md, encoding="utf-8")
        print(f"Markdown report written to {markdown_out}")

    return 1 if with_errors else 0


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python qa_report.py <file.json|directory> [--markdown <output.md>]")
        sys.exit(1)

    markdown_out = None
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--markdown" and i + 1 < len(args):
            markdown_out = Path(args[i + 1])
            i += 2
        else:
            positional.append(args[i])
            i += 1

    if not positional:
        print("Error: no input path specified.")
        sys.exit(1)

    target = Path(positional[0])
    if not target.exists():
        # data_set/ lives one level above this script (outer project root)
        candidate = Path(__file__).resolve().parent.parent / positional[0]
        if candidate.exists():
            target = candidate
        else:
            print(f"Error: not found — {target}")
            sys.exit(1)

    if target.is_dir():
        sys.exit(run_directory(target, markdown_out))
    else:
        sys.exit(run_single(target, markdown_out))


if __name__ == "__main__":
    main()
