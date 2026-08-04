# Impact Note — Day 1

- **Stakeholder:** Individual learners, student sustainability clubs and future project contributors.
- **Decision:** Whether an activity record is sufficiently valid and traceable to enter later carbon analysis.
- **Scope:** Synthetic personal activity fixtures covering transport, electricity, food, waste and purchases.
- **Primary metric:** Percentage of input rows accepted under schema 1.0.0, with every rejected row explained.
- **Baseline:** An ordinary spreadsheet/manual log has no enforced schema, source fingerprint, UTC normalization or machine-readable rejection trail.
- **Project result:** The valid CSV fixture accepts 8/8 rows. The deliberately mixed fixture accepts 2/8 and quarantines 6/8 with explicit error codes. These are software verification results, not environmental outcomes.
- **Uncertainty:** Acceptance depends on the declared schema; a valid row can still contain an inaccurate self-reported quantity.
- **Observed deployment evidence:** None. The project has only been exercised on synthetic fixtures.
- **Who may benefit:** Learners and small sustainability teams needing a defensible starting dataset.
- **Who may be harmed or excluded:** People whose activities do not fit the initial categories or units; users exposing private information in personal logs.
- **Safeguards:** Identifier-column warnings, coarse-location guidance, rejected-row quarantine and no automatic carbon claims.
- **Limitations:** No emissions factors, no lifecycle assessment, no external-data verification and no causal impact estimate.
- **Verification owner/date:** Safal Gupta — 2026-08-04.
- **Next experiment:** Collect a consented seven-day activity log, review schema gaps, and design Day 2's baseline analysis with explicit factor provenance.
