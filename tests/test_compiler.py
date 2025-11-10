"""Tests for main compiler."""

import tempfile
from pathlib import Path

import polars as pl
import pytest

from datagpu.compiler import DataCompiler
from datagpu.types import CompilationConfig, RankMethod


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / "test.csv"
    df = pl.DataFrame({
        "id": [1, 2, 3, 3, 4],  # Has duplicate
        "text": ["hello world", "machine learning", "deep learning", "deep learning", "ai"],
        "value": [10, 20, 30, 30, 40]
    })
    df.write_csv(csv_path)
    return csv_path


def test_load_csv(sample_csv):
    """Test loading CSV file."""
    config = CompilationConfig(
        source_path=sample_csv,
        output_path=Path("compiled")
    )
    compiler = DataCompiler(config)
    df = compiler.load_data(sample_csv)
    
    assert len(df) == 5
    assert "id" in df.columns


def test_compile_full_pipeline(sample_csv, tmp_path):
    """Test full compilation pipeline."""
    output_path = tmp_path / "compiled"
    
    config = CompilationConfig(
        source_path=sample_csv,
        output_path=output_path,
        dedupe=True,
        rank=True,
        rank_method=RankMethod.TFIDF,
        cache=False,
        verbose=False
    )
    
    compiler = DataCompiler(config)
    result_path, manifest, stats = compiler.compile()
    
    # Check output files exist
    assert result_path.exists()
    assert (output_path / "manifest.yaml").exists()
    
    # Check stats
    assert stats.total_rows == 5
    assert stats.duplicates_removed == 1
    assert stats.valid_rows == 5
    
    # Check manifest
    assert manifest.rows == 4  # After deduplication
    assert manifest.dataset_name == "test"


def test_compile_no_dedupe(sample_csv, tmp_path):
    """Test compilation without deduplication."""
    output_path = tmp_path / "compiled"
    
    config = CompilationConfig(
        source_path=sample_csv,
        output_path=output_path,
        dedupe=False,
        rank=False,
        cache=False,
        verbose=False
    )
    
    compiler = DataCompiler(config)
    result_path, manifest, stats = compiler.compile()
    
    assert stats.duplicates_removed == 0
    assert manifest.rows == 5


def test_save_and_load(sample_csv, tmp_path):
    """Test saving and loading compiled dataset."""
    output_path = tmp_path / "compiled"
    
    config = CompilationConfig(
        source_path=sample_csv,
        output_path=output_path,
        cache=False,
        verbose=False
    )
    
    compiler = DataCompiler(config)
    result_path, manifest, stats = compiler.compile()
    
    # Load the compiled dataset
    loaded_df = pl.read_parquet(result_path)
    assert len(loaded_df) > 0
    assert "quality_score" in loaded_df.columns
