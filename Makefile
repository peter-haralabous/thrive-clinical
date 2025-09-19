.PHONY: init
init: .venv node_modules
	[ -x .git/hooks/pre-commit ] || uv run pre-commit install

.venv: pyproject.toml uv.lock
	uv sync
	@touch $@

node_modules: package.json yarn.lock
	yarn install
	@touch $@

build-js: package.json yarn.lock
	yarn run build

.PHONY: migrate
migrate:
	uv run manage.py migrate

.PHONY: mailpit
mailpit:
	docker compose up -d mailpit

.PHONY: dev
dev: init migrate mailpit
	yarn run dev

.PHONY: test-unit
test-unit: init
	uv run pytest -m "not e2e" -x

.playwright-browsers: pyproject.toml
	uv run playwright install --with-deps chromium
	@touch $@

.PHONY: collectstatic
collectstatic:
	uv run manage.py collectstatic --noinput

.PHONY: test-e2e-browser
test-e2e-browser: .playwright-browsers

.PHONY: test-e2e
test-e2e: init node_modules build-js test-e2e-browser collectstatic
	# https://pytest-xdist.readthedocs.io/en/stable/distribution.html
	uv run pytest -m e2e -n logical -x

.PHONY: test-branch
test: test-unit test-e2e

.PHONY: lint
lint: init
	uv run pre-commit run -a
