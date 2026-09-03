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

## AI-assisted development disclosure

The initial concept, implementation, tests, and documentation were developed with OpenAI
Codex under human direction. Candidate ideas were screened against recent literature and
existing tools, and the generated package was subjected to formatting, lint, strict type,
test, coverage, Python 3.10/3.12/3.14, build, and clean-install checks. This disclosure does
not transfer scientific responsibility: maintainers must review the assumptions and
outputs before publication or use.
