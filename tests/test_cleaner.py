"""Tests for data cleaning module."""

import polars as pl
import pytest

from datagpu.cleaner import DataCleaner
from datagpu.types import DataType


def test_schema_inference():
    """Test schema inference for different data types."""
    df = pl.DataFrame({
        "text_col": ["hello", "world"],
        "numeric_col": [1, 2],
        "float_col": [1.5, 2.5],
        "bool_col": [True, False]
    })
    
    cleaner = DataCleaner()
    schema = cleaner.infer_schema(df)
    
    assert schema["text_col"] == DataType.TEXT.value
    assert schema["numeric_col"] == DataType.NUMERIC.value
    assert schema["float_col"] == DataType.NUMERIC.value
    assert schema["bool_col"] == DataType.CATEGORICAL.value


def test_clean_removes_all_null_rows():
    """Test that rows with all nulls are removed."""
    df = pl.DataFrame({
        "col1": [1, None, 3],
        "col2": ["a", None, "c"]
    })
    
    cleaner = DataCleaner()
    cleaned_df, stats = cleaner.clean(df)
    
    assert len(cleaned_df) == 2
    assert stats["all_null_removed"] == 1


def test_clean_fills_text_nulls():
    """Test that text nulls are filled with empty string."""
    df = pl.DataFrame({
        "text_col": ["hello", None, "world"],
        "other_col": [1, 2, 3]  # Prevent row removal
    })
    
    cleaner = DataCleaner()
    cleaned_df, stats = cleaner.clean(df)
    
    # Check that the null was filled with empty string
    assert cleaned_df["text_col"][1] == ""
    assert len(cleaned_df) == 3


def test_clean_normalizes_column_names():
    """Test that column names are normalized."""
    df = pl.DataFrame({
        "Column Name": [1, 2],
        "UPPER": [3, 4]
    })
    
    cleaner = DataCleaner()
    cleaned_df, stats = cleaner.clean(df)
    
    assert "column_name" in cleaned_df.columns
    assert "upper" in cleaned_df.columns


def test_validate():
    """Test dataset validation."""
    cleaner = DataCleaner()
    
    # Valid dataframe
    valid_df = pl.DataFrame({"col": [1, 2, 3]})
    assert cleaner.validate(valid_df) is True
    
    # Empty dataframe
    empty_df = pl.DataFrame()
    assert cleaner.validate(empty_df) is False
    
    # Zero rows
    zero_rows = pl.DataFrame({"col": []})
    assert cleaner.validate(zero_rows) is False
