# Stub-Coding TDD vs SDD — Claude 토큰 비용 비교 실험

## 개요

두 가지 코딩 방식에서 **Claude가 소비하는 토큰 비용**과 **코드 품질**을 비교하는 실험 프로젝트.

| 방식 | 설명 |
|------|------|
| **SDD** (Spec-Driven Development) | 스펙 → Claude(Sonnet 4.6)가 테스트 + 구현 전부 작성 |
| **Stub-Coding TDD** | 스펙 → **Claude(Sonnet 4.6)가 스텁 + pytest 테스트 작성** → **Local LLM(pi/Qwen3.5)이 스텁을 채워 구현** |

> **핵심 구조**: TDD 방식에서 Claude는 인터페이스 설계(스텁)와 테스트만 담당하고,
> 실제 로직 구현은 로컬에서 실행되는 Qwen3.5(pi agent)가 pytest를 통과할 때까지 반복 수행.

---

## 토큰 비용 실험 결과

| 세션 | 비용 | pytest |
|------|------|--------|
| SDD-A (CSV 통계) | $0.2512 | 13/13 통과 |
| TDD-A (CSV 통계) | **$0.1512** | 20/20 통과 |
| SDD-B (DNA 분석) | $0.2740 | 21/21 통과 |
| TDD-B (DNA 분석) | **$0.2479** | 29/29 통과 |

- Scenario A: TDD **40% 저렴**
- Scenario B: TDD **9.5% 저렴**

> 전체 수치 → [`results.md`](results.md) / 종합 분석 → [`report_final.md`](report_final.md)

---

## 코드 품질 실험 결과

구현 파일(`csv_stats.py`, `dna_analyzer.py`)만 대상. Ruff 린팅 + Radon(CC/MI/Halstead) 측정.

| 지표 | Scenario A (CSV) | Scenario B (DNA) |
|------|-----------------|-----------------|
| Ruff 오류 | SDD 1개 / TDD 3개 → **SDD 우위** | 둘 다 0개 → **동점** |
| 순환 복잡도(CC) | TDD 소폭 우위 (5.75 vs 7.0) | SDD 소폭 우위* (3.0 vs 3.4) |
| 유지보수성(MI) | **SDD 우위** (56.75 vs 51.03) | **TDD 우위** (65.35 vs 59.49) |
| Halstead Effort | **SDD 압도** (359 vs 799, 2.2×) | **TDD 우위** (1,725 vs 2,734) |

*SDD-B CC=3.0은 중첩함수 `_scan`에 복잡도가 숨어 Radon이 카운트 못하는 착시.

**결론**: 코드 품질은 도메인이 아닌 **경우에 따라 달라진다.** A에서 SDD가 이기고 B에서 TDD가 이긴 건 도메인 전문성의 차이이기도 하지만, B에서 Claude가 선택한 클로저 설계(`_scan` 중첩함수)가 Halstead 지표를 의도치 않게 높인 영향도 있다. 샘플이 각 1회인 만큼 패턴으로 일반화하기 어렵다.

> 상세 분석 → [`report_quality_a.md`](report_quality_a.md) / [`report_quality_b.md`](report_quality_b.md)

---

## 핵심 발견

1. **TDD 절감 효과는 테스트 복잡도에 반비례** — 테스트가 단순할수록 절감 효과가 크다
2. **절감은 output이 아닌 input에서 발생** — 구현→검증 루프를 Local LLM에 넘기면 Claude context 누적이 줄어든다
3. **pytest가 TDD 비용 구조의 전제** — pytest 작성 자체가 Claude 토큰을 소비하므로, pytest를 생략하면 SDD가 오히려 더 경제적일 수 있다

---

## SDD vs TDD — 어떤 상황에서 무엇을 쓸까

### Ant Mill 상황: TDD + Local LLM이 압도적으로 유리

*Ant Mill*: 코드가 꼬여 무의미한 수정을 반복하는 상황 (Claude 세션이 길어질수록 context 낭비가 심화됨).

이 경우 TDD 방식은 **Claude 토큰 소비 없이** Local LLM이 pytest를 통과할 때까지 로컬에서 무한 반복 가능. 비용 낭비 측면에서 SDD 대비 월등히 유리하다.

### 반복 개발 사이클: SDD가 범용성에서 우위

```
초기 아이디어 작성 → 중간 결과물 확인 → 추가 아이디어 적용 → 결과물 확인 → ...
```

이런 탐색적 개발 사이클에서는 TDD가 불리하다:

- **Local LLM의 불안정성** — 같은 입력에도 결과가 들쭉날쭉, 재현성 낮음
- **짧은 context 처리량** — 코드가 일정 규모를 넘으면 Local LLM이 전체 맥락을 파악하지 못함
- **느린 속도** — 탐색 단계에서 빠른 피드백이 필요할 때 병목이 됨
- **pytest 과부담** — 아직 확정되지 않은 인터페이스에 대해 테스트를 미리 작성해야 하는 부담

이 상황에서는 **SDD가 범용성 면에서 TDD보다 우수**하다.

### Local LLM TDD를 잘 쓰려면

- **모듈형 설계 필수** — 각 함수/모듈이 Local LLM의 context size 안에서 완결되도록 설계
- **코드 품질 기대치** — Local LLM(Qwen3.5 수준)의 코드 품질은 프론티어 모델 대비 생각보다 크게 뒤처지지 않음. 도메인 특화 코드에서는 오히려 앞서는 경우도 있음
- **pytest 범위 조율** — 인터페이스가 확정된 부분만 테스트 작성, 탐색 중인 부분은 생략

### 요약

| 상황 | 추천 |
|------|------|
| 반복 디버깅 루프 (Ant Mill), 비용 최우선 | **TDD + Local LLM** |
| 탐색적 개발, 빠른 피드백 필요 | **SDD** |
| pytest 없이 빠르게 구현 | **SDD** (pytest 제외 시 TDD 대비 경제적) |
| 모듈 단위가 명확히 확정된 구현 과제 | **TDD + Local LLM** |
| 범용 도메인 일반 과제 | **SDD** (코드 품질 평균적으로 우위) |

---

## 프로젝트 구조

```
stub_coding/
├── CONTEXT.md              # 도메인 용어 정의
├── results.md              # 실험 수치 기록
├── report_final.md         # 종합 레포트
├── report_quality_a.md     # Scenario A 품질 평가 (Ruff + Radon)
├── report_quality_b.md     # Scenario B 품질 평가 (Ruff + Radon)
├── report_scenario_a.md    # Scenario A 토큰 분석
├── data/
│   ├── iris_missing.csv    # 결측치 포함 Iris 데이터셋
│   └── tp53.fasta          # TP53 mRNA 서열 (NCBI NM_000546)
├── specs/
│   ├── spec_a_csv_stats.md
│   └── spec_b_dna_analyzer.md
├── prompts/                # 각 실험 세션 시작 프롬프트
│   ├── prompt_sdd_a.md
│   ├── prompt_tdd_a.md
│   ├── prompt_sdd_b.md
│   └── prompt_tdd_b.md
├── scenario_a/
│   ├── sdd/                # SDD 결과물 (Claude 작성)
│   └── tdd/                # TDD 결과물 (스텁+테스트: Claude / 구현: pi/Qwen3.5)
└── scenario_b/
    ├── sdd/
    └── tdd/
```

---

## 재현 방법

### 사전 준비
```bash
python3 -m pip install ruff radon pytest
```

### 실험 실행
1. 새 Claude Code 세션 시작 (`claude --cwd <이 디렉토리>`)
2. `prompts/` 의 해당 프롬프트 내용 붙여넣기
3. (TDD만) Claude 세션 종료 후 외부 터미널에서 `pi` 실행:
   ```bash
   pi "scenario_a/tdd/csv_stats.py 의 스텁을 구현하라. pytest가 전부 통과해야 한다."
   ```
4. `/cost` 로 토큰 확인 후 `results.md`에 기록

### 품질 평가
```bash
python3 -m ruff check scenario_a/sdd/csv_stats.py
python3 -m radon cc scenario_a/sdd/csv_stats.py -s -a
python3 -m radon mi scenario_a/sdd/csv_stats.py -s
python3 -m radon hal scenario_a/sdd/csv_stats.py
```

---

## 환경

- Claude: Sonnet 4.6 (SDD 전담, TDD에서 스텁+테스트 담당)
- pi agent: Qwen3.5 (`pi` CLI v0.79.3) — TDD에서 구현 담당 (로컬 실행, 토큰 비용 없음)
- Python: 3.11
- pytest / ruff / radon
