PROJ_PTH=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
# Overwrite it with 'export VENV_PATH=/pth/to/venv'
VENV_PATH?=${PROJ_PTH}.venv
PYTHON_EXEC=${VENV_PATH}/bin/python3
.ONESHELL:

LINT_PATHS = \
src \
tests \


venv:
	. "$(VENV_PATH)/bin/activate"

lint: venv
	$(PYTHON_EXEC) -m autoflake --in-place --recursive --exclude __init__.py,unit_tests.py --remove-unused-variables --remove-all-unused-imports $(LINT_PATHS)
	$(PYTHON_EXEC) -m black $(LINT_PATHS)
	$(PYTHON_EXEC) -m isort -rc $(LINT_PATHS)


compile-deps: venv
	$(PYTHON_EXEC) -m piptools compile --output-file "${PROJ_PTH}requirements.txt"


recompile-deps: venv
	$(PYTHON_EXEC) -m piptools compile --upgrade --output-file "${PROJ_PTH}requirements.txt"


sync-deps: venv
	$(PYTHON_EXEC) -m piptools sync "${PROJ_PTH}requirements.txt"


test: venv
	@echo asd ${PROJ_PTH}
	@echo daa ${VENV_PATH}
