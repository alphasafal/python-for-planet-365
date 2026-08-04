# Architecture

```text
CSV / JSON
    │
    ▼
format reader ──► source SHA-256 + field privacy scan
    │
    ▼
row validator
    ├── timestamp → UTC
    ├── category/unit compatibility
    ├── positive finite quantity
    ├── duplicate ID detection
    └── transformation log
    │
    ├── accepted_records.jsonl
    └── rejected_records.jsonl + explicit issues
                 │
                 ▼
        quality_report.json/.md
```

## Design decisions

- **Standard library only:** keeps Day 1 installable and teaches core Python.
- **Quarantine, never silent deletion:** every rejected row retains its raw values, row lineage and reasons.
- **Decimal quantities:** avoids introducing binary floating-point changes during ingestion.
- **UTC normalization:** prevents ambiguous comparisons across locations.
- **SHA-256 source fingerprint:** lets a reviewer verify which exact input produced a report.
- **No emission factors yet:** mixing ingestion and carbon accounting would hide assumptions and weaken auditability.
