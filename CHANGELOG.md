# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-03

### Added

- Four explicit evaluation policies: prospective, strain-holdout, pair-holdout, and
  cold-both.
- Directed-pair, same-role, and reversed-role leakage checks against train and validation.
- Temporal-boundary and future-antiserum checks.
- MAE, RMSE, and tie-aware Spearman metrics stratified by test-virus year and pair lag.
- Deterministic Markdown and JSON reports with CI-oriented exit codes.
- CSV, TSV, gzip, and custom-column support.
- Synthetic passing and deliberately failing examples.

[Unreleased]: https://github.com/williamtbarker/antigenic-audit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/williamtbarker/antigenic-audit/releases/tag/v0.1.0
