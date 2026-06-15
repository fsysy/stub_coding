def parse_fasta(path: str) -> dict[str, str]:
    """FASTA 파일을 읽어 {header: sequence} dict 반환. sequence는 줄바꿈 제거 후 합친 단일 문자열."""
    result = {}
    header = None
    seq_parts = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if header is not None:
                    result[header] = "".join(seq_parts)
                header = line[1:]
                seq_parts = []
            else:
                seq_parts.append(line)
    if header is not None:
        result[header] = "".join(seq_parts)
    return result


def gc_content(seq: str) -> float:
    """서열의 GC 함량(0.0~1.0)을 반환."""
    if not seq:
        return 0.0
    gc = sum(1 for c in seq if c in "GCgc")
    return gc / len(seq)


def reverse_complement(seq: str) -> str:
    """서열의 reverse complement를 반환. A↔T, G↔C, 대소문자 유지."""
    comp = {"A": "T", "T": "A", "G": "C", "C": "G",
            "a": "t", "t": "a", "g": "c", "c": "g"}
    return "".join(comp.get(b, b) for b in reversed(seq))


def find_orfs(seq: str, min_length: int = 100) -> list[tuple[int, int, str]]:
    """
    ATG~Stop codon 사이의 ORF를 탐색.
    Returns: list of (start, end, strand) where strand is '+' or '-'.
    min_length: ORF 최소 뉴클레오타이드 길이.
    """
    stop_codons = {"TAA", "TAG", "TGA"}
    orfs = []

    def _scan(s, strand):
        n = len(s)
        for frame in range(3):
            i = frame
            while i + 3 <= n:
                codon = s[i:i+3].upper()
                if codon == "ATG":
                    for j in range(i + 3, n - 2, 3):
                        stop = s[j:j+3].upper()
                        if stop in stop_codons:
                            length = j + 3 - i
                            if length >= min_length:
                                if strand == "+":
                                    orfs.append((i, j + 3, strand))
                                else:
                                    end = n - i
                                    start = n - (j + 3)
                                    orfs.append((start, end, strand))
                            break
                i += 3

    seq_upper = seq.upper()
    _scan(seq_upper, "+")
    rc = reverse_complement(seq_upper)
    _scan(rc, "-")

    return orfs
