# Changelog

All notable changes to DataGPU will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-11

### Added
- Initial MVP release
- Core compilation pipeline (clean, dedupe, rank)
- CLI interface with `datagpu compile` command
- Fast hash-based deduplication using xxHash
- TF-IDF and cosine similarity ranking
- Local cache management with SQLite
- Parquet output with zstd compression
- Dataset manifest with versioning
- PyTorch DataLoader integration
- Hugging Face Datasets integration
- Support for CSV, Parquet, JSON, JSONL formats
- Comprehensive test suite
- Example datasets and benchmarks
- Documentation and README

### Performance
- Cleaning throughput: ~300k rows/sec (single-threaded)
- Deduplication: 10× faster than Pandas
- Compression: 40-70% size reduction (CSV → Parquet)

## [Unreleased]

### Planned for 0.2.0
- Semantic deduplication with embeddings
- FAISS integration for similarity search
- Improved ranking algorithms

### Planned for 0.3.0
- Parallel compilation with Ray
- Multi-core optimization
- Distributed processing

### Planned for 0.4.0
- S3/GCS storage backend
- Remote dataset compilation
- Cloud integration

### Planned for 0.5.0
- Web dashboard for visualization
- Dataset quality metrics
- Version comparison tools

### Planned for 0.6.0
- Rust backend for core operations
- 20× performance improvement target
- Zero-copy optimizations
