SHELL := /bin/bash

PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
PLOTS_DIR := artefacts/plots
DOCS_DIR := artefacts/docs

.PHONY: setup lint test simulate baselines docs clean help

.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo "  setup     - Create a virtual environment and install dependencies."
	@echo "  lint      - Run lightweight static analysis on the Python sources."
	@echo "  test      - Execute the pytest suite with concise output."
	@echo "  simulate  - Produce placeholder simulation artefacts and verify interfaces."
	@echo "  baselines - Exercise baseline and metric scaffolding entry points."
	@echo "  docs      - Refresh documentation placeholders for downstream publishing."
	@echo "  clean     - Remove generated artefacts and caches."

$(VENV_PYTHON): requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PIP) install -r requirements.txt

setup: $(VENV_PYTHON)
	@echo "Environment initialised in $(VENV)."

lint: $(VENV_PYTHON)
	$(VENV_PYTHON) -m compileall src sim tools

test: $(VENV_PYTHON)
	$(VENV_PYTHON) -m pytest --maxfail=1 --disable-warnings -q

simulate: $(VENV_PYTHON)
	$(VENV_PYTHON) tools/run_simulation_stub.py --output-dir $(PLOTS_DIR)

baselines: $(VENV_PYTHON)
	$(VENV_PYTHON) tools/probe_analysis_interfaces.py

docs: $(VENV_PYTHON)
	$(VENV_PYTHON) tools/generate_docs_summary.py --output-dir $(DOCS_DIR)

clean:
	rm -rf $(VENV) __pycache__ */__pycache__ $(PLOTS_DIR) $(DOCS_DIR)
