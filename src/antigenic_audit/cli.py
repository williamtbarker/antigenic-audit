"""Command-line interface."""

from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Sequence
from dataclasses import fields
from pathlib import Path

from antigenic_audit import __version__
from antigenic_audit.audit import audit_records
from antigenic_audit.io import InputError, load_records
from antigenic_audit.models import AuditConfig, ColumnSpec
from antigenic_audit.render import render_json, render_markdown


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="antigenic-audit",
        description=(
            "Audit pairwise influenza antigenicity evaluations for role leakage and "
            "temporal overclaiming."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit", help="audit a CSV/TSV pair table")
    audit.add_argument("input", type=Path, help="CSV/TSV input; .gz is supported")
    audit.add_argument("-o", "--output", type=Path, help="write report instead of stdout")
    audit.add_argument("--format", choices=("markdown", "json"), default="markdown")
    audit.add_argument(
        "--policy",
        choices=("prospective", "strain-holdout", "pair-holdout", "cold-both"),
        default="prospective",
        help="deployment claim to enforce (default: prospective)",
    )
    audit.add_argument(
        "--fail-on",
        choices=("error", "warning"),
        default="error",
        help="minimum severity that returns exit code 2",
    )
    audit.add_argument("--max-examples", type=int, default=10)
    audit.add_argument("--train-label", default="train")
    audit.add_argument("--validation-label", default="validation")
    audit.add_argument("--test-label", default="test")
    for data_field in fields(ColumnSpec):
        field_name = data_field.name
        default = getattr(ColumnSpec(), field_name)
        audit.add_argument(
            f"--{field_name.replace('_', '-')}-column",
            default=default,
            metavar="NAME",
        )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a documented process exit code."""
    args = _parser().parse_args(argv)
    if args.max_examples < 1:
        print("error: --max-examples must be at least 1", file=sys.stderr)
        return 1

    train_label = args.train_label.strip().casefold()
    validation_label = args.validation_label.strip().casefold()
    test_label = args.test_label.strip().casefold()
    labels = {train_label, validation_label, test_label}
    if "" in labels:
        print("error: train, validation, and test labels must not be empty", file=sys.stderr)
        return 1
    if len(labels) != 3:
        print("error: train, validation, and test labels must be distinct", file=sys.stderr)
        return 1

    columns = ColumnSpec(
        split=args.split_column.strip(),
        virus_id=args.virus_id_column.strip(),
        antiserum_id=args.antiserum_id_column.strip(),
        virus_year=args.virus_year_column.strip(),
        antiserum_year=args.antiserum_year_column.strip(),
        observed=args.observed_column.strip(),
        predicted=args.predicted_column.strip(),
    )
    try:
        records = load_records(args.input, columns, allowed_splits=labels)
        config = AuditConfig(
            policy=args.policy,
            train_label=train_label,
            validation_label=validation_label,
            test_label=test_label,
            max_examples=args.max_examples,
        )
        report = audit_records(records, config)
    except (csv.Error, InputError, OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    rendered = render_json(report) if args.format == "json" else render_markdown(report)
    if args.output:
        try:
            if args.output.resolve() == args.input.resolve():
                raise ValueError("output path must not overwrite the input table")
            args.output.write_text(rendered, encoding="utf-8")
        except (OSError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    else:
        print(rendered, end="")

    if report.outcome == "FAIL":
        return 2
    if args.fail_on == "warning" and report.outcome == "WARN":
        return 2
    return 0


def entrypoint() -> None:
    """Console-script entry point."""
    raise SystemExit(main())
