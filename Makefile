#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = egfr40
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python
CONDA_ENV = conda_312
VENV_DIR = egfr40_venv

#################################################################################
# ENVIRONMENT                                                                   #
#################################################################################

## Create venv on top of the active conda env (run `conda activate $(CONDA_ENV)` first)
venv:
	$(PYTHON_INTERPRETER) -m venv $(VENV_DIR)
	@echo ">>> Activate with: source $(VENV_DIR)/bin/activate"

## Install the package in editable mode with dev and NHANES extras
install:
	$(PYTHON_INTERPRETER) -m pip install --upgrade pip
	$(PYTHON_INTERPRETER) -m pip install -e ".[dev,nhanes]"

#################################################################################
# PROJECT COMMANDS                                                              #
#################################################################################

## Run the test suite
test:
	$(PYTHON_INTERPRETER) -m pytest -v

## Fetch raw NHANES 2017-March 2020 files into data/raw
data_gen:
	$(PYTHON_INTERPRETER) data_gen.py --csv

## Merge and recode NHANES into data/processed/nhanes_egfr40.parquet
preprocess:
	$(PYTHON_INTERPRETER) preprocessing.py --csv

## Build sdist and wheel into dist/
build:
	$(PYTHON_INTERPRETER) -m pip install --upgrade build
	$(PYTHON_INTERPRETER) -m build

## Upload dist/ to TestPyPI (run `make build` first)
publish_test:
	$(PYTHON_INTERPRETER) -m twine check dist/*
	$(PYTHON_INTERPRETER) -m twine upload --repository testpypi dist/*

## Upload dist/ to PyPI (run `make build` first)
publish:
	$(PYTHON_INTERPRETER) -m twine check dist/*
	$(PYTHON_INTERPRETER) -m twine upload dist/*

## Remove build artifacts and caches
clean:
	rm -rf build dist *.egg-info .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: venv install test data_gen preprocess build publish_test publish clean help

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

## Show this help
help:
	@echo "Available targets:"
	@awk '/^## /{desc=substr($$0,4); getline; split($$0,t,":"); printf "  \033[36m%-12s\033[0m %s\n", t[1], desc}' $(MAKEFILE_LIST)
