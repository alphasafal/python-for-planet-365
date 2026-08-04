.PHONY: install test lint format check

install:
	python -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check .
	mypy

format:
	ruff check --fix .
	ruff format .

check: lint test
