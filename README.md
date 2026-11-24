# Python for Planet — 365

A rigorous **one-real-problem-per-day** path for becoming a world-class Python engineer while building open-source tools for sustainability, nature and all 17 United Nations Sustainable Development Goals.

> The goal is not 365 shallow notebooks. The goal is a compounding engineering portfolio: every week moves from data acquisition to evidence, algorithms, visual communication, decision science, product delivery and impact audit.

## What is included

- 365 detailed challenge briefs
- 52 weekly sustainability domains plus a final public launch
- all 17 SDGs mapped across the programme
- a professional Python package scaffold
- tests, typing, linting and CI
- project, impact and case-study templates
- open-source contribution and public-growth playbooks
- official data-source catalogue

## Start

```bash
git clone https://github.com/alphasafal/python-for-planet-365.git
cd python-for-planet-365
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -e '.[dev]'
pre-commit install
pytest
```

Open [`ROADMAP.md`](ROADMAP.md), begin Day 001, and copy [`project_template`](project_template) into the corresponding challenge folder.

## Daily operating system (2–4 focused hours)

1. **Understand (20 min):** define the stakeholder, decision and primary metric.
2. **Research (20 min):** inspect data provenance and domain assumptions.
3. **Build (60–120 min):** implement the smallest trustworthy solution.
4. **Verify (30 min):** tests, edge cases, baseline comparison and sensitivity.
5. **Communicate (20 min):** README, chart/demo, impact note and honest limitations.
6. **Connect (10 min):** ask one practitioner or contributor for specific feedback.

## The weekly loop

| Day | Role | Output |
|---|---|---|
| 1 | Data Scout | reproducible ingestion and data-quality report |
| 2 | Evidence Builder | defensible baseline and uncertainty |
| 3 | Algorithm Engineer | tested reusable Python component |
| 4 | Visual Storyteller | accessible decision-ready visual/map |
| 5 | Decision Scientist | baseline plus model/ranking/optimisation |
| 6 | Product Builder | CLI/API/dashboard/package |
| 7 | Impact Auditor | reproducibility, ethics, release and contributor issue |

## World-class proof standard

Every serious project should contain:

- a clearly named real stakeholder and decision;
- source, licence, timestamp, schema and data limitations;
- a naive baseline before any advanced model;
- type hints, tests, logging, error handling and deterministic examples;
- evaluation connected to operational consequences;
- subgroup/spatial/temporal error analysis when relevant;
- an `IMPACT.md` separating measured impact from estimates and aspirations;
- a reproducible release, demo and invitation for domain review.

## SDG coverage

SDG 1: 28 days, SDG 2: 21 days, SDG 3: 49 days, SDG 4: 43 days, SDG 5: 14 days, SDG 6: 77 days, SDG 7: 42 days, SDG 8: 57 days, SDG 9: 127 days, SDG 10: 42 days, SDG 11: 140 days, SDG 12: 98 days, SDG 13: 225 days, SDG 14: 42 days, SDG 15: 56 days, SDG 16: 42 days, SDG 17: 64 days

See [`ROADMAP.md`](ROADMAP.md) for the week-by-week project list.

## Recommended Python baseline

Use Python 3.12+ and continuously test supported versions. The starter CI tests 3.12, 3.13 and 3.14. Keep the core package lightweight; add geospatial, ML or dashboard dependencies only inside the project that needs them.

## Repository map

```text
.
├── challenges/               # 365 detailed problem statements
├── docs/                     # impact, ethics, portfolio and growth guides
├── project_template/         # copy into each day/project
├── src/planet365/            # reusable shared utilities
├── tests/                    # shared package tests
├── challenge_index.csv       # filter/sort all days
├── challenge_index.json      # machine-readable challenge catalogue
├── ROADMAP.md                # complete human-readable roadmap
├── pyproject.toml
└── .github/workflows/ci.yml
```

## Rules that protect your credibility

- Never invent impact numbers.
- Never hide missing data or failed experiments.
- Never expose personal data or sensitive ecological locations.
- Never optimise a proxy without checking who may be harmed.
- Never call a model “AI for good” without a stakeholder, baseline and verification path.
- Prefer a small deployed tool over a giant unvalidated platform.

## Licence

MIT for code. Dataset licences remain with their original publishers; do not redistribute data unless permitted.
