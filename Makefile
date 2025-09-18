.PHONY: init
init: .venv node_modules
	[ -x .git/hooks/pre-commit ] || uv run pre-commit install

.venv: pyproject.toml uv.lock
	uv sync
	@touch $@

node_modules: package.json yarn.lock
	yarn install
	@touch $@

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
test-unit: init migrate
	uv run pytest -x

.PHONY: test-e2e
test-e2e: init migrate
	# https://pytest-xdist.readthedocs.io/en/stable/distribution.html
	uv run pytest -m e2e -n logical -x

.PHONY: test
test: test-unit test-e2e

.PHONY: lint
lint: init
	uv run pre-commit run -a
