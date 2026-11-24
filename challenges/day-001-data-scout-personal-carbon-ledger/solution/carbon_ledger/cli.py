from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ingest import ingest_file
from .report import build_quality_report, write_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="carbon-ledger",
        description="Validate and normalize personal sustainability activity logs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a CSV or JSON activity log.")
    ingest_parser.add_argument("--input", required=True, type=Path, help="Path to CSV or JSON.")
    ingest_parser.add_argument("--output-dir", required=True, type=Path)
    ingest_parser.add_argument("--source-name", required=True)
    ingest_parser.add_argument("--license-note", required=True)
    ingest_parser.add_argument(
        "--fail-on-rejection",
        action="store_true",
        help="Return exit code 2 when one or more rows are rejected.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = ingest_file(
            args.input,
            source_name=args.source_name,
            license_note=args.license_note,
        )
        paths = write_outputs(result, args.output_dir)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = build_quality_report(result)
    rows = report["row_counts"]
    print(
        f"Ingested {rows['total']} rows: {rows['accepted']} accepted, {rows['rejected']} rejected."
    )
    print(f"Quality report: {paths['report_markdown']}")
    if args.fail_on_rejection and rows["rejected"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
