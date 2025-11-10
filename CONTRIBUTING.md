# Contributing to DataGPU

Thank you for your interest in contributing to DataGPU! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, professional, and constructive in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/datagpu.git
   cd datagpu
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Setting Up Your Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=datagpu --cov-report=html

# Run specific test file
pytest tests/test_compiler.py

# Run specific test
pytest tests/test_compiler.py::test_compile_full_pipeline
```

### Code Style

We use `black` for formatting and `ruff` for linting:

```bash
# Format code
black datagpu/ tests/

# Lint code
ruff check datagpu/ tests/

# Type checking
mypy datagpu/
```

### Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and add tests

3. Run tests and linting:
   ```bash
   pytest
   black datagpu/ tests/
   ruff check datagpu/ tests/
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request on GitHub

## Pull Request Guidelines

- Write clear, descriptive commit messages
- Include tests for new features
- Update documentation as needed
- Ensure all tests pass
- Keep PRs focused on a single feature or fix
- Reference related issues in PR description

## Types of Contributions

### Bug Reports

When filing a bug report, include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, DataGPU version)
- Minimal code example if applicable

### Feature Requests

When proposing a feature:
- Explain the use case
- Describe the proposed solution
- Consider alternative approaches
- Discuss potential impact on existing functionality

### Code Contributions

Areas where contributions are especially welcome:
- Performance optimizations
- Additional ranking methods
- New data format support
- Documentation improvements
- Test coverage expansion
- Bug fixes

## Project Structure

```
datagpu/
├── datagpu/              # Core package
│   ├── cli.py            # CLI interface
│   ├── compiler.py       # Main compiler orchestrator
│   ├── cleaner.py        # Data cleaning logic
│   ├── deduper.py        # Deduplication logic
│   ├── ranker.py         # Quality ranking logic
│   ├── cache.py          # Cache management
│   ├── loader.py         # Dataset loading
│   ├── types.py          # Type definitions
│   └── utils.py          # Utility functions
├── tests/                # Test suite
├── examples/             # Example scripts
└── docs/                 # Documentation
```

## Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Test edge cases and error conditions
- Use fixtures for common test data

Example test structure:

```python
def test_feature_name():
    """Test description."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Documentation

When adding features:
- Update README.md if user-facing
- Add docstrings to all functions/classes
- Include usage examples
- Update type hints

Docstring format:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Example:
        >>> function_name("test", 42)
        True
    """
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `datagpu/__init__.py`
2. Update CHANGELOG.md
3. Create release tag:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```
4. Build and publish to PyPI:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Questions?

If you have questions about contributing:
- Open a GitHub Discussion
- Check existing issues and PRs
- Review the documentation

Thank you for contributing to DataGPU!
