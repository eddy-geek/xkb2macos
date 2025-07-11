.PHONY: install install-dev format lint test clean build

# Default target
all: format lint test

# Install the package
install:
	pip install -e .

# Install the package with development dependencies
install-dev:
	pip install -e ".[dev]"

# Format code with black and isort
format:
	isort xkb_to_macos tests
	black xkb_to_macos tests

# Run linting checks
lint:
	ruff check xkb_to_macos tests
	mypy xkb_to_macos tests

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=xkb_to_macos --cov-report=term --cov-report=html

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

# Build package
build: clean
	python -m build

# Install pre-commit hooks
setup-hooks:
	pre-commit install
