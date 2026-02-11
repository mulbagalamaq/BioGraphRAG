"""Tests for the PubMed/NCBI data fetcher."""

import pytest

from backend.pubmed import BiomedicalDataFetcher, _GENE_SYMBOL_RE


def test_gene_symbol_regex():
    text = "EGFR and KRAS are oncogenes related to TP53 pathway"
    symbols = list(dict.fromkeys(_GENE_SYMBOL_RE.findall(text)))
    assert "EGFR" in symbols
    assert "KRAS" in symbols
    assert "TP53" in symbols


def test_extract_gene_symbols(sample_config):
    fetcher = BiomedicalDataFetcher(sample_config)
    syms = fetcher._extract_gene_symbols("What drugs target EGFR in lung cancer?")
    assert "EGFR" in syms


def test_extract_gene_symbols_no_match(sample_config):
    fetcher = BiomedicalDataFetcher(sample_config)
    syms = fetcher._extract_gene_symbols("what causes headaches")
    # Short lowercase words should NOT match
    assert all(len(s) >= 2 for s in syms)
