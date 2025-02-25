.PHONY: clean distclean docker docker-run format test test-formatting test-mypy test-pylint deploy

py_files:=$(shell find src -type f -name '*.py')

# formatting
format: .git/py-format

.git/py-format: venv/.updated $(py_files)
	venv/bin/ruff check --fix-only --unsafe-fixes --exit-zero --show-fixes $(py-files)
	venv/bin/ruff format $(py-files)
	@touch $@

# testing
test: venv/.updated
	venv/bin/ruff check $(py-files)
	venv/bin/ruff format --check $(py-files)
	@echo all tests passed

# virtual env
venv/.updated: venv/bin/python requirements.txt requirements-test.txt
	venv/bin/pip-sync requirements.txt requirements-test.txt
	@touch $@

venv/bin/python:
	python3.11 -m venv venv
	venv/bin/pip install -U pip wheel pip-tools --disable-pip-version-check

requirements.txt: venv/bin/python requirements.in
	venv/bin/pip-compile requirements.in --output-file requirements.txt --strip-extras --quiet --no-header --annotation-style line

requirements-test.txt: venv/bin/python requirements-test.in
	venv/bin/pip-compile requirements-test.in --output-file requirements-test.txt --strip-extras --quiet --no-header --annotation-style line

# cleaning
clean:
	@rm -f .git/py-format

distclean: clean
	@rm -rf venv

# docker
docker:
	docker build --tag slack-firefox-community --network host --platform linux/amd64 .

docker-run: docker
	docker run --rm --tty --interactive --mount type=bind,source=$(PWD)/state,target=/app/state slack-firefox-community

deploy: docker
	docker save slack-firefox-community | ssh lump 'docker load'
