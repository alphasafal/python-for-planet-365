from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A machine-readable validation failure for one source row."""

    field: str
    code: str
    message: str
    value: Any = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "code": self.code,
            "message": self.message,
            "value": self.value,
        }


@dataclass(frozen=True, slots=True)
class Provenance:
    """Dataset and row lineage retained with every normalized record."""

    source_name: str
    source_file: str
    source_sha256: str
    source_format: str
    source_row: int
    ingested_at_utc: str
    license_note: str
    schema_version: str = "1.0.0"
    transformations: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "source_file": self.source_file,
            "source_sha256": self.source_sha256,
            "source_format": self.source_format,
            "source_row": self.source_row,
            "ingested_at_utc": self.ingested_at_utc,
            "license_note": self.license_note,
            "schema_version": self.schema_version,
            "transformations": list(self.transformations),
        }


@dataclass(frozen=True, slots=True)
class ActivityRecord:
    """A validated sustainability activity ready for later emissions estimation."""

    record_id: str
    occurred_at_utc: str
    category: str
    activity: str
    quantity: Decimal
    unit: str
    location: str | None
    notes: str | None
    provenance: Provenance

    def as_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "occurred_at_utc": self.occurred_at_utc,
            "category": self.category,
            "activity": self.activity,
            "quantity": format(self.quantity, "f"),
            "unit": self.unit,
            "location": self.location,
            "notes": self.notes,
            "provenance": self.provenance.as_dict(),
        }


@dataclass(frozen=True, slots=True)
class RejectedRecord:
    """A source row quarantined with explicit reasons instead of being discarded."""

    raw_record: dict[str, Any]
    issues: tuple[ValidationIssue, ...]
    provenance: Provenance

    def as_dict(self) -> dict[str, Any]:
        return {
            "raw_record": self.raw_record,
            "issues": [issue.as_dict() for issue in self.issues],
            "provenance": self.provenance.as_dict(),
        }


@dataclass(slots=True)
class IngestionResult:
    """Accepted and rejected rows plus source-level warnings."""

    accepted: list[ActivityRecord] = field(default_factory=list)
    rejected: list[RejectedRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_sha256: str = ""
    source_file: str = ""
    source_format: str = ""
