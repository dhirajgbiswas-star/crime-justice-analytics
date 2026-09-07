# Data quality

The quality framework scores **loaded statistical tables**, not police recording practice.

## Dimensions

| Dimension | Rule |
|---|---|
| Completeness | Share of non-null count columns |
| Validity | No negative counts or rates |
| Uniqueness | No duplicate natural business keys |
| Consistency | Multi-year tables span at least eight years |
| Timeliness | Latest CSA year is 2026 |

Overall score is a weighted mean: completeness 25%, validity 25%, uniqueness 20%, consistency 15%, timeliness 15%.

Outputs:

- `data/exports/data_quality_report.csv`
- `reports/generated/data_quality_report.html`

CSA Stage 1–2 tables scored **100.0%** after ingest (no missing counts, negatives or duplicate keys). ABS time series are included in Stage 3 with `year_end` as the year field.

## Known limitations

- CSA confidentialises some homicide and sexual-offence counts of three or fewer.
- ABS randomly adjusts cells. Division sums may differ slightly from printed totals.
- `metro_regional` is an analytical grouping, not a CSA classification.
- Re-ingest used to wipe `data_requests`. The rebuild now exports and restores that table.

## Source metadata

`data/processed/source_metadata.json` records publisher, licence, catalogue URL, reporting period and extraction timestamp for every ingested workbook.
