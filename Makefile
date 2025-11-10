.PHONY: install dev test lint format clean benchmark docs

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest --cov=datagpu --cov-report=term-missing --cov-report=html

test-fast:
	pytest -x --ff

lint:
	ruff check datagpu/ tests/
	mypy datagpu/

format:
	black datagpu/ tests/ examples/
	ruff check --fix datagpu/ tests/

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .coverage htmlcov/
	rm -rf .datagpu/ compiled/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

benchmark:
	python examples/generate_sample_data.py
	python examples/benchmark.py

quickstart:
	python examples/quickstart.py

docs:
	@echo "Documentation is in README.md"
	@echo "Run 'make quickstart' for a demo"

all: format lint test
