lint:
	uv run ruff format --check

format:
	uv run ruff format

test:
	uv run pytest

.PHONY: lint format test
