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

### Installation from PyPI

Install the latest stable version directly from PyPI:

```bash
pip install datagpu
```

For production use, we recommend installing in a virtual environment:

```bash
# Create and activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install DataGPU
pip install datagpu
```

### Verify Installation

Check that DataGPU is installed correctly:

```bash
datagpu --version
# Output: DataGPU version 0.1.0
```

### Install from Source (Development)

For development or to get the latest features:

```bash
git clone https://github.com/Jasiri-App/datagpu.git
cd datagpu

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

## Basic Usage

### Compile a Dataset

Process and optimize your dataset with a single command:

```bash
datagpu compile data/your_dataset.csv \
  --rank \
  --dedupe \
  --cache \
  --out compiled/
```

Example with sample data:

```bash
# First, download or generate sample data
python examples/generate_sample_data.py

# Process the sample data
datagpu compile examples/data/small_test.csv --out /tmp/compiled --verbose
```

Example output:
```
DataGPU v0.1.0
Compiling: examples/data/small_test.csv

Loading data from examples/data/small_test.csv...
Cleaning data...
Deduplicating...
Ranking by relevance...
Saving to /tmp/compiled/data.parquet...

Compilation complete!

 Rows processed      100                          
 Valid rows          100 (100.0%)                 
 Duplicates removed  20 (20.0%)                   
 Ranked samples      80                           
 Processing time     0.1s                         
 Output              /tmp/compiled/data.parquet  
 Manifest            /tmp/compiled/manifest.yaml 

Dataset version: v0.1.0
```

### View Dataset Information

Inspect compiled datasets:

```bash
datagpu info /tmp/compiled/manifest.yaml
```

### Cache Management

List cached datasets:
```bash
datagpu cache-list
```

Clear cache:
```bash
datagpu cache-clear
```

### Python API

You can also use DataGPU programmatically:

```python
from datagpu import DataCompiler, load
from datagpu.types import CompilationConfig, RankMethod

# Configure the compilation
config = CompilationConfig(
    source_path="data/your_dataset.csv",
    output_path="compiled/",
    dedupe=True,                    # Enable deduplication
    rank=True,                      # Enable quality ranking
    rank_method=RankMethod.RELEVANCE,
    rank_target="high quality examples",  # Target for relevance ranking
    cache=True,                     # Enable caching
    verbose=True                    # Show progress
)

# Create and run the compiler
compiler = DataCompiler(config)
output_path, manifest, stats = compiler.compile()

# Load the compiled dataset
dataset = load("compiled/manifest.yaml")

# Use with PyTorch DataLoader
from torch.utils.data import DataLoader
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Or convert to pandas/arrow
df = dataset.to_pandas()
table = dataset.to_arrow()

# Access compilation statistics
print(f"Processed {stats.total_rows} rows")
print(f"Removed {stats.duplicates_removed} duplicates")
print(f"Processing time: {stats.processing_time:.2f}s")
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
git clone https://github.com/Jasiri-App/datagpu.git
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

DataGPU is released under the [Apache 2.0 License](LICENSE).

## Citation

If you use DataGPU in your research, please cite:

```bibtex
@software{datagpu2025,
  title = {DataGPU: Open-source data compiler for AI training datasets},
  author = {Celestino Kariuki},
  organization = {Safariblocks Ltd.},
  year = {2025},
  url = {https://github.com/Jasiri-App/datagpu}
}
```

## Support

- Documentation: [GitHub README](https://github.com/Jasiri-App/datagpu)
- Issues: [GitHub Issues](https://github.com/Jasiri-App/datagpu/issues)
- Discussions: [GitHub Discussions](https://github.com/Jasiri-App/datagpu/discussions)

---

**Made with focus on data quality and reproducibility**
