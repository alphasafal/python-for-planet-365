from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from .models import ActivityRecord, Provenance, ValidationIssue

REQUIRED_FIELDS = ("record_id", "occurred_at", "category", "activity", "quantity", "unit")
OPTIONAL_FIELDS = ("location", "notes")
KNOWN_FIELDS = frozenset((*REQUIRED_FIELDS, *OPTIONAL_FIELDS))

ALLOWED_UNITS: dict[str, frozenset[str]] = {
    "transport": frozenset({"km", "passenger_km", "litre"}),
    "electricity": frozenset({"kWh"}),
    "food": frozenset({"kg", "serving", "item"}),
    "waste": frozenset({"kg"}),
    "purchase": frozenset({"INR", "item", "kg"}),
}

UNIT_ALIASES = {
    "kms": "km",
    "kilometer": "km",
    "kilometers": "km",
    "kilometre": "km",
    "kilometres": "km",
    "kwh": "kWh",
    "l": "litre",
    "liter": "litre",
    "liters": "litre",
    "litres": "litre",
    "inr": "INR",
}

SENSITIVE_FIELD_NAMES = frozenset(
    {"name", "full_name", "email", "phone", "mobile", "exact_address", "device_id"}
)


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _optional_text(value: Any) -> str | None:
    cleaned = _text(value)
    return cleaned or None


def _parse_timestamp(value: Any) -> tuple[str | None, ValidationIssue | None, list[str]]:
    raw = _text(value)
    if not raw:
        return None, ValidationIssue("occurred_at", "missing", "Timestamp is required."), []

    transformations: list[str] = []
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
        transformations.append("converted_Z_suffix_to_UTC_offset")

    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return (
            None,
            ValidationIssue(
                "occurred_at",
                "invalid_timestamp",
                "Use ISO 8601, for example 2026-08-04T08:30:00+05:30.",
                value,
            ),
            transformations,
        )

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return (
            None,
            ValidationIssue(
                "occurred_at",
                "timezone_required",
                "Timestamp must include a UTC offset; local time alone is ambiguous.",
                value,
            ),
            transformations,
        )

    normalized = parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if normalized != _text(value):
        transformations.append("normalized_timestamp_to_UTC")
    return normalized, None, transformations


def _parse_quantity(value: Any) -> tuple[Decimal | None, ValidationIssue | None]:
    raw = _text(value)
    if not raw:
        return None, ValidationIssue("quantity", "missing", "Quantity is required.")
    try:
        quantity = Decimal(raw)
    except InvalidOperation:
        return None, ValidationIssue("quantity", "not_numeric", "Quantity must be numeric.", value)
    if not quantity.is_finite():
        return None, ValidationIssue("quantity", "not_finite", "Quantity must be finite.", value)
    if quantity <= 0:
        return None, ValidationIssue("quantity", "out_of_range", "Quantity must be greater than zero.", value)
    if quantity > Decimal("1000000000"):
        return None, ValidationIssue(
            "quantity",
            "implausibly_large",
            "Quantity exceeds the safety limit of 1,000,000,000.",
            value,
        )
    return quantity.normalize(), None


def _normalize_unit(value: Any) -> tuple[str, list[str]]:
    unit = _text(value)
    alias = UNIT_ALIASES.get(unit.lower())
    if alias is None:
        return unit, []
    return alias, [f"normalized_unit:{unit}->{alias}"] if unit != alias else []


def validate_record(
    raw_record: dict[str, Any],
    provenance: Provenance,
    *,
    duplicate_id: bool = False,
) -> tuple[ActivityRecord | None, tuple[ValidationIssue, ...]]:
    """Validate and normalize one raw activity record."""
    issues: list[ValidationIssue] = []
    transformations = list(provenance.transformations)

    record_id = _text(raw_record.get("record_id"))
    if not record_id:
        issues.append(ValidationIssue("record_id", "missing", "Record ID is required."))
    elif len(record_id) > 100:
        issues.append(ValidationIssue("record_id", "too_long", "Record ID must be at most 100 characters."))
    elif duplicate_id:
        issues.append(ValidationIssue("record_id", "duplicate", "Record ID already appeared in this input.", record_id))

    occurred_at_utc, timestamp_issue, timestamp_changes = _parse_timestamp(raw_record.get("occurred_at"))
    transformations.extend(timestamp_changes)
    if timestamp_issue:
        issues.append(timestamp_issue)

    category = _text(raw_record.get("category")).lower()
    if not category:
        issues.append(ValidationIssue("category", "missing", "Category is required."))
    elif category not in ALLOWED_UNITS:
        issues.append(ValidationIssue("category", "unsupported_category", f"Choose one of: {', '.join(sorted(ALLOWED_UNITS))}.", category))

    activity = _text(raw_record.get("activity"))
    if not activity:
        issues.append(ValidationIssue("activity", "missing", "Activity is required."))
    elif len(activity) > 120:
        issues.append(ValidationIssue("activity", "too_long", "Activity must be at most 120 characters."))

    quantity, quantity_issue = _parse_quantity(raw_record.get("quantity"))
    if quantity_issue:
        issues.append(quantity_issue)

    unit, unit_changes = _normalize_unit(raw_record.get("unit"))
    transformations.extend(unit_changes)
    if not unit:
        issues.append(ValidationIssue("unit", "missing", "Unit is required."))
    elif category in ALLOWED_UNITS and unit not in ALLOWED_UNITS[category]:
        issues.append(ValidationIssue("unit", "unit_category_mismatch", f"Unit '{unit}' is not valid for category '{category}'.", unit))

    unknown_fields = sorted(set(raw_record) - KNOWN_FIELDS)
    if unknown_fields:
        transformations.append(f"ignored_unknown_fields:{','.join(unknown_fields)}")

    if issues:
        return None, tuple(issues)

    assert occurred_at_utc is not None
    assert quantity is not None
    normalized_provenance = Provenance(
        source_name=provenance.source_name,
        source_file=provenance.source_file,
        source_sha256=provenance.source_sha256,
        source_format=provenance.source_format,
        source_row=provenance.source_row,
        ingested_at_utc=provenance.ingested_at_utc,
        license_note=provenance.license_note,
        schema_version=provenance.schema_version,
        transformations=tuple(transformations),
    )
    return ActivityRecord(
        record_id=record_id,
        occurred_at_utc=occurred_at_utc,
        category=category,
        activity=activity,
        quantity=quantity,
        unit=unit,
        location=_optional_text(raw_record.get("location")),
        notes=_optional_text(raw_record.get("notes")),
        provenance=normalized_provenance,
    ), ()


def privacy_warnings(field_names: set[str]) -> list[str]:
    """Flag common direct identifiers without inspecting or exposing values."""
    found = sorted(name.lower() for name in field_names if name.lower() in SENSITIVE_FIELD_NAMES)
    if not found:
        return []
    return [
        "Potential direct-identifier columns detected: "
        f"{', '.join(found)}. Remove or pseudonymize them before committing data."
    ]
