아래 스펙에 맞게 구현하라.
- `scenario_a/sdd/csv_stats.py` : 실제 구현 코드
- `scenario_a/sdd/test_csv_stats.py` : pytest 테스트 (assert 포함)

테스트가 모두 통과해야 완료. 작업 디렉토리는 `/data/script/fsysy/test_anything/stub_coding` 이다.

---

# Spec A — CSV 파서 + 통계 요약기

## 목적
CSV 파일을 읽어 숫자형 컬럼별 통계 요약을 반환한다.

## 데이터
- 파일: `data/iris_missing.csv`
- 컬럼: `sepal_length`, `sepal_width`, `petal_length`, `petal_width` (float), `species` (str)
- 숫자형 결측치는 빈 문자열 `""` 로 표현됨

## 함수 명세

```python
def parse_csv(path: str, encoding: str = "utf-8") -> list[dict]:
    """CSV 파일을 읽어 row별 dict 리스트로 반환. 숫자 변환 가능한 값은 float, 불가능하면 None."""

def compute_stats(
    rows: list[dict],
    columns: list[str] | None = None
) -> dict[str, dict[str, float | int]]:
    """숫자형 컬럼별 mean, median, std, missing 수를 반환. columns=None이면 자동 감지."""

def summarize(path: str, columns: list[str] | None = None) -> dict[str, dict[str, float | int]]:
    """parse_csv + compute_stats 를 합친 편의 함수."""
```
