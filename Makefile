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
	rm -r dist

dist-production: clean build test
	twine upload dist/*

dist-test: clean build test
	twine upload --repository testpypi dist/*

