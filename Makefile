PY=python3

VENVDIR=venv
WITH_VENV=source $(VENVDIR)/bin/activate &&

TWINE=$(WITH_VENV) && twine

.PHONY: all
all: venv

.PHONY: venv
venv:
	@if [[ -d "$(VENVDIR)" ]]; then \
		echo "venv already exists"; \
		exit 0; \
	fi; \
	$(PY) -m venv $(VENVDIR); \
	$(WITH_VENV) \
		pip install --upgrade pip && \
		pip install -r requirements.txt

.PHONY: test
test: venv
	$(WITH_VENV) pytest

.PHONY: build
build: venv
	$(WITH_VENV) python3 -m build

.PHONY: clean
clean:
	find . | grep egg-info$ | xargs rm -rfd
	rm -fr dist
	rm -rf venv

.PHONY: check-worktree
check-worktree:
	git diff --quiet --exit-code; \
	if [[ $$? -ne 0 ]]; then \
		echo "Fatal: working tree is not clean"; \
		exit 1; \
	fi

.PHONY: dist-production
dist-production: clean check-worktree build test
	$(TWINE) upload dist/*

.PHONY: dist-test
dist-test: clean build test
	$(TWINE) upload --repository testpypi dist/*

.PHONY: fmt
fmt:
	$(WITH_VENV) black .
