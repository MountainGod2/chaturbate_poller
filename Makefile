# Makefile for chaturbate-poller project
# This file provides common development tasks for the chaturbate-poller Python project

.PHONY: help install install-dev install-docs sync clean lint format typecheck test test-cov security docs docs-serve build docker docker-compose run debug version release all ci

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON_VERSION := 3.13
UV_CACHE_DIR := /tmp/uv-cache
DOCKER_IMAGE := chaturbate-poller
DOCS_PORT := 8000

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

help: ## Show this help message
	@echo "$(CYAN)Chaturbate Poller Development Makefile$(RESET)"
	@echo ""
	@echo "$(GREEN)Available targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Examples:$(RESET)"
	@echo "  make install-dev    # Install development dependencies"
	@echo "  make test           # Run tests"
	@echo "  make lint           # Run linting checks"
	@echo "  make ci             # Run all CI checks locally"

# Development Environment Setup
install: ## Install production dependencies only
	@echo "$(GREEN)Installing production dependencies...$(RESET)"
	uv sync --frozen

install-dev: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(RESET)"
	uv sync --group=dev --frozen

install-docs: ## Install documentation dependencies
	@echo "$(GREEN)Installing documentation dependencies...$(RESET)"
	uv sync --group=docs --frozen

install-build: ## Install build dependencies
	@echo "$(GREEN)Installing build dependencies...$(RESET)"
	uv sync --group=build --frozen

sync: ## Sync all dependencies (including optional groups)
	@echo "$(GREEN)Syncing all dependencies...$(RESET)"
	uv sync --group=dev --group=docs --group=build --frozen

update: ## Update dependencies (regenerate lock file)
	@echo "$(YELLOW)Updating dependencies...$(RESET)"
	uv lock --upgrade
	uv sync --group=dev --group=docs --group=build

# Code Quality
lint: ## Run linting checks (ruff)
	@echo "$(GREEN)Running ruff format check...$(RESET)"
	uv run ruff format --check --diff
	@echo "$(GREEN)Running ruff lint check...$(RESET)"
	uv run ruff check

lint-fix: ## Fix linting issues automatically
	@echo "$(GREEN)Running ruff format...$(RESET)"
	uv run ruff format
	@echo "$(GREEN)Running ruff lint with fixes...$(RESET)"
	uv run ruff check --fix

format: ## Format code with ruff
	@echo "$(GREEN)Formatting code...$(RESET)"
	uv run ruff format

typecheck: ## Run type checking
	@echo "$(GREEN)Running MyPy type check...$(RESET)"
	uv run mypy ./
	@echo "$(GREEN)Running BasedPyright type check...$(RESET)"
	uv run basedpyright ./

pylint: ## Run pylint
	@echo "$(GREEN)Running pylint...$(RESET)"
	uv run pylint src/

# Testing
test: ## Run tests
	@echo "$(GREEN)Running tests...$(RESET)"
	uv run pytest

test-cov: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(RESET)"
	uv run pytest --cov-report=html --cov-report=term-missing --cov-report=xml

test-fast: ## Run tests in parallel with minimal output
	@echo "$(GREEN)Running tests in parallel...$(RESET)"
	uv run pytest -n auto --tb=short

test-verbose: ## Run tests with verbose output
	@echo "$(GREEN)Running tests with verbose output...$(RESET)"
	uv run pytest -v

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(GREEN)Running tests in watch mode...$(RESET)"
	uv run pytest-watch

# Security
security: ## Run security checks
	@echo "$(GREEN)Running Bandit security scan...$(RESET)"
	uv run bandit -r src/ -f json || true
	@echo "$(GREEN)Running pip-audit...$(RESET)"
	uv run pip-audit || true

security-sarif: ## Run security checks with SARIF output
	@echo "$(GREEN)Running Bandit security scan with SARIF output...$(RESET)"
	uv run bandit -r src/ -f sarif -o bandit.sarif || true

# Documentation
docs: ## Build documentation
	@echo "$(GREEN)Building documentation...$(RESET)"
	rm -rf docs/_build
	uv run --group docs sphinx-build docs docs/_build/html -W

docs-serve: ## Serve documentation locally
	@echo "$(GREEN)Serving documentation at http://localhost:$(DOCS_PORT)$(RESET)"
	cd docs/_build/html && python -m http.server $(DOCS_PORT)

docs-clean: ## Clean documentation build
	@echo "$(GREEN)Cleaning documentation build...$(RESET)"
	rm -rf docs/_build
	rm -rf docs/api

docs-auto: ## Build docs with auto-reload (requires sphinx-autobuild)
	@echo "$(GREEN)Building docs with auto-reload...$(RESET)"
	uv run --group docs sphinx-autobuild docs docs/_build/html --host 0.0.0.0 --port $(DOCS_PORT)

# Building and Packaging
build: ## Build package
	@echo "$(GREEN)Building package...$(RESET)"
	uv build

build-wheel: ## Build wheel only
	@echo "$(GREEN)Building wheel...$(RESET)"
	uv build --wheel

build-sdist: ## Build source distribution only
	@echo "$(GREEN)Building source distribution...$(RESET)"
	uv build --sdist

# Docker
docker: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(RESET)"
	docker build -t $(DOCKER_IMAGE):latest .

docker-dev: ## Build Docker image with dev dependencies
	@echo "$(GREEN)Building Docker development image...$(RESET)"
	docker build -t $(DOCKER_IMAGE):dev --target builder .

docker-run: ## Run Docker container
	@echo "$(GREEN)Running Docker container...$(RESET)"
	docker run --rm -it $(DOCKER_IMAGE):latest

docker-compose-up: ## Start services with docker-compose
	@echo "$(GREEN)Starting services with docker-compose...$(RESET)"
	docker-compose up -d

docker-compose-down: ## Stop services with docker-compose
	@echo "$(GREEN)Stopping services with docker-compose...$(RESET)"
	docker-compose down

docker-compose-logs: ## View docker-compose logs
	@echo "$(GREEN)Viewing docker-compose logs...$(RESET)"
	docker-compose logs -f

# Application
run: ## Run the application
	@echo "$(GREEN)Running chaturbate-poller...$(RESET)"
	uv run chaturbate_poller

run-module: ## Run the application as module
	@echo "$(GREEN)Running chaturbate-poller as module...$(RESET)"
	uv run python -m chaturbate_poller

debug: ## Run the application in debug mode
	@echo "$(GREEN)Running chaturbate-poller in debug mode...$(RESET)"
	uv run chaturbate_poller --verbose

# Version and Release
version: ## Show current version
	@echo "$(GREEN)Current version:$(RESET)"
	@uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

version-bump-patch: ## Bump patch version
	@echo "$(GREEN)Bumping patch version...$(RESET)"
	uv run semantic-release version --patch

version-bump-minor: ## Bump minor version
	@echo "$(GREEN)Bumping minor version...$(RESET)"
	uv run semantic-release version --minor

version-bump-major: ## Bump major version
	@echo "$(GREEN)Bumping major version...$(RESET)"
	uv run semantic-release version --major

release: ## Create a release
	@echo "$(GREEN)Creating release...$(RESET)"
	uv run semantic-release publish

# Cleaning
clean: ## Clean build artifacts
	@echo "$(GREEN)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf docs/_build/
	rm -rf docs/api/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete

clean-cache: ## Clean UV cache
	@echo "$(GREEN)Cleaning UV cache...$(RESET)"
	uv cache clean

clean-all: clean clean-cache ## Clean everything

# Pre-commit and Git hooks
pre-commit-install: ## Install pre-commit hooks
	@echo "$(GREEN)Installing pre-commit hooks...$(RESET)"
	uv run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	@echo "$(GREEN)Running pre-commit on all files...$(RESET)"
	uv run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "$(GREEN)Updating pre-commit hooks...$(RESET)"
	uv run pre-commit autoupdate

# CI/CD
ci: install-dev lint typecheck security test-cov ## Run all CI checks locally
	@echo "$(GREEN)All CI checks completed successfully!$(RESET)"

ci-docs: install-docs docs ## Run documentation CI checks

ci-fast: install-dev lint typecheck test-fast ## Run fast CI checks (parallel tests)

# Development workflow
dev-setup: install-dev pre-commit-install ## Set up development environment
	@echo "$(GREEN)Development environment setup complete!$(RESET)"
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Copy .env.example to .env and configure your settings"
	@echo "  2. Run 'make test' to verify everything is working"
	@echo "  3. Run 'make run' to start the application"

dev-check: lint typecheck test ## Run development checks

# Examples and demos
examples: ## Run example scripts
	@echo "$(GREEN)Available examples:$(RESET)"
	@ls examples/

run-example: ## Run a specific example (use EXAMPLE=filename)
	@echo "$(GREEN)Running example: $(EXAMPLE)$(RESET)"
	uv run python examples/$(EXAMPLE)

# Monitoring and profiling
profile: ## Run with profiling
	@echo "$(GREEN)Running with profiling...$(RESET)"
	uv run python -m cProfile -o profile.stats -m chaturbate_poller

profile-view: ## View profiling results
	@echo "$(GREEN)Viewing profiling results...$(RESET)"
	uv run python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Database operations (InfluxDB)
db-setup: ## Set up InfluxDB with docker-compose
	@echo "$(GREEN)Setting up InfluxDB...$(RESET)"
	docker-compose up -d influxdb

db-status: ## Check database status
	@echo "$(GREEN)Checking InfluxDB status...$(RESET)"
	curl -f http://localhost:8086/health || echo "InfluxDB not accessible"

# Utility targets
check-deps: ## Check for dependency updates
	@echo "$(GREEN)Checking for dependency updates...$(RESET)"
	uv lock --dry-run --upgrade

list-deps: ## List installed dependencies
	@echo "$(GREEN)Installed dependencies:$(RESET)"
	uv pip list

env-info: ## Show environment information
	@echo "$(GREEN)Environment Information:$(RESET)"
	@echo "Python version: $(shell uv run python --version)"
	@echo "UV version: $(shell uv --version)"
	@echo "Project root: $(shell pwd)"
	@echo "UV cache dir: $(UV_CACHE_DIR)"

# All-in-one targets
all: clean install-dev lint typecheck test-cov security docs build ## Run complete workflow

# Quick development iteration
quick: lint-fix typecheck test-fast ## Quick development check and fix cycle
