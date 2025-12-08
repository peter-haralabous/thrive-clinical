# Makefile for common dev tasks

.PHONY: dev setup serve

# default port can be overridden: make dev PORT=3000
PORT ?= 8000

# Run setup (installs pre-commit if needed and registers hooks)
setup:
	@echo "Running repository setup..."
	@bash scripts/setup.sh

# Start a simple static server on port $(PORT)
serve:
	@echo "Starting local server at http://localhost:$(PORT)"
	@python3 -m http.server $(PORT)

# Dev: run setup, then start server, open browser and watch for changes
dev: setup
	@echo "Starting dev environment (port=$(PORT))"
	@bash scripts/dev.sh $(PORT)
