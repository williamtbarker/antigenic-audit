# Project selection report

## Decision

Build a small, dependency-free auditor for pairwise influenza antigenicity evaluations.
The useful unit is not another prediction model; it is a reproducible check that asks
whether a reported score matches the claimed deployment setting.

## Trigger

The 2026 FluEmbed paper reports alignment-free prediction of H3N2 cross-reactivity and
evaluates behavior outside training-era ranges. Its temporal results point to a general
reproducibility problem: a headline score is hard to interpret unless readers can inspect
which viruses and antisera crossed the development/test boundary.

Primary trigger:

- Gunderson, J. et al. (2026), “Alignment-free prediction of cross-reactivity in influenza
  A (H3N2) anticipates antigenic drift,” DOI
  [10.1371/journal.pcbi.1014628](https://doi.org/10.1371/journal.pcbi.1014628).

Relevant prior art:

- Joeres, R. et al. (2025), “DataSAIL: Data Splitting Against Information Leakage,” DOI
  [10.1038/s41467-025-58606-8](https://doi.org/10.1038/s41467-025-58606-8).

## Candidate screen

| Candidate | Utility | Feasible in one week | Differentiation | Decision |
|---|---:|---:|---:|---|
| Companion workflow for a new influenza pipeline paper | High | Medium | Low; the paper already ships a mature workflow | Reject |
| Viral-dataset manifest/lockfile tool | Medium | High | Low; data lockfiles and viral download wrappers already exist | Reject |
| Generic biological pairwise leakage splitter | High | Medium | Low; DataSAIL substantially covers the general problem | Reject |
| Role-aware temporal audit for influenza antigenicity tables | High | High | Medium; narrow policy semantics and review artifacts | Select |

## Scope and novelty claim

The project does **not** claim a new leakage algorithm. Its contribution is a compact,
domain-specific review layer with:

- explicit target-virus and reference-antiserum roles;
- cross-role identity checks;
- train-plus-validation development semantics;
- a strict prospective time-boundary policy;
- future-antiserum diagnostics; and
- metrics by target-virus year and virus–antiserum lag.

That combination was not found as a standalone package during the candidate screen.
Absence from a limited search is not proof of novelty, so the public claim should remain
“a focused evaluation auditor,” not “the first.”

## Why Python

The core is table validation and statistics, where Python minimizes contributor friction
in bioinformatics. Avoiding runtime dependencies keeps installation and audit behavior
simple. Rust would add packaging cost without materially improving this small, I/O-bound
tool. Under the weekly-project cadence, one of the next three ready releases should be in
Rust.

## Strongest reason not to publish

Strain identifiers are not normalized and phylogenetic relatedness is not measured. A
table can pass while near-identical viruses use different strings, so “leakage-free” would
be an overclaim. Publish only if the README’s structural-audit boundary is acceptable and
the project is presented as an alpha-quality review aid.
