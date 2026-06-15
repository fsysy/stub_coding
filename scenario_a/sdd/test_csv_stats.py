import math
import pytest
from pathlib import Path

from scenario_a.sdd.csv_stats import parse_csv, compute_stats, summarize

DATA = str(Path(__file__).parents[2] / "data" / "iris_missing.csv")

NUMERIC_COLS = ["sepal_length", "sepal_width", "petal_length", "petal_width"]


# ---------- parse_csv ----------

def test_parse_csv_row_count():
    rows = parse_csv(DATA)
    assert len(rows) == 150


def test_parse_csv_float_conversion():
    rows = parse_csv(DATA)
    for row in rows:
        for col in NUMERIC_COLS:
            assert row[col] is None or isinstance(row[col], float)


def test_parse_csv_none_for_missing():
    rows = parse_csv(DATA)
    none_counts = {col: sum(1 for r in rows if r[col] is None) for col in NUMERIC_COLS}
    # at least one missing per numeric column
    assert any(v > 0 for v in none_counts.values())


def test_parse_csv_species_is_string():
    rows = parse_csv(DATA)
    for row in rows:
        assert isinstance(row["species"], str)


# ---------- compute_stats ----------

def test_compute_stats_keys():
    rows = parse_csv(DATA)
    stats = compute_stats(rows)
    for col in NUMERIC_COLS:
        assert col in stats
        assert set(stats[col].keys()) == {"mean", "median", "std", "missing"}


def test_compute_stats_missing_count():
    rows = parse_csv(DATA)
    stats = compute_stats(rows, columns=NUMERIC_COLS)
    total_missing = sum(stats[c]["missing"] for c in NUMERIC_COLS)
    assert total_missing > 0


def test_compute_stats_mean_reasonable():
    rows = parse_csv(DATA)
    stats = compute_stats(rows)
    # iris sepal_length mean is ~5.8
    assert 4.0 < stats["sepal_length"]["mean"] < 8.0


def test_compute_stats_std_nonnegative():
    rows = parse_csv(DATA)
    stats = compute_stats(rows)
    for col in NUMERIC_COLS:
        assert stats[col]["std"] >= 0


def test_compute_stats_explicit_columns():
    rows = parse_csv(DATA)
    stats = compute_stats(rows, columns=["sepal_length"])
    assert list(stats.keys()) == ["sepal_length"]


def test_compute_stats_empty_rows():
    assert compute_stats([]) == {}


def test_compute_stats_all_missing():
    rows = [{"x": None}, {"x": None}]
    stats = compute_stats(rows, columns=["x"])
    assert stats["x"]["missing"] == 2
    assert math.isnan(stats["x"]["mean"])


# ---------- summarize ----------

def test_summarize_matches_pipeline():
    rows = parse_csv(DATA)
    expected = compute_stats(rows)
    result = summarize(DATA)
    for col in NUMERIC_COLS:
        assert pytest.approx(result[col]["mean"]) == expected[col]["mean"]
        assert result[col]["missing"] == expected[col]["missing"]


def test_summarize_with_columns():
    result = summarize(DATA, columns=["petal_length", "petal_width"])
    assert set(result.keys()) == {"petal_length", "petal_width"}
