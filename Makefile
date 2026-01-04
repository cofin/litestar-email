SHELL := /bin/bash

# =============================================================================
# Configuration and Environment Variables
# =============================================================================

.DEFAULT_GOAL:=help
.ONESHELL:
.EXPORT_ALL_VARIABLES:
MAKEFLAGS += --no-print-directory

# -----------------------------------------------------------------------------
# Display Formatting and Colors
# -----------------------------------------------------------------------------
BLUE := $(shell printf "\033[1;34m")
GREEN := $(shell printf "\033[1;32m")
RED := $(shell printf "\033[1;31m")
YELLOW := $(shell printf "\033[1;33m")
NC := $(shell printf "\033[0m")
INFO := $(shell printf "$(BLUE)ℹ$(NC)")
OK := $(shell printf "$(GREEN)✓$(NC)")
WARN := $(shell printf "$(YELLOW)⚠$(NC)")
ERROR := $(shell printf "$(RED)✖$(NC)")

# =============================================================================
# Help and Documentation
# =============================================================================

.PHONY: help
help:                                               ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# =============================================================================
# Installation and Environment Setup
# =============================================================================

.PHONY: install-uv
install-uv:                                         ## Install latest version of uv
	@echo "${INFO} Installing uv..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
	@echo "${OK} UV installed successfully"

.PHONY: install
install: clean                                      ## Install the project, dependencies, and pre-commit for local development
	@echo "${INFO} Starting fresh installation..."
	@uv sync --all-extras --dev
	@echo "${OK} Installation complete!"

.PHONY: destroy
destroy:                                            ## Destroy the virtual environment
	@echo "${INFO} Destroying virtual environment..."
	@rm -rf .venv
	@echo "${OK} Virtual environment destroyed"

# =============================================================================
# Dependency Management
# =============================================================================

.PHONY: upgrade
upgrade:                                            ## Upgrade all dependencies to latest stable versions
	@echo "${INFO} Updating all dependencies..."
	@uv lock --upgrade
	@echo "${OK} Dependencies updated"
	@uv run pre-commit autoupdate
	@echo "${OK} Updated Pre-commit hooks"

.PHONY: lock
lock:                                              ## Rebuild lockfiles from scratch
	@echo "${INFO} Rebuilding lockfiles..."
	@uv lock --upgrade
	@echo "${OK} Lockfiles updated"

# =============================================================================
# Build and Release
# =============================================================================

.PHONY: build
build:                                             ## Build the project
	@echo "${INFO} Building package..."
	@uv build
	@echo "${OK} Package build complete"

# =============================================================================
# Documentation
# =============================================================================

.PHONY: docs
docs:                                             ## Build documentation
	@echo "${INFO} Building docs..."
	@uv run sphinx-build -b html docs docs/_build/html
	@echo "${OK} Docs build complete"

.PHONY: docs-linkcheck
docs-linkcheck:                                   ## Check documentation links
	@echo "${INFO} Checking docs links..."
	@uv run sphinx-build -b linkcheck docs docs/_build/linkcheck
	@echo "${OK} Docs linkcheck complete"

.PHONY: docs-clean
docs-clean:                                       ## Clean documentation artifacts
	@echo "${INFO} Cleaning docs artifacts..."
	@rm -rf docs/_build docs-build >/dev/null 2>&1
	@echo "${OK} Docs artifacts cleaned"

# =============================================================================
# Cleaning and Maintenance
# =============================================================================

.PHONY: clean
clean:                                              ## Cleanup temporary build artifacts
	@echo "${INFO} Cleaning working directory..."
	@rm -rf .pytest_cache .ruff_cache .hypothesis build/ dist/ .eggs/ .coverage coverage.xml coverage.json htmlcov/ .pytest_cache src/tests/.pytest_cache src/tests/**/.pytest_cache .mypy_cache >/dev/null 2>&1
	@find . -name '*.egg-info' -exec rm -rf {} + >/dev/null 2>&1
	@find . -type f -name '*.egg' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*.pyc' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*.pyo' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*~' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '__pycache__' -exec rm -rf {} + >/dev/null 2>&1
	@find . -name '.ipynb_checkpoints' -exec rm -rf {} + >/dev/null 2>&1
	@echo "${OK} Working directory cleaned"

# =============================================================================
# Testing and Quality Checks
# =============================================================================

.PHONY: test
test:                                              ## Run the tests
	@echo "${INFO} Running test cases..."
	@uv run pytest src/tests
	@echo "${OK} Tests complete"

.PHONY: test-all
test-all: test                                     ## Run all tests

.PHONY: coverage
coverage:                                          ## Run tests with coverage report
	@echo "${INFO} Running tests with coverage..."
	@uv run pytest src/tests --cov -n auto
	@uv run coverage html >/dev/null 2>&1
	@uv run coverage xml >/dev/null 2>&1
	@echo "${OK} Coverage report generated"

# -----------------------------------------------------------------------------
# Type Checking
# -----------------------------------------------------------------------------

.PHONY: mypy
mypy:                                              ## Run mypy
	@echo "${INFO} Running mypy..."
	@uv run dmypy run
	@echo "${OK} Mypy checks passed"

.PHONY: mypy-nocache
mypy-nocache:                                      ## Run Mypy without cache
	@echo "${INFO} Running mypy without cache..."
	@uv run mypy
	@echo "${OK} Mypy checks passed"

.PHONY: pyright
pyright:                                           ## Run pyright
	@echo "${INFO} Running pyright..."
	@uv run pyright
	@echo "${OK} Pyright checks passed"

.PHONY: type-check
type-check: mypy pyright                           ## Run all type checking

# -----------------------------------------------------------------------------
# Linting and Formatting
# -----------------------------------------------------------------------------

.PHONY: pre-commit
pre-commit:                                        ## Run pre-commit hooks
	@echo "${INFO} Running pre-commit checks..."
	@uv run pre-commit run --all-files
	@echo "${OK} Pre-commit checks passed"

.PHONY: slotscheck
slotscheck:                                        ## Run slotscheck
	@echo "${INFO} Running slots check..."
	@uv run slotscheck src/litestar_email/
	@echo "${OK} Slots check passed"

.PHONY: fix
fix:                                               ## Fix linting issues
	@echo "${INFO} Fixing linting issues..."
	@uv run ruff check --fix --unsafe-fixes src/
	@uv run ruff format src/
	@echo "${OK} Linting issues fixed"

.PHONY: lint
lint: pre-commit type-check slotscheck             ## Run all linting checks

.PHONY: check-all
check-all: lint test-all coverage                  ## Run all checks (lint, test, coverage)

# =============================================================================
# Email Testing Infrastructure
# =============================================================================

.PHONY: start-mail
start-mail:                                        ## Start Mailpit for email testing
	@echo "${INFO} Starting Mailpit..."
	@docker run -d --name mailpit -p 8025:8025 -p 1025:1025 axllent/mailpit >/dev/null 2>&1 || \
		(docker start mailpit >/dev/null 2>&1 && echo "${OK} Mailpit already exists, starting...") || \
		podman run -d --name mailpit -p 8025:8025 -p 1025:1025 axllent/mailpit >/dev/null 2>&1 || \
		(podman start mailpit >/dev/null 2>&1 && echo "${OK} Mailpit already exists, starting...")
	@echo "${OK} Mailpit started at http://localhost:8025 (SMTP: localhost:1025)"

.PHONY: stop-mail
stop-mail:                                         ## Stop and remove Mailpit container
	@echo "${INFO} Stopping Mailpit..."
	@docker stop mailpit >/dev/null 2>&1 && docker rm mailpit >/dev/null 2>&1 || \
		podman stop mailpit >/dev/null 2>&1 && podman rm mailpit >/dev/null 2>&1 || true
	@echo "${OK} Mailpit stopped"

.PHONY: mail-logs
mail-logs:                                         ## Show Mailpit container logs
	@docker logs -f mailpit 2>/dev/null || podman logs -f mailpit 2>/dev/null
