"""Main compiler orchestrator."""

import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import polars as pl

from datagpu.types import (
    CompilationConfig,
    DatasetManifest,
    CompilationStats,
    RankMethod
)
from datagpu.cleaner import DataCleaner
from datagpu.deduper import DataDeduper
from datagpu.ranker import DataRanker
from datagpu.cache import CacheManager
from datagpu.utils import save_yaml, ensure_dir, compute_hash


class DataCompiler:
    """Main compiler that orchestrates the compilation pipeline."""
    
    def __init__(self, config: CompilationConfig):
        self.config = config
        self.cleaner = DataCleaner(verbose=config.verbose)
        self.deduper = DataDeduper(verbose=config.verbose)
        self.ranker = DataRanker(method=config.rank_method, verbose=config.verbose)
        self.cache_manager = CacheManager() if config.cache else None
    
    def load_data(self, source_path: Path) -> pl.DataFrame:
        """Load data from various formats."""
        suffix = source_path.suffix.lower()
        
        if suffix == ".csv":
            return pl.read_csv(source_path)
        elif suffix == ".parquet":
            return pl.read_parquet(source_path)
        elif suffix == ".json":
            return pl.read_json(source_path)
        elif suffix == ".jsonl":
            return pl.read_ndjson(source_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def save_data(self, df: pl.DataFrame, output_path: Path) -> None:
        """Save compiled dataset to Parquet."""
        ensure_dir(output_path.parent)
        df.write_parquet(
            output_path,
            compression=self.config.compression,
            use_pyarrow=True
        )
    
    def generate_manifest(
        self,
        df: pl.DataFrame,
        stats: CompilationStats,
        output_path: Path
    ) -> DatasetManifest:
        """Generate dataset manifest with metadata."""
        dataset_name = self.config.source_path.stem
        version = "v0.1.0"  # TODO: Implement proper versioning
        
        # Compute dataset hash
        import io
        buffer = io.BytesIO()
        df.write_parquet(buffer)
        data_bytes = buffer.getvalue()
        data_hash = compute_hash(data_bytes)
        
        manifest = DatasetManifest(
            dataset_name=dataset_name,
            version=version,
            rows=len(df),
            columns=len(df.columns),
            dedup_ratio=stats.dedup_ratio,
            rank_method=self.config.rank_method.value,
            created_at=datetime.now(timezone.utc).isoformat(),
            hash=data_hash,
            source_path=str(self.config.source_path.absolute()),
            compiled_path=str(output_path.absolute()),
            cache_path=str(Path(".datagpu/cache").absolute()),
            schema={k: v.value for k, v in self.cleaner.schema.items()} if hasattr(self.cleaner, 'schema') else {},
            stats={
                "total_rows": stats.total_rows,
                "valid_rows": stats.valid_rows,
                "duplicates_removed": stats.duplicates_removed,
                "ranked_samples": stats.ranked_samples,
                "processing_time": stats.processing_time,
            }
        )
        
        return manifest
    
    def compile(self) -> tuple[Path, DatasetManifest, CompilationStats]:
        """
        Execute full compilation pipeline.
        
        Returns:
            Tuple of (output_path, manifest, stats)
        """
        start_time = time.time()
        
        # Check cache if enabled
        if self.cache_manager:
            source_hash = self.cache_manager.compute_source_hash(self.config.source_path)
            cached = self.cache_manager.find_by_source_hash(source_hash)
            
            if cached and Path(cached["compiled_path"]).exists():
                if self.config.verbose:
                    print(f"Cache hit! Loading from {cached['compiled_path']}")
                # TODO: Load and return cached result
                pass
        
        # Load data
        if self.config.verbose:
            print(f"Loading data from {self.config.source_path}...")
        df = self.load_data(self.config.source_path)
        total_rows = len(df)
        
        # Clean data
        if self.config.verbose:
            print("Cleaning data...")
        df, clean_stats = self.cleaner.clean(df)
        valid_rows = len(df)
        
        # Deduplicate
        duplicates_removed = 0
        dedup_ratio = 0.0
        if self.config.dedupe:
            if self.config.verbose:
                print("Deduplicating...")
            df, dedup_stats = self.deduper.deduplicate(df)
            duplicates_removed = dedup_stats["duplicates_removed"]
            dedup_ratio = dedup_stats["dedup_ratio"]
        
        # Rank
        ranked_samples = 0
        if self.config.rank:
            if self.config.verbose:
                print(f"Ranking by {self.config.rank_method.value}...")
            df, rank_stats = self.ranker.rank(df, self.config.rank_target)
            ranked_samples = rank_stats["ranked_samples"]
        
        # Save compiled dataset
        output_path = self.config.output_path / "data.parquet"
        if self.config.verbose:
            print(f"Saving to {output_path}...")
        self.save_data(df, output_path)
        
        # Generate statistics
        processing_time = time.time() - start_time
        stats = CompilationStats(
            total_rows=total_rows,
            valid_rows=valid_rows,
            duplicates_removed=duplicates_removed,
            ranked_samples=ranked_samples,
            processing_time=processing_time,
            dedup_ratio=dedup_ratio,
            valid_ratio=valid_rows / total_rows if total_rows > 0 else 0
        )
        
        # Generate and save manifest
        manifest = self.generate_manifest(df, stats, output_path)
        manifest_path = self.config.output_path / "manifest.yaml"
        save_yaml(manifest.to_dict(), manifest_path)
        
        # Update cache
        if self.cache_manager:
            self.cache_manager.add_entry(
                dataset_name=manifest.dataset_name,
                version=manifest.version,
                source_hash=source_hash,
                compiled_path=str(output_path),
                manifest_path=str(manifest_path),
                metadata=manifest.stats
            )
        
        return output_path, manifest, stats
