import math
import os
import pytest
from csv_stats import parse_csv, compute_stats, summarize

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/iris_missing.csv")
NUMERIC_COLS = ["sepal_length", "sepal_width", "petal_length", "petal_width"]


class TestParseCsv:
    def test_returns_list_of_dicts(self):
        rows = parse_csv(DATA_PATH)
        assert isinstance(rows, list)
        assert len(rows) > 0
        assert isinstance(rows[0], dict)

    def test_expected_columns_present(self):
        rows = parse_csv(DATA_PATH)
        for col in NUMERIC_COLS + ["species"]:
            assert col in rows[0]

    def test_numeric_values_are_float(self):
        rows = parse_csv(DATA_PATH)
        for row in rows:
            for col in NUMERIC_COLS:
                val = row[col]
                assert val is None or isinstance(val, float)

    def test_empty_string_becomes_none(self):
        rows = parse_csv(DATA_PATH)
        # iris_missing.csv has missing values — at least one None must exist
        nones = [row[col] for row in rows for col in NUMERIC_COLS if row[col] is None]
        assert len(nones) > 0

    def test_species_is_string(self):
        rows = parse_csv(DATA_PATH)
        for row in rows:
            assert isinstance(row["species"], str)

    def test_row_count(self):
        rows = parse_csv(DATA_PATH)
        assert len(rows) == 150


class TestComputeStats:
    @pytest.fixture
    def rows(self):
        return parse_csv(DATA_PATH)

    def test_returns_dict_of_dicts(self, rows):
        stats = compute_stats(rows)
        assert isinstance(stats, dict)
        for col, s in stats.items():
            assert isinstance(s, dict)

    def test_stat_keys_present(self, rows):
        stats = compute_stats(rows)
        for col in stats:
            assert set(stats[col].keys()) >= {"mean", "median", "std", "missing"}

    def test_auto_detects_numeric_columns(self, rows):
        stats = compute_stats(rows)
        for col in NUMERIC_COLS:
            assert col in stats
        assert "species" not in stats

    def test_explicit_columns_respected(self, rows):
        stats = compute_stats(rows, columns=["sepal_length"])
        assert list(stats.keys()) == ["sepal_length"]

    def test_missing_count_is_int(self, rows):
        stats = compute_stats(rows)
        for col in stats:
            assert isinstance(stats[col]["missing"], int)

    def test_missing_count_nonnegative(self, rows):
        stats = compute_stats(rows)
        for col in stats:
            assert stats[col]["missing"] >= 0

    def test_mean_is_finite(self, rows):
        stats = compute_stats(rows)
        for col in stats:
            assert math.isfinite(stats[col]["mean"])

    def test_std_nonnegative(self, rows):
        stats = compute_stats(rows)
        for col in stats:
            assert stats[col]["std"] >= 0

    def test_known_missing_count(self, rows):
        # iris_missing.csv has at least one missing per numeric column;
        # total missing across all numeric cols must be > 0
        stats = compute_stats(rows)
        total_missing = sum(stats[col]["missing"] for col in NUMERIC_COLS)
        assert total_missing > 0

    def test_sepal_length_mean_approx(self, rows):
        # iris full dataset sepal_length mean ≈ 5.84; with a few missing it stays close
        stats = compute_stats(rows)
        assert abs(stats["sepal_length"]["mean"] - 5.84) < 0.5

    def test_empty_rows_raises_or_returns_empty(self):
        result = compute_stats([])
        assert result == {} or isinstance(result, dict)


class TestSummarize:
    def test_equivalent_to_parse_then_compute(self):
        direct = compute_stats(parse_csv(DATA_PATH))
        shortcut = summarize(DATA_PATH)
        assert direct.keys() == shortcut.keys()
        for col in direct:
            for stat in direct[col]:
                assert math.isclose(direct[col][stat], shortcut[col][stat], rel_tol=1e-9)

    def test_columns_filter_forwarded(self):
        stats = summarize(DATA_PATH, columns=["petal_length", "petal_width"])
        assert set(stats.keys()) == {"petal_length", "petal_width"}

    def test_returns_dict(self):
        result = summarize(DATA_PATH)
        assert isinstance(result, dict)
