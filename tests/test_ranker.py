"""Tests for ranking module."""

import polars as pl
import pytest

from datagpu.ranker import DataRanker
from datagpu.types import RankMethod


def test_rank_tfidf():
    """Test TF-IDF ranking."""
    df = pl.DataFrame({
        "text": [
            "machine learning is great",
            "deep learning neural networks",
            "hello world",
            "artificial intelligence and machine learning"
        ]
    })
    
    ranker = DataRanker(method=RankMethod.TFIDF)
    ranked_df, stats = ranker.rank(df)
    
    assert "quality_score" in ranked_df.columns
    assert len(ranked_df) == 4
    assert stats["ranked_samples"] == 4
    assert stats["method"] == "tfidf"


def test_rank_with_target():
    """Test ranking with target query."""
    df = pl.DataFrame({
        "text": [
            "machine learning algorithms",
            "cooking recipes",
            "deep learning models",
            "gardening tips"
        ]
    })
    
    ranker = DataRanker(method=RankMethod.RELEVANCE)
    ranked_df, stats = ranker.rank(df, target_query="machine learning")
    
    assert "quality_score" in ranked_df.columns
    # First row should have highest score (most relevant)
    scores = ranked_df["quality_score"].to_list()
    assert scores[0] >= scores[1]


def test_rank_no_text_columns():
    """Test ranking with no text columns."""
    df = pl.DataFrame({
        "numeric": [1, 2, 3, 4],
        "value": [10, 20, 30, 40]
    })
    
    ranker = DataRanker(method=RankMethod.TFIDF)
    ranked_df, stats = ranker.rank(df)
    
    assert "quality_score" in ranked_df.columns
    # Should assign uniform scores
    assert all(score == 1.0 for score in ranked_df["quality_score"].to_list())


def test_rank_none_method():
    """Test ranking with NONE method."""
    df = pl.DataFrame({
        "text": ["hello", "world"]
    })
    
    ranker = DataRanker(method=RankMethod.NONE)
    ranked_df, stats = ranker.rank(df)
    
    assert "quality_score" in ranked_df.columns
    assert stats["method"] == "none"
    assert all(score == 1.0 for score in ranked_df["quality_score"].to_list())
