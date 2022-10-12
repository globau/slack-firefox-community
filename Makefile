.PHONY: clean distclean docker docker-run format test test-formatting test-mypy test-pylint

py-files:=$(shell find src -type f -name '*.py')

# formatting
format: .git/py-format

.git/py-format: venv/.updated $(py-files)
	@venv/bin/black \
		$(py-files)
	@venv/bin/isort \
		--multi-line 3 \
		--line-width 88 \
		--trailing-comma \
		--atomic \
		--virtual-env venv \
		$(py-files)
	@touch $@

# virtual env
venv/.updated: requirements.txt dev-requirements.txt
	@[ -e venv/bin/python ] || python3 -m venv venv
	@venv/bin/pip install \
		--upgrade \
		--disable-pip-version-check \
		pip wheel
	@venv/bin/pip install \
		--upgrade \
		--disable-pip-version-check \
		--requirement dev-requirements.txt \
		--requirement requirements.txt
	@touch $@

# cleaning
clean:
	@rm -f .git/py-format

distclean: clean
	@rm -rf venv

# docker
docker:
	@docker build \
		--tag slack-reddit \
		--network host \
		.

docker-run: docker
	@docker run \
		--rm \
		--tty \
		--interactive \
		--mount type=bind,source=$(PWD)/state,target=/app/state \
		slack-reddit

# testing
test-formatting: venv/.updated $(py-files)
	@venv/bin/black \
		--check \
		$(py-files)
	@venv/bin/isort \
		--multi-line 3 \
		--line-width 88 \
		--trailing-comma \
		--atomic \
		--virtual-env venv \
		--check-only \
		$(py-files)

test-mypy: venv/.updated $(py-files)
	@venv/bin/mypy \
		--cache-dir .git/mypy_cache \
		--python-executable venv/bin/python \
		--no-error-summary \
		--disallow-untyped-calls \
		--disallow-incomplete-defs \
		--warn-redundant-casts \
		--warn-return-any \
		--show-error-codes \
		--strict-equality \
		$(py-files)

test-pylint: venv/.updated $(py-files)
	@venv/bin/flake8 \
		--max-line-length=88 \
		--ignore=E203,W503 \
		--disable-noqa \
		$(py-files)
	@pylint \
		--score=no \
		--persistent=no \
		--jobs=0 \
		--extension-pkg-allow-list=math,termios \
		--disable=consider-using-enumerate,consider-using-with,duplicate-code,fixme,import-error,import-outside-toplevel,import-self,invalid-name,invalid-overridden-method,logging-fstring-interpolation,missing-class-docstring,missing-function-docstring,missing-module-docstring,no-name-in-module,no-value-for-parameter,raise-missing-from,subprocess-run-check,too-few-public-methods,too-many-ancestors,too-many-arguments,too-many-boolean-expressions,too-many-branches,too-many-instance-attributes,too-many-lines,too-many-locals,too-many-public-methods,too-many-return-statements,too-many-statements,unspecified-encoding,wrong-import-order \
		$(py-files)

test: test-formatting test-pylint test-mypy
