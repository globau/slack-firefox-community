.PHONY: clean distclean docker docker-run format test test-formatting test-mypy test-pylint deploy

py_files:=$(shell find src -type f -name '*.py')

# formatting
format: .git/py-format

.git/py-format: venv/.updated $(py_files)
	venv/bin/ruff check --config .ruff.toml --cache-dir .git/ruff_cache --fix-only --exit-zero --show-fixes $(py_files)
	venv/bin/black $(py_files)
	venv/bin/isort --multi-line 3 --line-width 88 --trailing-comma --atomic $(py_files)
	@touch $@

# testing
test: venv/.updated
	venv/bin/ruff check --config .ruff.toml --cache-dir .git/ruff_cache $(py_files)
	venv/bin/black --check $(py_files)
	venv/bin/isort --multi-line 3 --line-width 88 --trailing-comma --check-only $(py_files)
	@echo all tests passed

# virtual env
venv/.updated: requirements.txt requirements-test.txt
	@[ -e venv/bin/python ] || python3 -m venv venv
	venv/bin/pip install --upgrade --disable-pip-version-check pip wheel
	venv/bin/pip install --upgrade --disable-pip-version-check --requirement requirements-test.txt --requirement requirements.txt
	@touch $@

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
