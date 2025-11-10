# DataGPU Quickstart Guide

Get started with DataGPU in 5 minutes.

## Installation

```bash
# Install from source
cd /home/kcelestinomaria/startuprojects/datagpu
pip install -e .

# Or install development mode with all dependencies
pip install -e ".[dev]"
```

## Verify Installation

```bash
datagpu version
```

Expected output:
```
DataGPU version 0.1.0
```

## Generate Sample Data

```bash
python examples/generate_sample_data.py
```

This creates:
- `examples/data/small_test.csv` (100 rows)
- `examples/data/instruction_dataset.csv` (5k rows)
- `examples/data/mixed_dataset.csv` (8k rows)
- `examples/data/text_dataset.csv` (10k rows)

## Run Your First Compilation

```bash
datagpu compile examples/data/small_test.csv \
  --rank \
  --dedupe \
  --cache \
  --out compiled/
```

Expected output:
```
DataGPU v0.1.0
Compiling: examples/data/small_test.csv

Loading data from examples/data/small_test.csv...
Cleaning data...
Deduplicating...
Ranking by relevance...
Saving to compiled/data.parquet...

Compilation complete!

Rows processed       100
Valid rows           100 (100.0%)
Duplicates removed   20 (20.0%)
Ranked samples       80
Processing time      0.3s
Output               compiled/data.parquet
Manifest             compiled/manifest.yaml

Dataset version: v0.1.0
```

## Inspect Compiled Dataset

```bash
datagpu info compiled/manifest.yaml
```

## Use in Python

```python
from datagpu import load

# Load compiled dataset
dataset = load("compiled/manifest.yaml")

print(f"Dataset has {len(dataset)} rows")

# Iterate over samples
for i, item in enumerate(dataset):
    if i >= 3:
        break
    print(f"Sample {i+1}:")
    print(f"  Text: {item['text'][:50]}...")
    print(f"  Quality: {item['quality_score']:.3f}")

# Convert to pandas
df = dataset.to_pandas()
print(df.head())
```

## Run Benchmarks

```bash
# Generate all sample datasets
python examples/generate_sample_data.py

# Run benchmarks
python examples/benchmark.py
```

## Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=datagpu --cov-report=term-missing

# Run specific test
pytest tests/test_compiler.py -v
```

## Common Commands

```bash
# Compile with custom options
datagpu compile data.csv \
  --rank-method tfidf \
  --rank-target "high quality examples" \
  --compression zstd \
  --out output/

# List cached datasets
datagpu cache-list

# Clear cache
datagpu cache-clear --force

# Get help
datagpu --help
datagpu compile --help
```

## Next Steps

1. Read the [README.md](README.md) for detailed documentation
2. Check [examples/](examples/) for more usage examples
3. Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
4. Explore the [tests/](tests/) directory for code examples

## Troubleshooting

### Import Error

If you get import errors, ensure you installed the package:
```bash
pip install -e .
```

### Missing Dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

### CLI Not Found

Ensure the package is installed and your PATH includes pip's bin directory:
```bash
pip install -e .
which datagpu
```

### Permission Errors

On Linux/Mac, you may need to use:
```bash
pip install --user -e .
```

## Performance Tips

1. Use `--compression zstd` for best compression (default)
2. Enable `--cache` to speed up repeated compilations
3. Use `--rank-target` for more relevant ranking
4. For large datasets (>1M rows), consider disabling verbose output with `--quiet`

## Support

- Issues: https://github.com/datagpu/datagpu/issues
- Documentation: README.md
- Examples: examples/ directory
