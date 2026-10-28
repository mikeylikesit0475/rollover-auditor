.PHONY: sync test lint test-strict run report
sync:
	uv sync
test:
	uv run pytest
lint:
	uv run ruff check src tests
	uv run mypy src
test-strict: lint test
run:
	uv run uvicorn rollover.main:app --reload --port 8010
report:
	uv run python -c "print('use /report endpoint')"
