# 코드 품질 평가 — Scenario B (DNA 서열 분석기)

도구: Ruff (린팅) + Radon CC/MI/Halstead (복잡도)
대상: `dna_analyzer.py` 구현 파일 (테스트 파일 제외)

---

## 1. Ruff — 린팅

| 항목 | SDD | TDD (pi/Qwen3.5) |
|------|-----|-----------------|
| 오류 수 | **0** | **0** |

**판정**: 둘 다 클린. Scenario A에서 TDD가 3오류 냈던 것과 대조적.

---

## 2. Radon CC — 순환 복잡도

| 함수 | SDD | TDD |
|------|-----|-----|
| `parse_fasta` | A (5) | A (5) |
| `gc_content` | A (4) | A (2) |
| `reverse_complement` | A (2) | A (2) |
| `find_orfs` | **A (1)** | A (2) |
| `_find_orfs_on_strand` | — | B (6) |
| **평균** | **A (3.0)** | **A (3.4)** |

**주의**: SDD `find_orfs` CC=1은 착시. 복잡한 로직이 내부 중첩함수 `_scan`에 숨어 있어 Radon이 카운트 못함.
TDD는 `_find_orfs_on_strand`를 모듈 레벨 함수로 분리해서 CC가 투명하게 드러남.

**판정**: 수치상 SDD 소폭 우위지만, 실질 복잡도는 TDD가 더 정직하게 표현됨.

---

## 3. Radon MI — 유지보수성 지수

| | SDD | TDD |
|--|-----|-----|
| MI 점수 | 59.49 (A) | **65.35 (A)** |

**판정**: TDD 우위. Scenario A와 반대. TDD(pi)가 더 유지보수하기 쉬운 코드를 생성.

---

## 4. Radon Halstead — 할스테드 복잡도

| 지표 | SDD | TDD | 승자 |
|------|-----|-----|------|
| Volume | 325.0 | 295.1 | **TDD** |
| Difficulty | 8.41 | 5.85 | **TDD** |
| Effort | 2,734 | 1,725 | **TDD** |
| 예상 버그 수 | 0.108 | 0.098 | **TDD** |

**판정**: TDD 전면 우위. Scenario A와 완전히 반대.
SDD의 클로저 기반 `_scan`이 변수 포착으로 인해 난이도/볼륨을 올림.
TDD의 `_find_orfs_on_strand` 분리가 Halstead 기준으로 더 단순한 구조.

---

## 코드 설계 차이점

| 항목 | SDD | TDD |
|------|-----|-----|
| ORF 탐색 구조 | `find_orfs` 내부에 중첩함수 `_scan` | `_find_orfs_on_strand` 모듈 레벨 분리 |
| FASTA 헤더 파싱 | `line[1:]` — 전체 헤더 보존 | `line[1:].split()[0]` — ID만 추출 |
| 서열 처리 방식 | 스트리밍 (line by line) | 전체 로드 후 처리 |
| N 염기 처리 | 미처리 (변환 안 됨) | `complement`에 N→N 명시 |

**헤더 파싱 차이**: TDD가 `split()[0]`으로 ID만 취하는 게 생물정보학 관례상 더 정확함.
실제 FASTA 헤더는 `>NM_000546.6 Homo sapiens tumor protein...` 형태라 설명부가 붙음.

---

## 종합 요약

| 평가 항목 | SDD | TDD (pi) | 승자 |
|-----------|-----|----------|------|
| Ruff 오류 | 0 | 0 | 동점 |
| CC 평균 | 3.0 | 3.4 | SDD (미미) |
| MI 점수 | 59.49 | **65.35** | **TDD** |
| Halstead Effort | 2,734 | **1,725** | **TDD** |
| 예상 버그 수 | 0.108 | **0.098** | **TDD** |
| 도메인 정확성 | △ (헤더 전체) | ✓ (ID 추출) | **TDD** |

**Scenario B 코드 품질은 TDD(pi)가 우위.**
Scenario A에서 Claude가 압도했던 것과 정반대 결과.
pi가 DNA 도메인에서는 더 관용적인 설계(헬퍼 분리, N 처리, FASTA ID 추출)를 선택함.
