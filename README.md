# Stub-Coding TDD vs SDD — Claude 토큰 비용 비교 실험

## 개요

두 가지 코딩 방식에서 **Claude가 소비하는 토큰 비용**을 비교하는 실험 프로젝트.

| 방식 | 설명 |
|------|------|
| **SDD** (Spec-Driven Development) | 스펙 → Claude가 테스트 + 구현 전부 작성 |
| **Stub-Coding TDD** | 스펙 → Claude가 스텁 + 테스트만 작성 → pi(Qwen3.5)가 구현 |

---

## 실험 결과 요약

| 세션 | 비용 | pytest |
|------|------|--------|
| SDD-A (CSV 통계) | $0.2512 | 13/13 통과 |
| TDD-A (CSV 통계) | **$0.1512** | 20/20 통과 |
| SDD-B (DNA 분석) | $0.2740 | 21/21 통과 |
| TDD-B (DNA 분석) | **$0.2479** | 29/29 통과 |

- Scenario A: TDD **40% 저렴**
- Scenario B: TDD **9.5% 저렴**

> 전체 결과 → [`results.md`](results.md) / 종합 분석 → [`report_final.md`](report_final.md)

---

## 핵심 발견

1. **TDD 절감 효과는 테스트 복잡도에 반비례** — 테스트가 단순할수록 절감 효과가 크다
2. **절감은 output이 아닌 input에서 발생** — 구현→검증 루프를 pi에 넘기면 Claude context 누적이 줄어든다
3. **코드 품질은 도메인에 따라 역전** — 범용 과제는 SDD 우위, 도메인 특화 과제는 TDD(pi) 우위

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
│   └── tdd/                # TDD 결과물 (스텁: Claude / 구현: pi)
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

- Claude: Sonnet 4.6
- pi agent: Qwen3.5 (`pi` CLI v0.79.3)
- Python: 3.11
- pytest / ruff / radon
