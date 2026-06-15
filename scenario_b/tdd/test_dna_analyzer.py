import os
import pytest
import tempfile

from dna_analyzer import parse_fasta, gc_content, reverse_complement, find_orfs


# ── parse_fasta ────────────────────────────────────────────────────────────────

FASTA_SINGLE = """>seq1
ATGCATGC
TTAAGGCC
"""

FASTA_MULTI = """>seq1
ATGC
>seq2
TTAA
GGCC
"""


@pytest.fixture
def fasta_single(tmp_path):
    f = tmp_path / "single.fasta"
    f.write_text(FASTA_SINGLE)
    return str(f)


@pytest.fixture
def fasta_multi(tmp_path):
    f = tmp_path / "multi.fasta"
    f.write_text(FASTA_MULTI)
    return str(f)


def test_parse_fasta_returns_dict(fasta_single):
    result = parse_fasta(fasta_single)
    assert isinstance(result, dict)


def test_parse_fasta_single_entry(fasta_single):
    result = parse_fasta(fasta_single)
    assert "seq1" in result
    assert result["seq1"] == "ATGCATGCTTAAGGCC"


def test_parse_fasta_multi_entry(fasta_multi):
    result = parse_fasta(fasta_multi)
    assert set(result.keys()) == {"seq1", "seq2"}
    assert result["seq1"] == "ATGC"
    assert result["seq2"] == "TTAAGGCC"


def test_parse_fasta_no_newlines_in_sequence(fasta_single):
    result = parse_fasta(fasta_single)
    assert "\n" not in result["seq1"]


def test_parse_fasta_nonexistent_file():
    with pytest.raises(Exception):
        parse_fasta("/nonexistent/path/file.fasta")


# ── gc_content ─────────────────────────────────────────────────────────────────

def test_gc_content_all_gc():
    assert gc_content("GCGC") == 1.0


def test_gc_content_all_at():
    assert gc_content("ATAT") == 0.0


def test_gc_content_mixed():
    assert gc_content("ATGC") == pytest.approx(0.5)


def test_gc_content_typical():
    # ATGCATGC: G=2, C=2, total=8 → 0.5
    assert gc_content("ATGCATGC") == pytest.approx(0.5)


def test_gc_content_returns_float():
    result = gc_content("ATGC")
    assert isinstance(result, float)


def test_gc_content_range():
    result = gc_content("ATGCGGCC")
    assert 0.0 <= result <= 1.0


def test_gc_content_lowercase():
    # 대소문자 유지 명세는 reverse_complement 쪽이지만 gc_content도 처리해야 함
    assert gc_content("atgc") == pytest.approx(0.5)


# ── reverse_complement ─────────────────────────────────────────────────────────

def test_reverse_complement_basic():
    assert reverse_complement("ATGC") == "GCAT"


def test_reverse_complement_palindrome():
    assert reverse_complement("ATAT") == "ATAT"


def test_reverse_complement_all_a():
    assert reverse_complement("AAAA") == "TTTT"


def test_reverse_complement_all_t():
    assert reverse_complement("TTTT") == "AAAA"


def test_reverse_complement_case_preserved_upper():
    result = reverse_complement("ATGC")
    assert result == result.upper()


def test_reverse_complement_case_preserved_lower():
    result = reverse_complement("atgc")
    assert result == "gcat"


def test_reverse_complement_mixed_case():
    result = reverse_complement("AtGc")
    assert result == "gCaT"


def test_reverse_complement_longer():
    # ATGCATGC → complement TACGTACG → reverse GCATGCAT
    assert reverse_complement("ATGCATGC") == "GCATGCAT"


def test_reverse_complement_returns_str():
    assert isinstance(reverse_complement("ATGC"), str)


def test_reverse_complement_involution():
    seq = "ATGCGGCCTT"
    assert reverse_complement(reverse_complement(seq)) == seq


# ── find_orfs ──────────────────────────────────────────────────────────────────

# ATG + 코돈 32개(96nt) + TAA = 전체 102nt, ORF(ATG~Stop 직전) = 99nt
_ORF_BODY = "ATG" + ("GCA" * 32) + "TAA"  # 3 + 96 + 3 = 102 nt
SEQ_SINGLE_ORF = "NNNN" + _ORF_BODY + "NNNN"


def test_find_orfs_returns_list():
    assert isinstance(find_orfs(SEQ_SINGLE_ORF), list)


def test_find_orfs_tuple_structure():
    result = find_orfs(SEQ_SINGLE_ORF)
    assert len(result) > 0
    start, end, strand = result[0]
    assert isinstance(start, int)
    assert isinstance(end, int)
    assert strand in ("+", "-")


def test_find_orfs_detects_plus_strand():
    result = find_orfs(SEQ_SINGLE_ORF, min_length=99)
    strands = [r[2] for r in result]
    assert "+" in strands


def test_find_orfs_start_is_atg():
    result = find_orfs(SEQ_SINGLE_ORF, min_length=99)
    for start, end, strand in result:
        if strand == "+":
            assert SEQ_SINGLE_ORF[start:start+3] == "ATG"


def test_find_orfs_min_length_filters():
    # min_length보다 짧은 ORF는 제외되어야 함
    short_orf = "ATGAAATAA"  # 9nt
    result = find_orfs(short_orf, min_length=100)
    assert result == []


def test_find_orfs_min_length_includes():
    result = find_orfs(SEQ_SINGLE_ORF, min_length=99)
    assert len(result) > 0


def test_find_orfs_empty_seq():
    assert find_orfs("") == []


def test_find_orfs_no_atg():
    assert find_orfs("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT") == []


def test_find_orfs_detects_minus_strand():
    # minus strand: reverse complement에 ATG~Stop 있어야 함
    # plus strand 서열: reverse_complement(_ORF_BODY) → minus strand에 ORF
    from dna_analyzer import reverse_complement as rc
    minus_seq = "NNNN" + rc(_ORF_BODY) + "NNNN"
    result = find_orfs(minus_seq, min_length=99)
    strands = [r[2] for r in result]
    assert "-" in strands


def test_find_orfs_coordinates_within_bounds():
    result = find_orfs(SEQ_SINGLE_ORF, min_length=99)
    for start, end, strand in result:
        assert 0 <= start < len(SEQ_SINGLE_ORF)
        assert 0 < end <= len(SEQ_SINGLE_ORF)
        assert start < end
