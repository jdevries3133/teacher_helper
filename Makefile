PY=python3
TESTER=pytest
BUILDER=python3 -m build
VENVDIR=venv

.PHONY: venv

all: venv

venv:
	@if [[ -d "$(VENVDIR)" ]]; then \
		echo "venv already exists"; \
		exit 0; \
	fi; \
	$(PY) -m venv $(VENVDIR) && \
	source $(VENVDIR)/bin/activate && \
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
	if [[ $? -ne 0 ]]; then \
		echo "Fatal: working tree is not clean"; \
		exit 1; \
	fi

dist-production: clean check-worktree build test
	twine upload dist/*

dist-test: clean check-worktree build test
	twine upload --repository testpypi dist/*

