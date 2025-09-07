# Makefile for livekit-voice-agent

# Python executable
PYTHON = python3.13
# UV package manager
UV = uv
# Project name
PROJECT_NAME = livekit-voice-agent

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  setup         - Create virtual environment and install dependencies"
	@echo "  setup-dev     - Install development dependencies"
	@echo "  download      - Download required model files"
	@echo "  run-console   - Run the voice agent in console mode"
	@echo "  run-dev       - Run the voice agent in development mode"
	@echo "  run-prod      - Run the voice agent in production mode"
	@echo "  test          - Run tests"
	@echo "  clean         - Remove temporary files and directories"
	@echo "  env-setup     - Set up .env.local from .env.sample (requires manual editing)"

# Create virtual environment and install dependencies
.PHONY: setup
setup:
	@echo "Creating virtual environment and installing dependencies..."
	$(UV) venv
	$(UV) pip install -e .

# Install development dependencies
.PHONY: setup-dev
setup-dev: setup
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[dev]"

# Download required model files
.PHONY: download
download:
	@echo "Downloading required model files..."
	$(UV) run agent.py download-files

# Run the voice agent in console mode
.PHONY: run-console
run-console:
	@echo "Running voice agent in console mode..."
	$(UV) run agent.py console

# Run the voice agent in development mode
.PHONY: run-dev
run-dev:
	@echo "Running voice agent in development mode..."
	$(UV) run agent.py dev

# Run the voice agent in production mode
.PHONY: run-prod
run-prod:
	@echo "Running voice agent in production mode..."
	$(UV) run agent.py start

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	$(UV) run pytest -v

# Run tests with coverage report
.PHONY: test-coverage
test-coverage:
	@echo "Running tests with coverage report..."
	$(UV) run pytest -v --cov=. --cov-report=term

# Clean up temporary files and directories
.PHONY: clean
clean:
	@echo "Cleaning up temporary files and directories..."
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf $(PROJECT_NAME).egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Set up environment file
.PHONY: env-setup
env-setup:
	@if [ ! -f .env.local ]; then \
		echo "Creating .env.local from .env.sample..."; \
		cp .env.sample .env.local; \
		echo "Please edit .env.local to add your API keys and other required data."; \
	else \
		echo ".env.local already exists. No changes made."; \
	fi