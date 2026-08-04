from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .models import IngestionResult


def build_quality_report(result: IngestionResult) -> dict[str, Any]:
    """Create decision-ready quality metrics without estimating emissions."""
    total = len(result.accepted) + len(result.rejected)
    error_codes = Counter(issue.code for rejected in result.rejected for issue in rejected.issues)
    error_fields = Counter(issue.field for rejected in result.rejected for issue in rejected.issues)
    categories = Counter(record.category for record in result.accepted)
    units = Counter(record.unit for record in result.accepted)
    transformed = sum(bool(record.provenance.transformations) for record in result.accepted)

    return {
        "schema_version": "1.0.0",
        "source": {"file": result.source_file, "format": result.source_format, "sha256": result.source_sha256},
        "row_counts": {
            "total": total,
            "accepted": len(result.accepted),
            "rejected": len(result.rejected),
            "acceptance_rate_percent": round((len(result.accepted) / total * 100), 2) if total else 0.0,
            "accepted_with_transformations": transformed,
        },
        "accepted_breakdown": {
            "by_category": dict(sorted(categories.items())),
            "by_unit": dict(sorted(units.items())),
        },
        "rejection_breakdown": {
            "by_error_code": dict(sorted(error_codes.items())),
            "by_field": dict(sorted(error_fields.items())),
        },
        "warnings": result.warnings,
        "fitness_for_use": {
            "ready_for_day_2_baseline_analysis": bool(result.accepted),
            "condition": "Only accepted rows may enter later emissions calculations.",
        },
    }


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def report_to_markdown(report: dict[str, Any]) -> str:
    rows = report["row_counts"]
    errors = report["rejection_breakdown"]["by_error_code"]
    categories = report["accepted_breakdown"]["by_category"]
    warnings = report["warnings"]
    lines = [
        "# Data Quality Report",
        "",
        f"- Source: `{report['source']['file']}` ({report['source']['format']})",
        f"- SHA-256: `{report['source']['sha256']}`",
        f"- Total rows: **{rows['total']}**",
        f"- Accepted: **{rows['accepted']}**",
        f"- Rejected: **{rows['rejected']}**",
        f"- Acceptance rate: **{rows['acceptance_rate_percent']}%**",
        f"- Accepted rows normalized: **{rows['accepted_with_transformations']}**",
        "",
        "## Accepted categories",
        "",
    ]
    lines.extend(f"- {name}: {count}" for name, count in categories.items())
    if not categories:
        lines.append("- None")
    lines.extend(["", "## Rejection reasons", ""])
    lines.extend(f"- {name}: {count}" for name, count in errors.items())
    if not errors:
        lines.append("- None")
    lines.extend(["", "## Privacy and provenance warnings", ""])
    lines.extend(f"- {warning}" for warning in warnings)
    if not warnings:
        lines.append("- No common direct-identifier columns detected.")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "This report measures data fitness, not environmental impact. Carbon emissions are not calculated on Day 1 because emission-factor selection, geography, year and uncertainty must be handled explicitly in later stages.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(result: IngestionResult, output_dir: str | Path) -> dict[str, Path]:
    """Write normalized, rejected and summary artifacts to one reproducible directory."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    accepted_path = output / "accepted_records.jsonl"
    rejected_path = output / "rejected_records.jsonl"
    report_json_path = output / "quality_report.json"
    report_md_path = output / "quality_report.md"

    _write_jsonl(accepted_path, [record.as_dict() for record in result.accepted])
    _write_jsonl(rejected_path, [record.as_dict() for record in result.rejected])
    report = build_quality_report(result)
    report_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    report_md_path.write_text(report_to_markdown(report), encoding="utf-8")

    return {
        "accepted": accepted_path,
        "rejected": rejected_path,
        "report_json": report_json_path,
        "report_markdown": report_md_path,
    }
