"""End-to-end CLI tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from antigenic_audit.cli import main


def test_clean_example_exits_zero() -> None:
    root = Path(__file__).parents[1]
    assert main(["audit", str(root / "examples" / "clean_pairs.csv")]) == 0


def test_leaky_example_exits_two(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    report = tmp_path / "report.json"
    result = main(
        [
            "audit",
            str(root / "examples" / "leaky_pairs.csv"),
            "--format",
            "json",
            "--output",
            str(report),
        ]
    )
    assert result == 2
    assert json.loads(report.read_text(encoding="utf-8"))["outcome"] == "FAIL"


def test_warning_can_fail_ci(tmp_path: Path) -> None:
    table = tmp_path / "warning.csv"
    table.write_text(
        "split,virus_id,antiserum_id,virus_year,antiserum_year,observed,predicted\n"
        "train,v1,s1,2000,1999,1,1\n"
        "test,v2,s2,2002,2003,2,2\n",
        encoding="utf-8",
    )
    assert main(["audit", str(table)]) == 0
    assert main(["audit", str(table), "--fail-on", "warning"]) == 2


def test_invalid_flag_value_exits_one() -> None:
    root = Path(__file__).parents[1]
    assert (
        main(
            [
                "audit",
                str(root / "examples" / "clean_pairs.csv"),
                "--max-examples",
                "0",
            ]
        )
        == 1
    )


def test_custom_columns_and_split_labels(tmp_path: Path) -> None:
    table = tmp_path / "custom.csv"
    table.write_text(
        "set,target,serum,target_year,serum_year,y,yhat\n"
        "fit,v1,s1,2000,1999,1,1.1\n"
        "eval,v2,s1,2002,1999,2,1.9\n",
        encoding="utf-8",
    )
    args = [
        "audit",
        str(table),
        "--train-label",
        " FIT ",
        "--validation-label",
        "tune",
        "--test-label",
        "EVAL",
        "--split-column",
        "set",
        "--virus-id-column",
        "target",
        "--antiserum-id-column",
        "serum",
        "--virus-year-column",
        "target_year",
        "--antiserum-year-column",
        "serum_year",
        "--observed-column",
        "y",
        "--predicted-column",
        "yhat",
    ]
    assert main(args) == 0


def test_input_cannot_be_overwritten(tmp_path: Path) -> None:
    table = tmp_path / "pairs.csv"
    table.write_text(
        "split,virus_id,antiserum_id,virus_year,antiserum_year,observed,predicted\n"
        "train,v1,s1,2000,1999,1,1\n"
        "test,v2,s1,2002,1999,2,2\n",
        encoding="utf-8",
    )
    original = table.read_text(encoding="utf-8")
    assert main(["audit", str(table), "--output", str(table)]) == 1
    assert table.read_text(encoding="utf-8") == original


@pytest.mark.parametrize(
    "args",
    [
        ["--train-label", " "],
        ["--train-label", "test"],
        ["--virus-id-column", "virus_id", "--antiserum-id-column", "virus_id"],
    ],
)
def test_invalid_label_or_column_configuration_exits_one(args: list[str]) -> None:
    root = Path(__file__).parents[1]
    assert main(["audit", str(root / "examples" / "clean_pairs.csv"), *args]) == 1


def test_unwritable_output_exits_one(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    missing_parent = tmp_path / "missing" / "report.md"
    assert (
        main(
            [
                "audit",
                str(root / "examples" / "clean_pairs.csv"),
                "--output",
                str(missing_parent),
            ]
        )
        == 1
    )
