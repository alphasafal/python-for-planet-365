from __future__ import annotations

import json
from pathlib import Path

import pytest
from carbon_ledger.cli import main
from carbon_ledger.ingest import ingest_file
from carbon_ledger.models import Provenance
from carbon_ledger.report import build_quality_report, write_outputs
from carbon_ledger.schema import validate_record

BASE = Path(__file__).parents[1]


def provenance() -> Provenance:
    return Provenance(
        source_name="test",
        source_file="fixture.csv",
        source_sha256="abc",
        source_format="csv",
        source_row=2,
        ingested_at_utc="2026-08-04T17:00:00Z",
        license_note="Synthetic test fixture",
    )


def valid_record() -> dict[str, str]:
    return {
        "record_id": "a-1",
        "occurred_at": "2026-08-04T08:30:00+05:30",
        "category": "Transport",
        "activity": "City bus commute",
        "quantity": "12.5",
        "unit": "kms",
        "location": "Vellore",
        "notes": "Morning trip",
    }


def test_valid_record_is_normalized() -> None:
    record, issues = validate_record(valid_record(), provenance())
    assert issues == ()
    assert record is not None
    assert record.category == "transport"
    assert record.unit == "km"
    assert record.occurred_at_utc == "2026-08-04T03:00:00Z"


def test_timestamp_requires_timezone() -> None:
    raw = valid_record()
    raw["occurred_at"] = "2026-08-04T08:30:00"
    record, issues = validate_record(raw, provenance())
    assert record is None
    assert {issue.code for issue in issues} == {"timezone_required"}


def test_invalid_category_and_unit_are_rejected() -> None:
    raw = valid_record()
    raw["category"] = "gaming"
    record, issues = validate_record(raw, provenance())
    assert record is None
    assert "unsupported_category" in {issue.code for issue in issues}

    raw = valid_record()
    raw["unit"] = "kWh"
    record, issues = validate_record(raw, provenance())
    assert record is None
    assert "unit_category_mismatch" in {issue.code for issue in issues}


def test_quantity_must_be_positive_and_finite() -> None:
    for invalid in ("0", "-1", "NaN", "Infinity", "not-a-number"):
        raw = valid_record()
        raw["quantity"] = invalid
        record, issues = validate_record(raw, provenance())
        assert record is None
        assert any(issue.field == "quantity" for issue in issues)


def test_clean_csv_fixture_is_fully_accepted(fixed_clock) -> None:
    result = ingest_file(
        BASE / "data/raw/sample_activities.csv",
        source_name="Synthetic Day 1 CSV",
        license_note="CC0 synthetic fixture",
        clock=fixed_clock,
    )
    assert len(result.accepted) == 8
    assert not result.rejected
    assert len(result.source_sha256) == 64


def test_malformed_rows_are_quarantined(fixed_clock) -> None:
    result = ingest_file(
        BASE / "data/raw/mixed_quality_activities.csv",
        source_name="Mixed fixture",
        license_note="CC0 synthetic fixture",
        clock=fixed_clock,
    )
    assert len(result.accepted) == 2
    assert len(result.rejected) == 6
    assert all(row.issues for row in result.rejected)


def test_json_wrapper_is_supported(fixed_clock) -> None:
    result = ingest_file(
        BASE / "data/raw/sample_activities.json",
        source_name="JSON fixture",
        license_note="CC0 synthetic fixture",
        clock=fixed_clock,
    )
    assert len(result.accepted) == 3
    assert result.accepted[0].unit == "kWh"


def test_duplicate_ids_reject_later_row(tmp_path: Path, fixed_clock) -> None:
    path = tmp_path / "duplicate.csv"
    path.write_text(
        "record_id,occurred_at,category,activity,quantity,unit\n"
        "same,2026-08-04T10:00:00Z,waste,Food scraps,1,kg\n"
        "same,2026-08-04T11:00:00Z,waste,Food scraps,2,kg\n",
        encoding="utf-8",
    )
    result = ingest_file(path, source_name="dup", license_note="synthetic", clock=fixed_clock)
    assert len(result.accepted) == 1
    assert result.rejected[0].issues[0].code == "duplicate"


def test_privacy_warning_never_echoes_value(tmp_path: Path, fixed_clock) -> None:
    path = tmp_path / "privacy.csv"
    path.write_text(
        "record_id,occurred_at,category,activity,quantity,unit,email\n"
        "x,2026-08-04T10:00:00Z,waste,Paper,1,kg,private@example.com\n",
        encoding="utf-8",
    )
    result = ingest_file(path, source_name="privacy", license_note="synthetic", clock=fixed_clock)
    assert "email" in result.warnings[0]
    assert "private@example.com" not in result.warnings[0]


def test_reports_and_cli_contract(tmp_path: Path, fixed_clock) -> None:
    result = ingest_file(
        BASE / "data/raw/mixed_quality_activities.csv",
        source_name="Mixed",
        license_note="Synthetic",
        clock=fixed_clock,
    )
    report = build_quality_report(result)
    assert report["row_counts"]["acceptance_rate_percent"] == 25.0
    paths = write_outputs(result, tmp_path / "out")
    assert all(path.exists() for path in paths.values())
    assert json.loads(paths["report_json"].read_text())["row_counts"]["rejected"] == 6

    code = main(
        [
            "ingest",
            "--input",
            str(BASE / "data/raw/mixed_quality_activities.csv"),
            "--output-dir",
            str(tmp_path / "cli-output"),
            "--source-name",
            "CLI fixture",
            "--license-note",
            "CC0 synthetic fixture",
            "--fail-on-rejection",
        ]
    )
    assert code == 2


def test_unsupported_extension_is_clear(tmp_path: Path, fixed_clock) -> None:
    path = tmp_path / "records.txt"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported input format"):
        ingest_file(path, source_name="text", license_note="synthetic", clock=fixed_clock)
