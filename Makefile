reformat:
	uv run ruff format modelo720

lint:
	uv run ruff check --fix modelo720

test:
	uv run pytest tests