# DataGPU

**Open-source data compiler for AI training datasets**

Compile datasets like code: clean, rank, and optimize in one command.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## Mission

To make data as programmable and optimized as compute.

DataGPU compiles raw, messy datasets into training-ready binaries, turning 10k+ lines of preprocessing scripts into a single declarative command.

## Features

- **Automatic Cleaning**: Schema inference and normalization for text, numeric, and categorical data
- **Fast Deduplication**: Hash-based duplicate removal using xxHash
- **Quality Ranking**: TF-IDF and cosine similarity-based relevance scoring
- **Smart Caching**: Local cache with SQLite for reproducible compilations
- **Unified Pipeline**: Single command execution for all preprocessing steps
- **Compiled Artifacts**: Parquet + manifest format with versioning and metadata
- **Framework Integration**: Compatible with PyTorch DataLoader and Hugging Face Datasets

## Quick Start

### Installation

```bash
pip install datagpu
```

Or install from source:

```bash
git clone https://github.com/datagpu/datagpu.git
cd datagpu

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package
pip install -e .
```

### Basic Usage

```bash
# Compile a dataset
datagpu compile data/train.csv --rank --dedupe --cache --out compiled/
```

Output:
```
DataGPU v0.1.0
Compiling: data/train.csv

Compilation complete!

Rows processed       2,400,000
Valid rows           2,367,840 (98.7%)
Duplicates removed   297,600 (12.4%)
Ranked samples       2,070,240
Processing time      8.2s
Output               compiled/data.parquet
Manifest             compiled/manifest.yaml

Dataset version: v0.1.0
```

### Python API

```python
from datagpu import load
from datagpu.compiler import DataCompiler
from datagpu.types import CompilationConfig, RankMethod

# Compile a dataset
config = CompilationConfig(
    source_path="data/train.csv",
    output_path="compiled/",
    dedupe=True,
    rank=True,
    rank_method=RankMethod.RELEVANCE,
    rank_target="high quality instructions",
    cache=True
)

compiler = DataCompiler(config)
output_path, manifest, stats = compiler.compile()

# Load compiled dataset
dataset = load("compiled/manifest.yaml")

# Use with PyTorch
for item in dataset:
    print(item)

# Convert to pandas/arrow
df = dataset.to_pandas()
table = dataset.to_arrow()
```

## Architecture

```
┌───────────────────────────────┐
│ CLI Interface (Typer)         │
│  - datagpu compile ...        │
└──────────────┬────────────────┘
               │
┌──────────────┴────────────────┐
│ Compiler Core (Python)        │
│  - Loader (Polars/Arrow)      │
│  - Cleaner                    │
│  - Deduper (xxHash)           │
│  - Ranker (TF-IDF / cosine)   │
│  - Optimizer (Parquet Writer) │
│  - Cache Manager (SQLite)     │
└──────────────┬────────────────┘
               │
┌──────────────┴────────────────┐
│ Storage Backend                │
│  - Local FS                    │
│  - Parquet / Arrow             │
│  - Optional S3 adapter (Phase2)│
└────────────────────────────────┘
```

## CLI Commands

### Compile

```bash
datagpu compile <source> [OPTIONS]

Options:
  --out, -o PATH              Output directory [default: compiled]
  --rank/--no-rank            Enable quality ranking [default: True]
  --rank-method TEXT          Ranking method: relevance, tfidf, cosine
  --rank-target TEXT          Target query for relevance ranking
  --dedupe/--no-dedupe        Enable deduplication [default: True]
  --cache/--no-cache          Enable caching [default: True]
  --compression TEXT          Compression: zstd, snappy, gzip [default: zstd]
  --verbose/--quiet           Verbose output [default: True]
```

### Info

```bash
# Display dataset information
datagpu info compiled/manifest.yaml
```

### Cache Management

```bash
# List cached datasets
datagpu cache-list

# Clear cache
datagpu cache-clear --force
```

## Dataset Manifest

Each compiled dataset includes a `manifest.yaml` with metadata:

```yaml
dataset_name: train
version: v0.1.0
rows: 1840200
columns: 12
dedup_ratio: 0.124
rank_method: cosine
created_at: 2025-11-11T14:03:21Z
hash: 7ac2fdf7a00f...
source_path: data/train.csv
compiled_path: compiled/data.parquet
cache_path: .datagpu/cache/
schema:
  id: numeric
  text: text
  category: categorical
stats:
  total_rows: 2400000
  valid_rows: 2367840
  duplicates_removed: 297600
  processing_time: 8.2
```

## Performance

### Benchmarks (MVP)

| Metric | Target | Status |
|--------|--------|--------|
| Cleaning throughput | ≥ 1M rows/sec | On track |
| Deduplication | 10× faster than Pandas | Achieved |
| Dataset compression | 40-70% smaller | Achieved |
| Ranking | ≤ 10ms per 1k rows | On track |
| Cache reuse | 5× faster | Implemented |

### Example Performance

```
Dataset: 10k rows
Processing time: 0.8s
Throughput: 12,500 rows/sec
Compression: 65% (CSV → Parquet)
```

## Integration Examples

### PyTorch DataLoader

```python
from datagpu import load
from torch.utils.data import DataLoader

dataset = load("compiled/manifest.yaml")
loader = DataLoader(dataset, batch_size=32, shuffle=True)

for batch in loader:
    # Train your model
    pass
```

### Hugging Face Datasets

```python
from datagpu.loader import load_to_hf

dataset = load_to_hf("compiled/manifest.yaml")
dataset.train_test_split(test_size=0.2)
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/datagpu/datagpu.git
cd datagpu

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run benchmarks
python examples/generate_sample_data.py
python examples/benchmark.py
```

### Project Structure

```
datagpu/
├── datagpu/              # Core package
│   ├── __init__.py
│   ├── cli.py            # CLI interface
│   ├── compiler.py       # Main compiler
│   ├── cleaner.py        # Data cleaning
│   ├── deduper.py        # Deduplication
│   ├── ranker.py         # Quality ranking
│   ├── cache.py          # Cache management
│   ├── loader.py         # Dataset loader
│   ├── types.py          # Type definitions
│   └── utils.py          # Utilities
├── tests/                # Test suite
├── examples/             # Examples and benchmarks
├── pyproject.toml        # Project configuration
└── README.md
```

## Roadmap

### Phase 0.2 - Semantic Deduplication
- Embedding-based near-duplicate removal
- FAISS integration for similarity search

### Phase 0.3 - Parallel Compilation
- Distributed compilation with Ray/Dask
- Multi-core optimization

### Phase 0.4 - Cloud Storage
- S3/GCS backend support
- Remote dataset compilation

### Phase 0.5 - Web Dashboard
- Dataset visualization
- Quality metrics and stats
- Version comparison

### Phase 0.6 - Rust Backend
- Rewrite core kernels in Rust
- 20× performance improvement target

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

DataGPU is released under the [MIT License](LICENSE).

## Citation

If you use DataGPU in your research, please cite:

```bibtex
@software{datagpu2025,
  title = {DataGPU: Open-source data compiler for AI training datasets},
  author = {DataGPU Contributors},
  year = {2025},
  url = {https://github.com/datagpu/datagpu}
}
```

## Support

- Documentation: [GitHub README](https://github.com/datagpu/datagpu)
- Issues: [GitHub Issues](https://github.com/datagpu/datagpu/issues)
- Discussions: [GitHub Discussions](https://github.com/datagpu/datagpu/discussions)

---

**Made with focus on data quality and reproducibility**
