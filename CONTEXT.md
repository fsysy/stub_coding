# stub_coding — Context

## 프로젝트 목적

**Stub-Coding TDD** vs **SDD(Spec-Driven Development)** 두 방식에서
Claude가 소비하는 토큰 양을 비교하는 실험 프로젝트.

---

## 핵심 용어

### SDD (Spec-Driven Development)
스펙을 주면 Claude Code가 **pytest 테스트 + 실제 구현 코드 전부** 작성.
스텁 없음. 대조군(baseline).

### Stub-Coding TDD
1. **Claude**가 함수 스텁(시그니처 + docstring + `pass`) + pytest 테스트 스켈레톤 작성
2. Claude 세션 종료
3. **pi agent (Qwen 3.5)** 가 외부 터미널에서 스텁 → 실제 구현으로 채움
4. pi가 pytest 실행 → 실패 시 자체 수정 반복
5. pi 컨텍스트 초과 실패 시에만 Claude 예외 개입

### pi agent
`pi` CLI (v0.79.3)로 실행. Qwen 3.5 모델 사용.
**외부 터미널에서만 실행** — Claude context에 stdout 유입 없음.

### Token Budget (측정 대상)
**Claude가 소비한 input + output 토큰 합계**만 카운트.
pi agent 토큰은 측정 대상 외.

### 측정 방법
Claude Code `/cost` 명령. 세션(프로세스) 단위 로컬 집계 → 다른 동시 세션 오염 없음.
**All tests pass** 시점에 `/cost` 스냅샷.

---

## 실험 설계

| 항목 | 결정 |
|------|------|
| 시나리오 | A (CSV 통계), B (DNA 분석기) — 각각 동일 과제 적용 |
| 스펙 수준 | High — 함수 시그니처 + 타입 명시. 엣지케이스/기대값은 구현 세션에서 결정 |
| 실험 시작점 | 완성된 스펙 문서를 첫 메시지로 붙여넣기 |
| SDD 세션 | Claude: 테스트 + 구현 전부 작성 |
| TDD 세션 | Claude: 스텁 + 테스트 스켈레톤만 작성 후 종료 |
| pi 실행 | 외부 터미널 (Claude Code 외부) |
| 완료 기준 | pytest 전체 통과 |
| 반복 횟수 | 1회 (탐색적 실험) |
| 총 세션 수 | 4개 (SDD-A, SDD-B, TDD-A, TDD-B) |

---

## 실험 절차

```
[이 설계 세션에서]
1. 시나리오 A, B 스펙 문서 작성 (High 수준)
2. 샘플 데이터 준비

[각 실험 세션에서]
3. 새 Claude Code 세션 시작
4. 스펙 문서 붙여넣기
5. SDD: Claude가 tests + 구현 작성
   TDD: Claude가 stubs + test skeleton 작성 후 세션 종료
6. (TDD만) 외부 터미널에서 pi 실행 → 구현 완성
7. pytest 전체 통과 확인
8. /cost 스냅샷 기록
```
