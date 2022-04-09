# Copyright (c) John DeVries
# All rights reserved.

# This code is licensed under the MIT License.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

SHELL:=bash

VENVDIR=venv
WITH_VENV=source $(VENVDIR)/bin/activate &&

TWINE=$(WITH_VENV) twine

# documentation site container
DOCKER_ACCOUNT=jdevries3133
CONTAINER_NAME=teacher_helper_docs
TAG?=$(shell git describe --tags)
CONTAINER=$(DOCKER_ACCOUNT)/$(CONTAINER_NAME):$(TAG)

.PHONY: test
test: venv
	$(WITH_VENV) pytest

.PHONY: venv
venv:
	@if [[ -d "$(VENVDIR)" ]]; then \
		echo "venv already exists"; \
		exit 0; \
	fi; \
	python3 -m venv $(VENVDIR); \
	$(WITH_VENV) \
		pip install --upgrade pip && \
		pip install -r requirements.txt


.PHONY: build
build: venv
	$(WITH_VENV) python3 -m build

.PHONY: clean
clean:
	find . | grep egg-info$ | xargs rm -rfd
	rm -fr dist

.PHONY: fmt
fmt: venv
	$(WITH_VENV) black .

.PHONY: fmt-check
fmt-check: venv
	$(WITH_VENV) black --check .

.PHONY: check-worktree
check-worktree:
	@git diff --quiet --exit-code; \
	if [[ $$? -ne 0 ]]; then \
		echo "Fatal: working tree is not clean"; \
		exit 1; \
	fi

.PHONY: serve-docs
serve-docs:
	@# roughly check if documentation dependencies were installed
	if [ "$(shell pip freeze | grep mkdocs)" == "" ]; then \
		$(WITH_VENV) pip install -r requirements.docs.txt; \
	fi
	$(WITH_VENV) mkdocs serve

.PHONY: deploy-docs
deploy-docs: check-worktree
	docker buildx build --platform linux/amd64 --push -t $(CONTAINER) .
	terraform init -input=false
	terraform apply -auto-approve

.PHONY: dist-production
dist-production: clean check-worktree build test
	$(TWINE) upload dist/*

.PHONY: dist-test
dist-test: clean build test
	$(TWINE) upload --repository testpypi dist/*

