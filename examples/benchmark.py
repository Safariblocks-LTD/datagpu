"""Benchmark DataGPU compilation performance."""

import time
from pathlib import Path

import polars as pl

from datagpu.compiler import DataCompiler
from datagpu.types import CompilationConfig, RankMethod


def benchmark_compilation(dataset_path: Path, name: str):
    """Benchmark compilation of a single dataset."""
    print(f"\n{'='*60}")
    print(f"Benchmarking: {name}")
    print(f"{'='*60}")
    
    # Load original dataset
    df = pl.read_csv(dataset_path)
    original_size = dataset_path.stat().st_size
    print(f"Original rows: {len(df):,}")
    print(f"Original size: {original_size / 1024 / 1024:.2f} MB")
    
    # Benchmark compilation
    output_path = Path(f"examples/compiled/{name}")
    output_path.mkdir(parents=True, exist_ok=True)
    
    config = CompilationConfig(
        source_path=dataset_path,
        output_path=output_path,
        dedupe=True,
        rank=True,
        rank_method=RankMethod.TFIDF,
        cache=False,
        verbose=False
    )
    
    compiler = DataCompiler(config)
    
    start_time = time.time()
    result_path, manifest, stats = compiler.compile()
    elapsed = time.time() - start_time
    
    # Get compiled size
    compiled_size = result_path.stat().st_size
    compression_ratio = (1 - compiled_size / original_size) * 100
    
    # Calculate throughput
    throughput = stats.total_rows / elapsed
    
    print(f"\nResults:")
    print(f"  Compiled rows: {manifest.rows:,}")
    print(f"  Duplicates removed: {stats.duplicates_removed:,} ({stats.dedup_ratio:.1%})")
    print(f"  Valid ratio: {stats.valid_ratio:.1%}")
    print(f"  Processing time: {elapsed:.2f}s")
    print(f"  Throughput: {throughput:,.0f} rows/sec")
    print(f"  Compiled size: {compiled_size / 1024 / 1024:.2f} MB")
    print(f"  Compression: {compression_ratio:.1f}%")
    
    return {
        "name": name,
        "original_rows": len(df),
        "compiled_rows": manifest.rows,
        "duplicates_removed": stats.duplicates_removed,
        "processing_time": elapsed,
        "throughput": throughput,
        "original_size_mb": original_size / 1024 / 1024,
        "compiled_size_mb": compiled_size / 1024 / 1024,
        "compression_ratio": compression_ratio
    }


def main():
    """Run benchmarks on all sample datasets."""
    print("DataGPU Benchmark Suite")
    print("="*60)
    
    data_dir = Path("examples/data")
    
    if not data_dir.exists():
        print(f"\nError: Data directory not found: {data_dir}")
        print("Run 'python examples/generate_sample_data.py' first")
        return
    
    datasets = [
        ("small_test.csv", "Small Test (100 rows)"),
        ("instruction_dataset.csv", "Instruction Dataset (5k rows)"),
        ("mixed_dataset.csv", "Mixed Dataset (8k rows)"),
        ("text_dataset.csv", "Text Dataset (10k rows)"),
    ]
    
    results = []
    
    for filename, name in datasets:
        dataset_path = data_dir / filename
        if dataset_path.exists():
            result = benchmark_compilation(dataset_path, filename.replace(".csv", ""))
            results.append(result)
        else:
            print(f"\nSkipping {name}: file not found")
    
    # Summary
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*60}")
    
    if results:
        avg_throughput = sum(r["throughput"] for r in results) / len(results)
        avg_compression = sum(r["compression_ratio"] for r in results) / len(results)
        total_rows = sum(r["original_rows"] for r in results)
        total_time = sum(r["processing_time"] for r in results)
        
        print(f"\nTotal rows processed: {total_rows:,}")
        print(f"Total processing time: {total_time:.2f}s")
        print(f"Average throughput: {avg_throughput:,.0f} rows/sec")
        print(f"Average compression: {avg_compression:.1f}%")
        
        # Performance targets check
        print(f"\nPerformance Targets:")
        target_throughput = 1_000_000  # 1M rows/sec on 8-core
        print(f"  Target throughput: {target_throughput:,} rows/sec")
        print(f"  Actual throughput: {avg_throughput:,.0f} rows/sec")
        
        if avg_throughput >= target_throughput * 0.3:  # 30% of target for single-threaded
            print(f"  Status: On track (single-threaded baseline)")
        else:
            print(f"  Status: Below target (optimization needed)")


if __name__ == "__main__":
    main()
