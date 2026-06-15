def parse_fasta(path: str) -> dict[str, str]:
    """FASTA 파일을 읽어 {header: sequence} dict 반환. sequence 는 줄바꿈 제거 후 합친 단일 문자열."""
    with open(path, "r") as f:
        lines = f.readlines()
    
    result = {}
    current_header = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            header = line[1:].split()[0]  # 첫 번째 단어만 사용
            current_header = header
            result[header] = ""
        elif current_header:
            result[current_header] += line
    
    return result


def gc_content(seq: str) -> float:
    """서열의 GC 함량 (0.0~1.0) 을 반환."""
    if not seq:
        return 0.0
    
    seq_upper = seq.upper()
    gc_count = seq_upper.count("G") + seq_upper.count("C")
    return gc_count / len(seq)


def reverse_complement(seq: str) -> str:
    """서열의 reverse complement 를 반환. A↔T, G↔C, 대소문자 유지."""
    complement = {"A": "T", "T": "A", "G": "C", "C": "G",
                  "a": "t", "t": "a", "g": "c", "c": "g",
                  "N": "N", "n": "n"}
    
    result = []
    for base in reversed(seq):
        result.append(complement.get(base, base))
    
    return "".join(result)


def find_orfs(seq: str, min_length: int = 100) -> list[tuple[int, int, str]]:
    """
    ATG~Stop codon 사이의 ORF 를 탐색.
    Returns: list of (start, end, strand) where strand is '+' or '-'.
    min_length: ORF 최소 뉴클레오타이드 길이.
    """
    orfs = []
    
    # Plus strand
    plus_orfs = _find_orfs_on_strand(seq, "+", min_length)
    orfs.extend(plus_orfs)
    
    # Minus strand
    rev_comp = reverse_complement(seq)
    minus_orfs = _find_orfs_on_strand(rev_comp, "-", min_length)
    
    # Adjust coordinates for minus strand (relative to original sequence)
    for start, end, _ in minus_orfs:
        # The coordinates are relative to rev_comp, convert back to original
        adjusted_start = len(seq) - end
        adjusted_end = len(seq) - start
        orfs.append((adjusted_start, adjusted_end, "-"))
    
    return orfs


def _find_orfs_on_strand(seq: str, strand: str, min_length: int) -> list[tuple[int, int, str]]:
    """Find ORFs on a single strand (ATG to Stop codon)."""
    stop_codons = ["TAA", "TAG", "TGA"]
    orfs = []
    i = 0
    
    while i <= len(seq) - 3:
        codon = seq[i:i+3]
        if codon == "ATG":
            # Found start codon, search for stop
            for j in range(i + 3, len(seq) - 2, 3):
                next_codon = seq[j:j+3]
                if next_codon in stop_codons:
                    # Found stop codon
                    orf_length = j + 3 - i
                    if orf_length >= min_length:
                        orfs.append((i, j + 3, strand))
                    break
        i += 1
    
    return orfs
