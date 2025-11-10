"""Tests for deduplication module."""

import polars as pl
import pytest

from datagpu.deduper import DataDeduper


def test_deduplicate_exact():
    """Test exact duplicate removal."""
    df = pl.DataFrame({
        "col1": [1, 2, 1, 3],
        "col2": ["a", "b", "a", "c"]
    })
    
    deduper = DataDeduper()
    deduped_df, stats = deduper.deduplicate(df)
    
    assert len(deduped_df) == 3
    assert stats["duplicates_removed"] == 1
    assert stats["dedup_ratio"] == 0.25


def test_deduplicate_subset():
    """Test deduplication on subset of columns."""
    df = pl.DataFrame({
        "id": [1, 2, 3, 4],
        "name": ["alice", "bob", "alice", "charlie"],
        "value": [10, 20, 30, 40]
    })
    
    deduper = DataDeduper()
    deduped_df, stats = deduper.deduplicate(df, subset=["name"])
    
    assert len(deduped_df) == 3
    assert stats["duplicates_removed"] == 1


def test_deduplicate_no_duplicates():
    """Test deduplication with no duplicates."""
    df = pl.DataFrame({
        "col1": [1, 2, 3],
        "col2": ["a", "b", "c"]
    })
    
    deduper = DataDeduper()
    deduped_df, stats = deduper.deduplicate(df)
    
    assert len(deduped_df) == 3
    assert stats["duplicates_removed"] == 0
    assert stats["dedup_ratio"] == 0.0


def test_deduplicate_all_duplicates():
    """Test deduplication with all duplicates."""
    df = pl.DataFrame({
        "col1": [1, 1, 1],
        "col2": ["a", "a", "a"]
    })
    
    deduper = DataDeduper()
    deduped_df, stats = deduper.deduplicate(df)
    
    assert len(deduped_df) == 1
    assert stats["duplicates_removed"] == 2
    assert stats["dedup_ratio"] == pytest.approx(0.667, rel=0.01)
