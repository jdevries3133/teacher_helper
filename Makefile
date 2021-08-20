PY=python3
VENVDIR=venv
WITH_VENV=source $(VENVDIR)/bin/activate

TWINE=$(WITH_VENV) && twine
TESTER=$(WITH_VENV) && pytest
BUILDER=$(WITH_VENV) && python3 -m build

.PHONY: venv

all: venv

venv:
	@if [[ -d "$(VENVDIR)" ]]; then \
		echo "venv already exists"; \
		exit 0; \
	fi; \
	$(PY) -m venv $(VENVDIR) && \
	$(WITH_VENV) && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

test: venv
	$(TESTER)

build: venv
	$(BUILDER)

clean:
	find . | grep egg-info$ | xargs rm -rfd
	rm -fr dist

check-worktree:
	git diff --quiet --exit-code; \
	if [[ $$? -ne 0 ]]; then \
		echo "Fatal: working tree is not clean"; \
		exit 1; \
	fi

dist-production: clean check-worktree build test
	$(TWINE) upload dist/*

dist-test: clean build test
	$(TWINE) upload --repository testpypi dist/*

