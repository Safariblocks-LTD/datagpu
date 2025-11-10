"""Quickstart example for DataGPU."""

from pathlib import Path

from datagpu import load
from datagpu.compiler import DataCompiler
from datagpu.types import CompilationConfig, RankMethod


def main():
    """Run a simple compilation example."""
    print("DataGPU Quickstart Example\n")
    
    # Check if sample data exists
    data_path = Path("examples/data/small_test.csv")
    if not data_path.exists():
        print("Generating sample data...")
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from generate_sample_data import generate_text_dataset
        
        data_path.parent.mkdir(parents=True, exist_ok=True)
        df = generate_text_dataset(100, duplicate_ratio=0.2)
        df.write_csv(data_path)
        print(f"Created: {data_path}\n")
    
    # Configure compilation
    output_path = Path("examples/compiled/quickstart")
    
    config = CompilationConfig(
        source_path=data_path,
        output_path=output_path,
        dedupe=True,
        rank=True,
        rank_method=RankMethod.RELEVANCE,
        rank_target="machine learning",
        cache=True,
        verbose=True
    )
    
    # Compile dataset
    print("Compiling dataset...")
    compiler = DataCompiler(config)
    result_path, manifest, stats = compiler.compile()
    
    print(f"\nCompilation complete!")
    print(f"Output: {result_path}")
    print(f"\nStats:")
    print(f"  Total rows: {stats.total_rows}")
    print(f"  Valid rows: {stats.valid_rows} ({stats.valid_ratio:.1%})")
    print(f"  Duplicates removed: {stats.duplicates_removed} ({stats.dedup_ratio:.1%})")
    print(f"  Processing time: {stats.processing_time:.2f}s")
    
    # Load compiled dataset
    print(f"\nLoading compiled dataset...")
    manifest_path = output_path / "manifest.yaml"
    dataset = load(manifest_path)
    
    print(f"Loaded {len(dataset)} rows")
    print(f"\nFirst 3 samples:")
    for i, item in enumerate(dataset):
        if i >= 3:
            break
        print(f"\n  Sample {i+1}:")
        print(f"    Text: {item['text'][:60]}...")
        print(f"    Quality: {item['quality_score']:.3f}")
    
    print("\nQuickstart complete!")


if __name__ == "__main__":
    main()
