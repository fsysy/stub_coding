# 실험 레포트 — Scenario A (CSV 파서 + 통계 요약기)

## 토큰 사용량 비교

| 항목 | SDD-A | TDD-A | 차이 |
|------|-------|-------|------|
| input tokens | 353 | 53 | **TDD -85%** |
| output tokens | 2,500 | 2,500 | 동일 |
| cache read | 183,200 | 124,200 | TDD -32% |
| cache write | 26,300 | 12,700 | TDD -52% |
| total cost | $0.2512 | $0.1512 | **TDD -$0.10 (-40%)** |
| pytest 통과 | 13/13 | 20/20 | 둘 다 통과 |

> **핵심**: input 토큰이 TDD에서 85% 적음. Claude가 구현 코드를 읽고 생성하는 과정이 없기 때문.
> output 토큰은 동일 — Claude가 생성한 텍스트 양(스텁+테스트 vs 구현+테스트)이 비슷하다는 의미.

---

## 구현 코드 평가

### SDD-A (`csv_stats.py`, 60줄)

**강점:**
- 간결하고 읽기 쉬움
- `statistics.pstdev` 사용 (population std, 수학적으로 일반적인 선택)
- 전체 결측 컬럼에 `float("nan")` 반환 → 명시적인 예외 표현
- import 순서 깔끔

**약점:**
- `columns` 자동 감지 시 첫 row 기준으로 컬럼 타입 추측 → None이 많은 컬럼 제외 가능성

---

### TDD-A (`csv_stats.py`, 79줄) — pi/Qwen3.5 작성

**강점:**
- `_detect_numeric_columns` 헬퍼 분리로 단일 책임 명확
- 타입 힌트 꼼꼼하게 명시

**약점:**
- `from typing import Callable` 미사용 import 존재 (코드 노이즈)
- `statistics.stdev` 사용 (sample std, ddof=1) — SDD와 다른 공식
- 전체 결측 컬럼에 `0.0` 반환 → NaN보다 의미가 모호함
- import가 파일 중간에 추가됨 (구조 불량)
- `_detect_numeric_columns`가 첫 row만 보는 동일 문제

---

## 테스트 코드 평가

| 항목 | SDD-A | TDD-A |
|------|-------|-------|
| 테스트 수 | 13개 | 20개 |
| 코드 라인 | 100줄 | 123줄 |
| 스타일 | 함수형 (flat) | 클래스 기반 |
| 커버리지 깊이 | 중 | 중~상 |

### SDD 테스트 특징
- `test_compute_stats_all_missing` → NaN 반환 검증 (엣지케이스 정확히 포착)
- 전반적으로 필요한 것만 간결하게

### TDD 테스트 특징
- `test_auto_detects_numeric_columns`에서 `"species" not in stats` 명시적 검증 (SDD에 없는 케이스)
- `test_empty_rows_raises_or_returns_empty`가 `result == {} or isinstance(result, dict)` — 사실상 모든 경우 통과하는 약한 검증
- `test_mean_is_finite`은 TDD 구현(0.0 반환)에 맞춰져 있어 SDD(NaN 반환)와 비호환

---

## 관찰 사항

### 1. std 계산 방식 불일치
SDD는 `pstdev` (population), TDD는 `stdev` (sample). 스펙에 명시하지 않아서 각자 다른 선택을 했음.
동일한 데이터에서 결과값이 달라짐. **High 수준 스펙에서도 이런 해석 차이는 발생한다.**

### 2. 결측 전체 컬럼 처리 불일치
SDD: `NaN` / TDD: `0.0`. 의미상으로는 NaN이 더 정확하나 TDD 테스트가 `isfinite` 검증을 하고 있어 교차 호환 불가.

### 3. output 토큰이 동일한 이유
TDD에서 Claude는 스텁(짧음) + 테스트(많음)을 작성. SDD에서 Claude는 구현(많음) + 테스트(많음)을 작성.
결과적으로 Claude가 생성한 총 텍스트 양은 비슷하게 수렴함.
**토큰 절감은 output이 아니라 input에서 발생** — 구현 코드를 Claude context가 읽지 않아서.

---

## 결론 (Scenario A)

- **비용 측면**: TDD가 40% 저렴 ($0.15 vs $0.25)
- **코드 품질**: SDD가 소폭 우위 (간결, NaN 처리 명확, import 정리)
- **테스트 품질**: TDD가 케이스 수 많으나 일부 약한 assertion 존재
- **호환성**: 두 구현이 std 공식, 결측 처리 방식이 달라 상호 교체 불가
