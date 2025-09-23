.PHONY: init
init: .venv node_modules
	[ -x .git/hooks/pre-commit ] || uv run pre-commit install

.venv: pyproject.toml uv.lock
	uv sync
	@touch $@

node_modules: package.json yarn.lock
	yarn install
	@touch $@

.playwright-browsers: pyproject.toml
	uv run playwright install --with-deps chromium
	@touch $@

.PHONY: collectstatic
collectstatic: .venv build-js
	uv run manage.py collectstatic --noinput

.PHONY: build-js
build-js: node_modules
	yarn run build

.PHONY: migrate
migrate:
	uv run manage.py migrate

.PHONY: mailpit
mailpit:
	docker compose up -d mailpit

.PHONY: dev
dev: init collectstatic migrate mailpit
	yarn run dev

.PHONY: test-unit
test-unit: .venv
	uv run pytest -m "not e2e" -x

.PHONY: test-e2e
test-e2e: .playwright-browsers collectstatic
	# https://pytest-xdist.readthedocs.io/en/stable/distribution.html
	uv run pytest -m e2e -n logical -x

.PHONY: test
test: test-unit test-e2e

.PHONY: coverage
coverage:
	uv run coverage run -m pytest
	uv run coverage html
	open htmlcov/index.html

.PHONY: lint
lint: init
	uv run pre-commit run -a
