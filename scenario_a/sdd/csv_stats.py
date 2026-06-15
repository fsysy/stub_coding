import csv
import math
import statistics


def parse_csv(path: str, encoding: str = "utf-8") -> list[dict]:
    rows = []
    with open(path, encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {}
            for k, v in row.items():
                stripped = v.strip()
                if stripped == "":
                    parsed[k] = None
                else:
                    try:
                        parsed[k] = float(stripped)
                    except ValueError:
                        parsed[k] = stripped
            rows.append(parsed)
    return rows


def compute_stats(
    rows: list[dict],
    columns: list[str] | None = None,
) -> dict[str, dict[str, float | int]]:
    if not rows:
        return {}

    if columns is None:
        columns = [k for k, v in rows[0].items() if isinstance(v, float) or v is None]
        # refine: keep only columns that have at least one float value
        columns = [
            c for c in columns
            if any(isinstance(r.get(c), float) for r in rows)
        ]

    result = {}
    for col in columns:
        values = [r[col] for r in rows if r.get(col) is not None]
        missing = sum(1 for r in rows if r.get(col) is None)
        if values:
            mean = sum(values) / len(values)
            median = statistics.median(values)
            std = statistics.pstdev(values)
        else:
            mean = median = std = float("nan")
        result[col] = {
            "mean": mean,
            "median": median,
            "std": std,
            "missing": missing,
        }
    return result


def summarize(path: str, columns: list[str] | None = None) -> dict[str, dict[str, float | int]]:
    return compute_stats(parse_csv(path), columns)
