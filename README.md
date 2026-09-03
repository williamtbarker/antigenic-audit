# Antigenic Audit

[![CI](https://github.com/williamtbarker/antigenic-audit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/williamtbarker/antigenic-audit/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/williamtbarker/antigenic-audit)](https://github.com/williamtbarker/antigenic-audit/releases) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`antigenic-audit` is a dependency-free Python CLI that checks pairwise influenza
virus–antiserum evaluations for entity leakage, reversed-role leakage, and temporal
overclaiming before model results are published.

> **Status:** research prototype. It audits an evaluation table; it does not validate a
> biological model or replace expert review.

## Why this exists

An antigenicity model is often evaluated on pairs: a target virus and a reference
antiserum. A held-out pair can still reuse its virus, reuse its antiserum, or expose a
strain in the opposite role during development. Random pair splits can therefore answer
a much easier question than “will this generalize to a newly emerging strain?”

The 2026 FluEmbed study reported strong within-range performance and lower performance
on temporally out-of-range epochs, making the evaluation boundary itself worth auditing.
[DataSAIL](https://doi.org/10.1038/s41467-025-58606-8) addresses leakage-aware dataset
splitting broadly. Antigenic Audit takes a narrower role: it checks an already-produced
influenza pair table against an explicit deployment claim and emits a reviewable report
with stratified metrics.

## What it catches

- the same directed virus–antiserum pair in development and test;
- test viruses seen as either viruses or antisera during development;
- test antisera seen in either role when a cold-both claim is requested;
- non-forward year boundaries for prospective evaluation;
- antisera whose strain year is later than the paired test-virus year;
- duplicate pairs that can overweight aggregate metrics;
- headline metrics hiding performance changes by virus year or virus–antiserum lag.

“Development” always means `train + validation`; validation leakage is not ignored.

## Quick start

Requirements: Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-extras --locked
uv run antigenic-audit audit examples/clean_pairs.csv
```

The clean synthetic example returns exit code `0`. The deliberately leaky example emits
a failing JSON report and returns exit code `2`:

```bash
uv run antigenic-audit audit examples/leaky_pairs.csv --format json
```

After the repository is public, it can also be run directly from GitHub:

```bash
uvx --from git+https://github.com/williamtbarker/antigenic-audit \
  antigenic-audit audit pairs.csv --policy prospective
```

## Input contract

CSV, TSV, and gzip-compressed forms are supported. Each non-empty row must contain:

| Column | Meaning |
|---|---|
| `split` | `train`, `validation`, or `test` |
| `virus_id` | Stable identifier of the target/test virus |
| `antiserum_id` | Stable identifier of the antiserum's reference strain |
| `virus_year` | Target-virus year, from 1800 through 2200 |
| `antiserum_year` | Antiserum reference-strain year, from 1800 through 2200 |
| `observed` | Finite observed response on a consistent numeric scale |
| `predicted` | Finite model prediction on the same scale |

Column and split-label names can be remapped from the command line. Run
`antigenic-audit audit --help` for all options.

Identifiers are compared as trimmed, case-sensitive strings. They should be normalized
upstream: aliases such as `A/Hong Kong/1/68` and `A/HongKong/1/1968` are not inferred to
be the same strain.

## Policies

| Policy | Enforced claim |
|---|---|
| `prospective` | Test viruses are unseen in either role and strictly later than every development target virus; known reference antisera are allowed. |
| `strain-holdout` | Test viruses are unseen in either role; no chronological claim is required. |
| `pair-holdout` | Only the exact directed pair must be absent from development; entity reuse is reported as information. |
| `cold-both` | Both test viruses and test antisera are absent from development in either role. |

`prospective` is the default because it encodes the strongest common claim about an
emerging target virus. A future antiserum is a warning under that policy, not an error,
because whether it invalidates the experiment depends on the intended use.

## Output and CI behavior

Reports are Markdown by default and deterministic JSON with `--format json`. They contain
MAE, RMSE, and tie-aware Spearman correlation for train, validation, combined development,
test, each test-virus year, and virus–antiserum year-lag bins.

| Exit code | Meaning |
|---:|---|
| `0` | No error-level finding (`WARN` also returns 0 by default) |
| `1` | Invalid input, configuration, or output path |
| `2` | Audit failure, or warning when `--fail-on warning` is used |

Example CI gate:

```bash
uv run antigenic-audit audit results/pairs.csv \
  --policy prospective \
  --fail-on warning \
  --format json \
  --output antigenic-audit.json
```

## Reproduce the package checks

```bash
make verify
```

This checks formatting, lint, strict typing, branch-aware test coverage, and both wheel
and source-distribution builds. See [DEVELOPMENT.md](DEVELOPMENT.md) for individual
commands.

## Scientific boundary

This tool cannot determine whether titers from different assays or laboratories are
comparable, whether strain aliases were normalized, whether sequences are phylogenetically
independent, whether metadata years are historically correct, or whether a model is useful
for surveillance or clinical decisions. Its example data are synthetic. A passing report
means only that the supplied table satisfies the selected structural policy.

## Research basis

- Gunderson, J. et al. (2026). “Alignment-free prediction of cross-reactivity in influenza
  A (H3N2) anticipates antigenic drift.” *PLOS Computational Biology*.
  <https://doi.org/10.1371/journal.pcbi.1014628>
- Joeres, R. et al. (2025). “DataSAIL: Data Splitting Against Information Leakage.”
  *Nature Communications*. <https://doi.org/10.1038/s41467-025-58606-8>

The project is independent of those author teams and is not an official companion to
either paper.

## License

MIT. See [LICENSE](LICENSE).
