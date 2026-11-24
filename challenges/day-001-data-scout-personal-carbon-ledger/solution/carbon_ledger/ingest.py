from __future__ import annotations

import csv
import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import IngestionResult, Provenance, RejectedRecord
from .schema import privacy_warnings, validate_record

Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(UTC)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_csv(path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV must contain a header row.")
        records = [dict(row) for row in reader]
        return records, set(reader.fieldnames)


def _read_json(path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict) and "records" in payload:
        payload = payload["records"]
    if not isinstance(payload, list):
        raise ValueError("JSON input must be a list or an object containing a 'records' list.")

    records: list[dict[str, Any]] = []
    field_names: set[str] = set()
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"JSON record {index} must be an object.")
        record = {str(key): value for key, value in item.items()}
        records.append(record)
        field_names.update(record)
    return records, field_names


def _read_records(path: Path) -> tuple[list[dict[str, Any]], set[str], str]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        records, fields = _read_csv(path)
        return records, fields, "csv"
    if suffix == ".json":
        records, fields = _read_json(path)
        return records, fields, "json"
    raise ValueError("Unsupported input format. Use a .csv or .json file.")


def ingest_file(
    input_path: str | Path,
    *,
    source_name: str,
    license_note: str,
    clock: Clock = _utc_now,
) -> IngestionResult:
    """Ingest a CSV or JSON file and quarantine invalid rows with lineage."""
    path = Path(input_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")
    if not source_name.strip():
        raise ValueError("source_name cannot be empty.")
    if not license_note.strip():
        raise ValueError("license_note cannot be empty.")

    records, field_names, source_format = _read_records(path)
    source_hash = sha256_file(path)
    ingested_at = clock().astimezone(UTC).isoformat().replace("+00:00", "Z")
    result = IngestionResult(
        source_sha256=source_hash,
        source_file=path.name,
        source_format=source_format,
        warnings=privacy_warnings(field_names),
    )

    seen_ids: set[str] = set()
    for row_number, raw_record in enumerate(records, start=2 if source_format == "csv" else 1):
        raw_id = str(raw_record.get("record_id", "")).strip()
        duplicate = bool(raw_id and raw_id in seen_ids)
        provenance = Provenance(
            source_name=source_name.strip(),
            source_file=path.name,
            source_sha256=source_hash,
            source_format=source_format,
            source_row=row_number,
            ingested_at_utc=ingested_at,
            license_note=license_note.strip(),
        )
        record, issues = validate_record(raw_record, provenance, duplicate_id=duplicate)
        if record is None:
            result.rejected.append(
                RejectedRecord(raw_record=raw_record, issues=issues, provenance=provenance)
            )
        else:
            result.accepted.append(record)
            seen_ids.add(record.record_id)

    return result
