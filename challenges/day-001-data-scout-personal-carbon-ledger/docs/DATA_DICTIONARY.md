# Data Dictionary — Activity Ledger Schema 1.0.0

| Field | Type | Required | Rule | Example |
|---|---|---:|---|---|
| `record_id` | string | yes | Unique within one input; 1–100 characters | `act-001` |
| `occurred_at` | ISO 8601 timestamp | yes | Must include UTC offset | `2026-08-04T08:30:00+05:30` |
| `category` | enum | yes | `transport`, `electricity`, `food`, `waste`, `purchase` | `transport` |
| `activity` | string | yes | Human-readable; 1–120 characters | `City bus commute` |
| `quantity` | decimal | yes | Finite, greater than 0, at most 1 billion | `12.5` |
| `unit` | enum | yes | Must be compatible with category | `km` |
| `location` | string | no | Coarse place only; avoid exact home addresses | `Vellore` |
| `notes` | string | no | Context, measurement method or uncertainty note | `Measured by meter` |

## Category/unit compatibility

| Category | Accepted units |
|---|---|
| transport | `km`, `passenger_km`, `litre` |
| electricity | `kWh` |
| food | `kg`, `serving`, `item` |
| waste | `kg` |
| purchase | `INR`, `item`, `kg` |

## Normalized output additions

Every accepted row receives:

- `occurred_at_utc`, normalized to UTC;
- source file name and SHA-256 digest;
- source format and source row number;
- ingestion timestamp;
- dataset source name and licence/terms note;
- schema version and transformation history.

## What this dataset cannot prove

An activity log cannot prove a person's complete carbon footprint, causal environmental impact, avoided emissions, or the accuracy of future emission factors. Self-reported records may be incomplete or biased, quantities may be estimated, and coarse categories omit lifecycle details. This Day 1 pipeline establishes traceability and data fitness only. Emissions calculation requires geography-, year-, technology- and methodology-specific factors with uncertainty, which belongs in later project days.
