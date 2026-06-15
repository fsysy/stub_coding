# Spec B — DNA 서열 분석기

## 목적
FASTA 파일을 읽어 GC 함량 계산, reverse complement 반환, ORF 탐색을 수행한다.

## 데이터
- 파일: `data/tp53.fasta`
- 형식: 표준 FASTA (헤더 `>`, 이후 서열 여러 줄)

## 함수 명세

```python
def parse_fasta(path: str) -> dict[str, str]:
    """FASTA 파일을 읽어 {header: sequence} dict 반환. sequence는 줄바꿈 제거 후 합친 단일 문자열."""

def gc_content(seq: str) -> float:
    """서열의 GC 함량(0.0~1.0)을 반환."""

def reverse_complement(seq: str) -> str:
    """서열의 reverse complement를 반환. A↔T, G↔C, 대소문자 유지."""

def find_orfs(seq: str, min_length: int = 100) -> list[tuple[int, int, str]]:
    """
    ATG~Stop codon 사이의 ORF를 탐색.
    Returns: list of (start, end, strand) where strand is '+' or '-'.
    min_length: ORF 최소 뉴클레오타이드 길이.
    """
```

## 구현 파일
- SDD: `scenario_b/sdd/dna_analyzer.py`, `scenario_b/sdd/test_dna_analyzer.py`
- TDD: `scenario_b/tdd/dna_analyzer.py`, `scenario_b/tdd/test_dna_analyzer.py`
