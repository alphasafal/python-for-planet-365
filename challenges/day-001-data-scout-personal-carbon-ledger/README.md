# Day 001 — Personal Carbon Ledger Data Scout

A production-minded Python ingestion pipeline for personal sustainability activity logs. It accepts CSV and JSON, validates the schema, normalizes timestamps and units, preserves source provenance, quarantines invalid rows, and creates machine- and human-readable data-quality reports.

**SDGs:** 12 — Responsible Consumption and Production; 13 — Climate Action.

## Why this problem matters

Carbon dashboards are only as trustworthy as the records entering them. A spreadsheet can contain ambiguous local times, incompatible units, duplicate rows, impossible quantities and no source lineage. Calculating emissions on top of those errors creates precise-looking but unreliable results.

Day 1 therefore solves the first real problem: **make the activity data auditable before estimating impact**.

## Stakeholder and decision

- **Users:** individuals, student climate clubs and open-source contributors.
- **Decision:** accept a row into later analysis or quarantine it for correction.
- **Primary metric:** accepted and rejected rows, with explicit reasons and traceable provenance.

## Features

- CSV and JSON ingestion
- ISO 8601 timestamps with mandatory timezone offsets
- UTC normalization
- category/unit compatibility rules
- positive finite decimal quantities
- duplicate record-ID detection
- safe unit aliases such as `kms → km` and `kwh → kWh`
- SHA-256 source fingerprint
- row-level source and transformation history
- direct-identifier column warnings
- accepted and rejected JSONL outputs
- JSON and Markdown quality reports
- strict optional CLI exit code for CI/data contracts
- 15+ tests covering valid, malformed, boundary, privacy and CLI behaviour

## Repository structure

```text
.
├── data/raw/                       # synthetic allowed fixtures
├── docs/
│   ├── ARCHITECTURE.md
│   └── DATA_DICTIONARY.md
├── reports/sample-run/             # reproducible generated evidence
├── solution/carbon_ledger/
│   ├── cli.py
│   ├── ingest.py
│   ├── models.py
│   ├── report.py
│   └── schema.py
├── tests/
├── IMPACT.md
└── pyproject.toml
```

## Run locally

From this Day 1 folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy solution/carbon_ledger
```

Ingest the clean CSV fixture:

```bash
carbon-ledger ingest \
  --input data/raw/sample_activities.csv \
  --output-dir reports/sample-run \
  --source-name "Day 1 synthetic activity log" \
  --license-note "CC0 synthetic fixture created for this project"
```

Test the quarantine path:

```bash
carbon-ledger ingest \
  --input data/raw/mixed_quality_activities.csv \
  --output-dir reports/mixed-run \
  --source-name "Day 1 mixed-quality fixture" \
  --license-note "CC0 synthetic fixture created for this project" \
  --fail-on-rejection
```

The second command intentionally exits with code `2` because invalid rows exist.

## Output contract

- `accepted_records.jsonl`: normalized rows allowed into later analysis
- `rejected_records.jsonl`: raw rows, lineage and one or more validation issues
- `quality_report.json`: automation-friendly metrics
- `quality_report.md`: reviewer-friendly summary

Read [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) before adding data.

## Acceptance criteria status

- [x] CSV and JSON inputs
- [x] required fields, units, ranges, timestamps and missing-value validation
- [x] source, ingestion time, licence note and transformation history
- [x] more than five unit tests including malformed and boundary inputs
- [x] data dictionary and clear statement of what the dataset cannot prove
- [x] generated evidence under `reports/`
- [x] impact note separating software results from environmental outcomes

## Responsible use

Do not commit real names, email addresses, phone numbers, exact home addresses or device identifiers. Use coarse locations, obtain consent for personal logs, and follow the original dataset's licence. Passing this validator does not prove that a reported activity is true.

## Next step

Day 2 will calculate a transparent baseline only after choosing documented emission factors, units, geography, year and uncertainty rules.
