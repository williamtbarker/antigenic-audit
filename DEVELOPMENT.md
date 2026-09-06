# Development

## Setup

Install Python 3.10+ and [uv](https://docs.astral.sh/uv/), then run:

```bash
uv sync --all-extras --locked
```

## Quality checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest --cov=antigenic_audit --cov-report=term-missing
uv build
```

`make verify` runs the same sequence. To apply safe formatting changes, run `make format`.

## Design constraints

- Runtime code uses only the Python standard library.
- Audit results must be deterministic for identical inputs and arguments.
- Validation is model-development data for all leakage and temporal checks.
- A new finding must map to a documented policy, severity, and test fixture.
- Input failures should produce a concise message and exit code `1`, not a traceback.
- Examples must remain synthetic unless redistribution and provenance are documented.
