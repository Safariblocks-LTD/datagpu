"""Data cleaning and schema inference module."""

from typing import Dict, List, Tuple
import polars as pl
from datagpu.types import DataType


class DataCleaner:
    """Handles data cleaning and schema normalization."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.schema: Dict[str, DataType] = {}
    
    def infer_schema(self, df: pl.DataFrame) -> Dict[str, str]:
        """Infer data types for each column."""
        schema = {}
        
        for col in df.columns:
            dtype = df[col].dtype
            
            if dtype in [pl.Utf8, pl.Categorical]:
                schema[col] = DataType.TEXT.value
            elif dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, 
                          pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                          pl.Float32, pl.Float64]:
                schema[col] = DataType.NUMERIC.value
            elif dtype in [pl.Date, pl.Datetime]:
                schema[col] = DataType.DATETIME.value
            elif dtype == pl.Boolean:
                schema[col] = DataType.CATEGORICAL.value
            else:
                schema[col] = DataType.UNKNOWN.value
        
        self.schema = {k: DataType(v) for k, v in schema.items()}
        return schema
    
    def clean(self, df: pl.DataFrame) -> Tuple[pl.DataFrame, Dict[str, int]]:
        """
        Clean dataset by removing invalid rows and normalizing columns.
        
        Returns:
            Tuple of (cleaned dataframe, stats dict)
        """
        original_rows = len(df)
        stats = {"original_rows": original_rows}
        
        # Infer schema
        self.infer_schema(df)
        
        # Remove rows with all nulls
        df = df.filter(~pl.all_horizontal(pl.all().is_null()))
        stats["all_null_removed"] = original_rows - len(df)
        
        # Handle missing values per column type
        for col in df.columns:
            col_type = self.schema.get(col, DataType.UNKNOWN)
            
            if col_type == DataType.TEXT:
                # Fill text nulls with empty string
                df = df.with_columns(
                    pl.col(col).fill_null("")
                )
            elif col_type == DataType.NUMERIC:
                # Keep numeric nulls for now (could fill with median/mean)
                pass
            elif col_type == DataType.CATEGORICAL:
                # Fill categorical nulls with "unknown"
                df = df.with_columns(
                    pl.col(col).fill_null("unknown")
                )
        
        # Remove duplicate columns
        unique_cols = []
        seen = set()
        for col in df.columns:
            if col not in seen:
                unique_cols.append(col)
                seen.add(col)
        
        if len(unique_cols) < len(df.columns):
            df = df.select(unique_cols)
            stats["duplicate_cols_removed"] = len(df.columns) - len(unique_cols)
        
        # Normalize column names (lowercase, replace spaces with underscores)
        df = df.rename({col: col.lower().replace(" ", "_") for col in df.columns})
        
        stats["cleaned_rows"] = len(df)
        stats["valid_ratio"] = len(df) / original_rows if original_rows > 0 else 0
        
        return df, stats
    
    def validate(self, df: pl.DataFrame) -> bool:
        """Validate that dataframe meets basic quality requirements."""
        if len(df) == 0:
            return False
        if len(df.columns) == 0:
            return False
        return True
