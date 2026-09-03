.PHONY: sync format lint typecheck test build verify examples clean

sync:
	uv sync --all-extras --locked

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff format --check .
	uv run ruff check .

typecheck:
	uv run mypy

test:
	uv run pytest --cov=antigenic_audit --cov-report=term-missing

build:
	uv build

verify: lint typecheck test build examples

examples:
	uv run antigenic-audit audit examples/clean_pairs.csv
	@status=0; uv run antigenic-audit audit examples/leaky_pairs.csv \
		--format json >/dev/null || status=$$?; test $$status -eq 2

clean:
	rm -rf build dist htmlcov
