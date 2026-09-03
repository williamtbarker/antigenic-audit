"""Input validation and compressed-table tests."""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest

from antigenic_audit.io import InputError, load_records
from antigenic_audit.models import ColumnSpec

HEADER = "split,virus_id,antiserum_id,virus_year,antiserum_year,observed,predicted\n"


def test_load_csv(tmp_path: Path) -> None:
    table = tmp_path / "pairs.csv"
    table.write_text(HEADER + "train,v1,s1,2000,1999,2.0,2.1\n", encoding="utf-8")
    records = load_records(table)
    assert len(records) == 1
    assert records[0].virus_id == "v1"
    assert records[0].observed == 2.0


def test_utf8_bom_and_blank_rows_are_accepted(tmp_path: Path) -> None:
    table = tmp_path / "pairs.csv"
    table.write_text(
        "\ufeff" + HEADER + "\ntrain,v1,s1,2000,1999,2.0,2.1\n",
        encoding="utf-8",
    )
    assert load_records(table)[0].virus_id == "v1"


def test_load_gzipped_tsv(tmp_path: Path) -> None:
    table = tmp_path / "pairs.tsv.gz"
    body = HEADER.replace(",", "\t") + "test\tv2\ts1\t2002\t1999\t3.0\t2.9\n"
    with gzip.open(table, mode="wt", encoding="utf-8", newline="") as handle:
        handle.write(body)
    records = load_records(table)
    assert records[0].split == "test"
    assert records[0].virus_year == 2002


def test_custom_columns(tmp_path: Path) -> None:
    table = tmp_path / "custom.csv"
    table.write_text(
        "set,target,serum,target_year,serum_year,y,yhat\ntrain,v1,s1,2000,1999,2.0,2.1\n",
        encoding="utf-8",
    )
    spec = ColumnSpec(
        split="set",
        virus_id="target",
        antiserum_id="serum",
        virus_year="target_year",
        antiserum_year="serum_year",
        observed="y",
        predicted="yhat",
    )
    assert load_records(table, spec)[0].antiserum_id == "s1"


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("split,virus_id\ntrain,v1\n", "missing required columns"),
        (HEADER.replace("virus_id", "split", 1), "duplicate column names"),
        (HEADER + "train,v1,s1,2000,1999,2,2,extra\n", "more values"),
        (HEADER + "train,,s1,2000,1999,2,2\n", "virus_id is empty"),
        (HEADER + "train,v1,,2000,1999,2,2\n", "antiserum_id is empty"),
        (HEADER + "holdout,v1,s1,2000,1999,2,2\n", "unknown split"),
        (HEADER + "train,v1,s1,not-a-year,1999,2,2\n", "integer year"),
        (HEADER + "train,v1,s1,1799,1999,2,2\n", "outside 1800..2200"),
        (HEADER + "train,v1,s1,2000,1999,2,nope\n", "must be numeric"),
        (HEADER + "train,v1,s1,2000,1999,nan,2\n", "must be finite"),
        (HEADER, "no data records"),
    ],
)
def test_invalid_input_fails_loudly(tmp_path: Path, body: str, message: str) -> None:
    table = tmp_path / "bad.csv"
    table.write_text(body, encoding="utf-8")
    with pytest.raises(InputError, match=message):
        load_records(table)


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(InputError, match="does not exist"):
        load_records(tmp_path / "absent.csv")


@pytest.mark.parametrize(
    "columns",
    [ColumnSpec(split=""), ColumnSpec(virus_id="split")],
)
def test_invalid_column_spec_is_rejected(tmp_path: Path, columns: ColumnSpec) -> None:
    table = tmp_path / "pairs.csv"
    table.write_text(HEADER + "train,v1,s1,2000,1999,2,2\n", encoding="utf-8")
    with pytest.raises(InputError, match="column names"):
        load_records(table, columns)


def test_empty_allowed_split_set_is_rejected(tmp_path: Path) -> None:
    table = tmp_path / "pairs.csv"
    table.write_text(HEADER + "train,v1,s1,2000,1999,2,2\n", encoding="utf-8")
    with pytest.raises(InputError, match="split labels"):
        load_records(table, allowed_splits=set())
