# Contributing

Focused bug reports and small, tested changes are welcome.

1. Open an issue describing the evaluation policy or failure mode involved.
2. Create a branch from `main`.
3. Add or update tests, including an adversarial case when behavior changes.
4. Run `make verify`.
5. Submit a pull request describing the scientific assumption behind the change.

Please do not add a new “leakage” rule without documenting which deployment claim it
protects. Structural overlap is not automatically invalid; policy and intended use matter.

Do not submit private, controlled, or personally identifying surveillance data. Minimal
synthetic reproductions are preferred.
