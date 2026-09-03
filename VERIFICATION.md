# Verification record

- Date: 2026-09-03
- Release candidate: 0.1.0
- Live-run platform: Linux x86-64

## Release gate

| Check | Result |
|---|---|
| Ruff formatting | Pass; 22 files formatted |
| Ruff lint | Pass; no findings |
| mypy strict mode | Pass; 15 source/test files checked |
| pytest | Pass; 54 tests |
| Branch-aware coverage | Pass; 97.52% total |
| Python 3.10.20 | Pass; 54 tests and clean-example smoke test |
| Python 3.12.13 | Pass; full `make verify` |
| Python 3.14.6 | Pass; 54 tests and clean-example smoke test |
| Wheel and source build | Pass |
| Isolated wheel install | Pass on system Python 3.12.3 |
| Console and `python -m` entry points | Pass |
| Wheel dependency consistency | Pass; one package, no runtime dependencies |
| Wheel/sdist metadata | Pass with Twine |
| Version-control/sdist file manifest | Pass; 32 files/directories match |
| `CITATION.cff` schema | Pass against CFF 1.2.0 |
| Lockfile freshness | Pass |

GitHub Actions additionally defines Python 3.10, 3.12, and 3.14 jobs on Linux and a
Python 3.12 job on macOS. Those hosted jobs cannot run until the repository is published.

## Behavioral smoke tests

```text
clean_pairs.csv  -> PASS, process exit 0
leaky_pairs.csv  -> FAIL, process exit 2
```

The failing fixture detected an exact pair overlap, a reused test virus, a non-forward
time boundary, and a future antiserum. The passing fixture still reports allowed
known-antiserum reuse as informational findings.

## Review boundary

Passing these checks establishes software consistency for the tested cases. It does not
establish correctness on a real laboratory dataset, cross-platform success outside the
listed environments, or biological validity. In particular, identifier aliases and
phylogenetic similarity remain upstream responsibilities.
