SHELL:=bash

PY=python3

VENVDIR=venv
WITH_VENV=source $(VENVDIR)/bin/activate &&

TWINE=$(WITH_VENV) twine

IS_COMMIT_TAGGED=[[ $(shell git describe --tags) == $(shell git describe --tags --abbrev=0) ]]

# documentation site container
DOCKER_ACCOUNT=jdevries3133
CONTAINER_NAME=teacher_helper_docs
TAG?=$(shell git describe --tags)
CONTAINER=$(DOCKER_ACCOUNT)/$(CONTAINER_NAME):$(TAG)

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

.PHONY: check-worktree
check-worktree:
	@git diff --quiet --exit-code; \
	if [[ $$? -ne 0 ]]; then \
		echo "Fatal: working tree is not clean"; \
		exit 1; \
	fi

.PHONY: deploy-docs
deploy-docs:
	docker buildx build --platform linux/amd64 --push -t $(CONTAINER) .
	terraform init -input=false
	terraform apply -auto-approve


.PHONY: dist-production
dist-production: clean check-worktree build test
	$(TWINE) upload dist/*

.PHONY: dist-test
dist-test: clean build test
	$(TWINE) upload --repository testpypi dist/*

.PHONY: fmt
fmt: venv
	$(WITH_VENV) black .

.PHONY: fmt-check
fmt-check: venv
	$(WITH_VENV) black --check .
