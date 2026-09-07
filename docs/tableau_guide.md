# Tableau Public dashboards

Five interactive dashboards cover the analysis: statewide overview, geography, alleged offenders and justice, national ABS comparison, and data quality.

Do not blend **recorded offences**, **criminal incidents**, **alleged offender incidents** or **ABS unique offenders** as if they were the same measure.

## Open the public dashboard now

Double-click:

`dashboard/tableau-public/Victorian_Crime_Justice_Dashboard.html`

This is a Tableau Public–style interactive dashboard (year filter, metro/regional filter, five tabs, hover tooltips). CSA charts use year ending March. The National tab uses ABS financial years.

## Open in Tableau Desktop 2026.2 and publish to Tableau Public

Tableau Desktop (Apple silicon) 2026.2 is the authoring tool. Tableau Public is the free host.

1. Open `dashboard/tableau-public/Victorian_Crime_Justice.twbx`
2. Tableau will upgrade the workbook to 2026.2 on first save
3. Use the five dashboard tabs. **Year ending March** updates CSA KPI cards and selected-year charts. ABS national charts use financial year 2024–25 and are not driven by that parameter
4. **Server → Tableau Public → Save to Tableau Public…** (sign in with your Tableau Public account)
5. After publish, copy the Tableau Public URL into your portfolio

The packaged workbook includes `tableau_mart.csv`. Extract CSVs and a multi-sheet Excel file are also in `dashboard/tableau-public/data/` if you want to rebuild a sheet.

## Dashboard 1: Victorian Crime Overview

KPIs: recorded offences, offence rate per 100,000, criminal incidents, alleged offender incidents.

Visuals: statewide dual-axis trend, three official CSA products, year-on-year change, offence-division mix, investigation status.

## Dashboard 2: Geographic Crime Intelligence

Visuals: Victoria symbol map (LGA centroids), highest rates, highest counts, count versus rate, metro/regional trend, largest LGA year-on-year changes.

Use **rates** to compare LGAs. Melbourne leads recorded-offence *counts* as an activity centre. In 2026 the highest alleged-offender *rate* is Latrobe, not Melbourne.

Metropolitan / regional is an analytical grouping, not official CSA geography.

## Dashboard 3: Offenders and justice

Visuals: alleged-offender trend, youth versus adult, known sex, age groups, youth single year of age, principal offence, criminal-incident charge status, highest alleged-offender rate LGAs.

Alleged offender incidents are not unique people and are not findings of guilt.

## Dashboard 4: National comparison

ABS Recorded Crime – Offenders, financial year 2024–25.

KPIs: Victoria 59,693 unique offenders; Victoria rate 961.6; Australia rate 1,419.8; Victorian youth 7,644.

Visuals: state and territory rates, Victoria versus Australia rate trend, Victoria principal offence, youth trend, youth by jurisdiction, and a side-by-side reminder that CSA 195,342 incidents are not ABS 59,693 offenders.

Rates are per 100,000 persons aged 10 years and over. Do not blend this sheet with CSA alleged offender incidents.

## Dashboard 5: Data quality

Visuals: overall loaded-table score (100.0% on current extracts), row counts, missing values, negatives, duplicate keys, CSA and ABS catalogue links.

## Rebuild

```bash
cd crime-justice-analytics
export PYTHONPATH=.
python -m src.dashboard.build
```

HTML and Tableau extracts are always written. The `.twb` / `.twbx` files are generated when `cwtwb` is installed (`pip install cwtwb`).

Rebuild everything, including figures:

```bash
python -m src.pipeline --skip-ingest
```
