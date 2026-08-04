.PHONY: install test lint typecheck sample verify

install:
	python -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check .

typecheck:
	mypy solution/carbon_ledger

sample:
	carbon-ledger ingest --input data/raw/sample_activities.csv --output-dir reports/sample-run --source-name "Day 1 synthetic activity log" --license-note "CC0 synthetic fixture created for this project"

verify: lint typecheck test sample
