# pystatis justfile

# Show available recipes
default:
    @just --list

# Install dependencies
install:
    uv sync

# Install dependencies including dev
install-dev:
    uv sync --all-groups

# Run all tests
test:
    uv run pytest tests/

# Run tests with coverage report
test-cov:
    uv run pytest tests/ --cov=src/pystatis --cov-report=term-missing

# Format code
fmt:
    uv run ruff format src/ tests/

# Lint code
lint:
    uv run ruff check src/ tests/

# Lint and auto-fix
lint-fix:
    uv run ruff check --fix src/ tests/

# Type check
typecheck:
    uv run ty check src/
