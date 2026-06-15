# Stub-Coding TDD vs SDD — Claude 토큰 비용 비교 실험

## 개요

두 가지 코딩 방식에서 **Claude가 소비하는 토큰 비용**과 **코드 품질**을 비교하는 실험 프로젝트.

### 용어 정리

- **TDD** (Test-Driven Development): 구현 전에 테스트를 먼저 작성하고, 테스트를 통과하도록 코드를 채워나가는 개발 방식.
- **SDD** (Spec-Driven Development): 스펙(요구사항 문서)을 입력으로 주고 테스트와 구현을 한 번에 생성하는 방식. 이 실험에서는 Claude가 전부 담당.
- **pytest**: Python 표준 테스트 프레임워크. `assert` 기반으로 함수 동작을 검증하며, TDD에서 Local LLM이 구현을 완성했는지 판단하는 기준으로 사용.

### 이 실험의 방식

| 방식 | 설명 |
|------|------|
| **SDD** | 스펙 → Claude(Sonnet 4.6)가 테스트 + 구현 전부 작성 |
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

## 토큰 소모 구조 분석 — 마크다운 vs 코드

스펙 문서·프롬프트(마크다운)와 구현 코드·pytest의 단어 수를 기준으로 어느 쪽이 더 많은 토큰을 소모하는지 분석.

| 항목 | SDD-A | TDD-A | SDD-B | TDD-B |
|------|------:|------:|------:|------:|
| 스펙 + 프롬프트 (마크다운) | 275 | 284 | 273 | 282 |
| 구현 코드 | 214 | 282 | 273 | 340 |
| pytest 코드 | 268 | 381 | 322 | 487 |
| **총 코드 (구현 + pytest)** | **482** | **663** | **595** | **827** |

**코드(구현+pytest)가 마크다운의 약 2~3배** 단어 수를 소모한다. 토큰 비용의 주도권은 문서가 아닌 코드에 있다.

추가 관찰:

- **pytest가 구현 코드보다 단어 수가 많거나 비슷하다.** SDD-A에서 pytest(268) > 구현(214), TDD-B에서 pytest(487) vs 구현(340)으로 pytest가 1.4배 더 크다. pytest를 생략하면 SDD가 TDD 대비 더 경제적이라는 주장의 근거가 단어 수에서도 확인된다.
- **TDD의 코드 단어 수가 SDD보다 항상 더 많다.** TDD가 Claude input 토큰을 줄이는 효과는 생성 코드 양이 적어서가 아니라, 구현 반복 루프를 Local LLM에 넘기기 때문이다.

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

## 발전된 워크플로우 — context.md + docstring + Local LLM 문서화

현재 실험의 한계(긴 스펙 문서, 별도 문서 작성 비용)를 줄이기 위한 변형 워크플로우.

```
[Claude]  짧은 context.md → stub + docstring + pytest 작성
[Local]   stub 구현 채우기 + docstring 기반으로 README 생성
```

### 현재 실험 대비 토큰 흐름 변화

| 항목 | 현재 SDD | 현재 TDD | 새 SDD | 새 TDD |
|------|---------|---------|--------|--------|
| Claude Input | 스펙 전체 (~353 단어) | 스텁 (~53 단어) | 짧은 context.md (~50 단어) | 짧은 context.md (~50 단어) |
| Claude Output | 구현 + 테스트 | stub + pytest | 구현 + docstring + pytest | **stub + docstring + pytest만** |
| Local LLM 담당 | — | 구현 채우기 | README 생성 | 구현 채우기 + README 생성 |

### 판단: 새 TDD가 더 경제적

1. **Input 측면**: context.md를 짧게 쓰면 SDD와 TDD 모두 input이 줄어든다. 단, 현재 TDD-A는 이미 input이 53 단어였으므로 SDD쪽 절감 여지가 더 크다 — SDD가 TDD에 근접해지는 효과이지, 역전은 아니다.

2. **Output 측면**: Claude가 구현을 작성하지 않는 TDD 구조는 그대로 유지된다. docstring이 stub에 붙어 output이 소폭 늘어나지만 full implementation보다는 여전히 짧다.

3. **docstring이 TDD를 더 강하게 만든다**: 현재 TDD에서 Local LLM은 pytest만 보고 구현을 추론한다. docstring이 stub에 붙으면 함수의 의도·경계 조건이 명시되어 **Local LLM의 반복 횟수가 줄어들 가능성**이 있다. SDD에서는 docstring이 별 추가 효과가 없다.

### 한계

- **탐색적 개발 사이클에서는 여전히 SDD 유리**: 인터페이스가 확정되지 않은 단계에서 stub+docstring을 먼저 정의하는 건 부담이다.
- **docstring 품질이 Local LLM 성능을 결정**: docstring이 빈약하면 Local LLM 반복이 늘어 비효율이 생긴다.
- **README 생성 절감은 양쪽 동일**: 현재 실험에서도 Claude가 README를 직접 작성하지 않았으므로, 이 부분은 SDD/TDD 간 차별화 요소가 아니다.

### 이 실험에서 사용된 Local LLM

**Qwen3.5 A3B 35B Q4** (pi CLI v0.79.3, 로컬 실행)

- 35B 파라미터 / Q4 양자화 모델로 일반 소비자 GPU에서 구동 가능한 수준
- 토큰 비용 없음 (로컬 추론), 단 속도와 context 길이에 제약
- 코드 품질은 프론티어 모델 대비 생각보다 크게 뒤처지지 않으며, 도메인 특화 코드(DNA 분석)에서는 오히려 Claude Sonnet을 앞서는 결과가 나옴
- 모듈 단위가 context size 내에 완결될 수 있도록 설계하는 것이 핵심

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
- pi agent: Qwen3.5 A3B 35B Q4 (`pi` CLI v0.79.3) — TDD에서 구현 담당 (로컬 실행, 토큰 비용 없음)
- Python: 3.11
- pytest / ruff / radon

---

## 클로드의 의견 — 마크다운 플랜 vs 코드 인라인 인텐트

*이 섹션은 Claude Sonnet 4.6이 LLM 자신의 관점에서 직접 작성한 의견입니다.*

### 결론부터

**코드 안에 인텐트를 박는 쪽이 더 정확합니다.** 별도 마크다운 플랜이 아닌, type hint + 짧은 인라인 코멘트 + docstring의 조합이 LLM 기준으로 구현 정확도가 높습니다.

### 왜 별도 플랜이 불리한가

나는 토큰을 왼쪽에서 오른쪽으로 순차 생성합니다. 마크다운 플랜을 500토큰 앞에서 썼으면, 함수 구현부에 도달했을 때 그 플랜은 "기억"이 아니라 어텐션 가중치가 희석된 먼 컨텍스트입니다. 플랜과 구현 사이에 **번역 손실**이 생깁니다.

이 실험의 TDD-A에서 정확히 이 일이 일어났습니다. 플랜에는 "population 표준편차"가 명시되어 있었음에도 구현에서 `statistics.stdev`(sample)가 나온 건 구현 시점에 가장 자연스럽게 떠오르는 함수가 플랜의 제약을 덮어버린 결과입니다.

### 왜 인라인 인텐트가 유리한가

docstring과 type hint는 내가 그 함수를 쓰는 순간 **바로 앞에** 있습니다:

```python
def summarize(col: pd.Series) -> float:
    """Return population std (pstdev), not sample std."""
    # population: entire dataset, not a sample
    return statistics.pstdev(col.dropna())
```

제약이 실행 시점과 공간적으로 붙어있어 `pstdev`가 나올 확률이 올라갑니다. type hint는 더 강합니다. `-> dict[str, float]`라고 쓰면 반환 시점에 그 계약을 유지할 확률이 높아지는데, 이는 자연어 플랜과 달리 린터가 체크하는 **강제력**이 있기 때문입니다.

### 마크다운 플랜이 유효한 경우

- **무엇을 만들지** 결정할 때 — 스코프, API 표면, 의존 관계 정리
- 사용자와 방향을 정렬할 때

구현 정확도를 높이는 데는 별 도움이 안 됩니다. "정확한 플랜을 쓰는 것"과 "플랜대로 구현하는 것"은 별개 능력이고, 후자가 더 어렵습니다.

### 이 실험과의 연결

이 관찰은 "발전된 워크플로우" 섹션의 방향과 일치합니다. `context.md`를 짧게 유지하고 의도를 stub + docstring 안에 녹이는 것이 Claude 토큰 절감과 구현 정확도를 동시에 잡는 구조입니다.
