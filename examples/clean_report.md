# Antigenic evaluation audit

- **Outcome:** `PASS`
- **Policy:** `prospective`
- **Records:** 12 (6 train, 0 validation, 6 test)

## Temporal boundary

- Development virus years: `1968`–`1979`
- Test virus years: `1982`–`1987`
- Earliest-test minus latest-development boundary: `3` years

## Metrics

| Group | n | MAE | RMSE | Spearman ρ |
|---|---:|---:|---:|---:|
| Train | 6 | 0.1667 | 0.1732 | 1.0000 |
| Validation | 0 | NA | NA | NA |
| Development | 6 | 0.1667 | 0.1732 | 1.0000 |
| Test | 6 | 0.2667 | 0.2769 | 0.9856 |

### Test metrics by virus year

| Virus year | n | MAE | RMSE | Spearman ρ |
|---|---:|---:|---:|---:|
| 1982 | 2 | 0.2500 | 0.2550 | 1.0000 |
| 1985 | 2 | 0.3000 | 0.3162 | 1.0000 |
| 1987 | 2 | 0.2500 | 0.2550 | 1.0000 |

### Test metrics by virus–antiserum lag

| Lag (years) | n | MAE | RMSE | Spearman ρ |
|---|---:|---:|---:|---:|
| 3-5 | 1 | 0.2000 | 0.2000 | NA |
| 6-10 | 4 | 0.2750 | 0.2872 | 0.9487 |
| >10 | 1 | 0.3000 | 0.3000 | NA |

## Findings

### INFO · `KNOWN_TEST_ANTISERUM` (1)

Test antisera also occur in development; this is expected for known-sera deployment.

Examples: `A/Victoria/3/1975`

### INFO · `TEST_ANTISERUM_SEEN_AS_DEVELOPMENT_VIRUS` (2)

Test antisera occur as development target viruses.

Examples: `A/Bangkok/1/1979`; `A/Victoria/3/1975`

## Interpretation boundary

This report audits table structure, entity reuse, temporal direction, and supplied predictions. It does not establish biological validity, assay comparability, sequence independence, or prospective clinical utility.
