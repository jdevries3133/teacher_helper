PY=python3
TESTER=pytest
BUILDER=python3 -m build


all: venv test

venv:
	$(PY) -m venv venv && \
	source venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

test:
	$(TESTER)

build:
	$(BUILDER)

clean:
	find . | grep egg-info$ | xargs rm -rfd
	rm -fr dist

dist-production: clean build test
	twine upload dist/*

dist-test:
	if [![ $(git diff --quiet) ]]; then \
		echo "Fatal: working tree is not clean"; \
		exit 1; \
	fi \

	# twine upload --repository testpypi dist/*

