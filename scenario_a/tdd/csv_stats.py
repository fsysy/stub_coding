import csv
from typing import Any


def parse_csv(path: str, encoding: str = "utf-8") -> list[dict]:
    """CSV 파일을 읽어 row별 dict 리스트로 반환. 숫자 변환 가능한 값은 float, 불가능하면 None."""
    rows: list[dict] = []
    with open(path, mode="r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed_row: dict[str, Any] = {}
            for key, value in row.items():
                if value == "":
                    parsed_row[key] = None
                else:
                    try:
                        parsed_row[key] = float(value)
                    except ValueError:
                        parsed_row[key] = value
            rows.append(parsed_row)
    return rows


import statistics
from typing import Callable


def compute_stats(
    rows: list[dict],
    columns: list[str] | None = None,
) -> dict[str, dict[str, float | int]]:
    """숫자형 컬럼별 mean, median, std, missing 수를 반환. columns=None이면 자동 감지."""
    if not rows:
        return {}

    # 자동 감지: 숫자형 컬럼만 선택
    if columns is None:
        columns = _detect_numeric_columns(rows)

    stats: dict[str, dict[str, float | int]] = {}
    for col in columns:
        values = [row[col] for row in rows if col in row]
        numeric_values = [v for v in values if isinstance(v, (int, float)) and v is not None]
        missing_count = sum(1 for v in values if v is None)

        if numeric_values:
            mean_val = statistics.mean(numeric_values)
            median_val = statistics.median(numeric_values)
            std_val = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0
        else:
            mean_val = 0.0
            median_val = 0.0
            std_val = 0.0

        stats[col] = {
            "mean": mean_val,
            "median": median_val,
            "std": std_val,
            "missing": missing_count,
        }

    return stats


def _detect_numeric_columns(rows: list[dict]) -> list[str]:
    """자동으로 숫자형 컬럼을 감지."""
    first_row = rows[0]
    numeric_cols: list[str] = []
    for col in first_row:
        sample_value = first_row[col]
        if isinstance(sample_value, (int, float)) or sample_value is None:
            numeric_cols.append(col)
    return numeric_cols


def summarize(path: str, columns: list[str] | None = None) -> dict[str, dict[str, float | int]]:
    """parse_csv + compute_stats 를 합친 편의 함수."""
    rows = parse_csv(path)
    return compute_stats(rows, columns)
