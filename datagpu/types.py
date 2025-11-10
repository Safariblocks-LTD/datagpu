"""Type definitions and data models for DataGPU."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any


class RankMethod(str, Enum):
    """Ranking methods for dataset quality scoring."""
    RELEVANCE = "relevance"
    TFIDF = "tfidf"
    COSINE = "cosine"
    NONE = "none"


class DataType(str, Enum):
    """Detected data types for columns."""
    TEXT = "text"
    NUMERIC = "numeric"
    IMAGE = "image"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    UNKNOWN = "unknown"


@dataclass
class CompilationConfig:
    """Configuration for dataset compilation."""
    source_path: Path
    output_path: Path
    dedupe: bool = True
    rank: bool = True
    rank_method: RankMethod = RankMethod.RELEVANCE
    cache: bool = True
    rank_target: Optional[str] = None
    compression: str = "zstd"
    parallel: bool = True
    verbose: bool = True


@dataclass
class DatasetManifest:
    """Manifest metadata for compiled datasets."""
    dataset_name: str
    version: str
    rows: int
    columns: int
    dedup_ratio: float
    rank_method: str
    created_at: str
    hash: str
    source_path: str
    compiled_path: str
    cache_path: str
    schema: Dict[str, str] = field(default_factory=dict)
    stats: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary."""
        return {
            "dataset_name": self.dataset_name,
            "version": self.version,
            "rows": self.rows,
            "columns": self.columns,
            "dedup_ratio": self.dedup_ratio,
            "rank_method": self.rank_method,
            "created_at": self.created_at,
            "hash": self.hash,
            "source_path": self.source_path,
            "compiled_path": self.compiled_path,
            "cache_path": self.cache_path,
            "schema": self.schema,
            "stats": self.stats,
        }


@dataclass
class CompilationStats:
    """Statistics from compilation process."""
    total_rows: int
    valid_rows: int
    duplicates_removed: int
    ranked_samples: int
    processing_time: float
    dedup_ratio: float
    valid_ratio: float
    
    def __str__(self) -> str:
        """Format stats for display."""
        return (
            f"{self.total_rows:,} rows processed\n"
            f"Cleaned {self.valid_ratio:.1%} valid rows\n"
            f"Removed {self.dedup_ratio:.1%} duplicates\n"
            f"Ranked {self.ranked_samples:,} samples by quality score\n"
            f"Total time: {self.processing_time:.1f}s"
        )
