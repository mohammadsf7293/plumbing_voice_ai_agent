UV ?= uv

.PHONY: help setup setup-dev env-setup download run-console run-dev run-prod demo test test-basic test-handoffs test-edge-cases test-behavior test-provider test-coverage test-verbose
help:
	@echo "setup / setup-dev  Install locked runtime / test dependencies"
	@echo "demo               Run a booking workflow without credentials"
	@echo "test               Run offline tests; provider evaluations are skipped"
	@echo "test-provider      Run paid provider evaluations (credentials required)"
	@echo "run-console / run-dev / run-prod  Run the voice worker"

setup:
	$(UV) sync --locked

setup-dev:
	$(UV) sync --locked --extra dev

env-setup:
	@if [ ! -f .env.local ]; then cp .env.sample .env.local; fi
	@echo "Edit .env.local with your credentials before running the voice worker."

download:
	$(UV) run --locked agent.py download-files

run-console:
	$(UV) run --locked agent.py console

run-dev:
	$(UV) run --locked agent.py dev

run-prod:
	$(UV) run --locked agent.py start

demo:
	$(UV) run --locked -m plumbing.demo

test:
	$(UV) run --locked --extra dev pytest -q

test-basic:
	$(UV) run --locked --extra dev pytest -q tests/test_simple.py tests/test_assistant.py

test-handoffs:
	$(UV) run --locked --extra dev pytest -q tests/test_offline_handoffs.py tests/test_agent_handoffs.py

test-edge-cases:
	$(UV) run --locked --extra dev pytest -q tests/test_business.py tests/test_speech.py tests/test_config_telemetry.py

test-behavior: test-provider

test-provider:
	$(UV) run --locked --extra dev pytest --run-provider -m provider -v

test-coverage:
	$(UV) run --locked --extra dev pytest --cov=plumbing --cov=agent --cov-report=term-missing

test-verbose:
	$(UV) run --locked --extra dev pytest -v -s
