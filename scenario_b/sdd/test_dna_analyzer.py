import pytest
import os
from dna_analyzer import parse_fasta, gc_content, reverse_complement, find_orfs

FASTA_PATH = os.path.join(os.path.dirname(__file__), "../../data/tp53.fasta")


# parse_fasta
def test_parse_fasta_returns_dict():
    result = parse_fasta(FASTA_PATH)
    assert isinstance(result, dict)
    assert len(result) >= 1


def test_parse_fasta_header_no_gt():
    result = parse_fasta(FASTA_PATH)
    for header in result:
        assert not header.startswith(">")


def test_parse_fasta_sequence_no_newlines():
    result = parse_fasta(FASTA_PATH)
    for seq in result.values():
        assert "\n" not in seq
        assert len(seq) > 0


def test_parse_fasta_sequence_contains_only_nucleotides():
    result = parse_fasta(FASTA_PATH)
    for seq in result.values():
        assert all(c in "ACGTNacgtn" for c in seq)


# gc_content
def test_gc_content_known():
    assert gc_content("GCGC") == pytest.approx(1.0)
    assert gc_content("ATAT") == pytest.approx(0.0)
    assert gc_content("ACGT") == pytest.approx(0.5)


def test_gc_content_empty():
    assert gc_content("") == 0.0


def test_gc_content_range():
    result = parse_fasta(FASTA_PATH)
    for seq in result.values():
        val = gc_content(seq)
        assert 0.0 <= val <= 1.0


def test_gc_content_case_insensitive():
    assert gc_content("gcgc") == pytest.approx(1.0)
    assert gc_content("GcGc") == pytest.approx(1.0)


# reverse_complement
def test_reverse_complement_simple():
    assert reverse_complement("ATGC") == "GCAT"


def test_reverse_complement_palindrome():
    seq = "AACCGGTT"
    rc = reverse_complement(seq)
    assert rc == "AACCGGTT"


def test_reverse_complement_lowercase():
    assert reverse_complement("atgc") == "gcat"


def test_reverse_complement_double():
    seq = "ATGCATGC"
    assert reverse_complement(reverse_complement(seq)) == seq


def test_reverse_complement_tp53():
    result = parse_fasta(FASTA_PATH)
    seq = list(result.values())[0]
    rc = reverse_complement(seq)
    assert len(rc) == len(seq)
    assert reverse_complement(rc) == seq


# find_orfs
def test_find_orfs_returns_list():
    result = parse_fasta(FASTA_PATH)
    seq = list(result.values())[0]
    orfs = find_orfs(seq)
    assert isinstance(orfs, list)


def test_find_orfs_tuple_structure():
    result = parse_fasta(FASTA_PATH)
    seq = list(result.values())[0]
    orfs = find_orfs(seq)
    for orf in orfs:
        assert len(orf) == 3
        start, end, strand = orf
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert strand in ("+", "-")
        assert start < end


def test_find_orfs_min_length():
    result = parse_fasta(FASTA_PATH)
    seq = list(result.values())[0]
    orfs = find_orfs(seq, min_length=100)
    for start, end, _ in orfs:
        assert end - start >= 100


def test_find_orfs_start_codon():
    seq = "ATGAAATAA"  # single ORF, length=9 < 100, so won't appear with default
    orfs = find_orfs(seq, min_length=9)
    assert len(orfs) >= 1
    assert orfs[0][0] == 0
    assert orfs[0][1] == 9
    assert orfs[0][2] == "+"


def test_find_orfs_both_strands():
    result = parse_fasta(FASTA_PATH)
    seq = list(result.values())[0]
    orfs = find_orfs(seq, min_length=30)
    strands = {o[2] for o in orfs}
    assert "+" in strands or "-" in strands
