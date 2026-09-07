# Victorian Crime & Justice Intelligence Analytics Platform

Public-sector analytics portfolio using official Crime Statistics Agency and Australian Bureau of Statistics open data.

**Stage 1** recorded offences. **Stage 2** criminal incidents, alleged offender incidents, quality scoring and Streamlit. **Stage 3** ABS Recorded Crime – Offenders, automated briefing, preserved data-request log, documentation and a usable MySQL star-schema load.

Recorded offences, criminal incidents, alleged offender incidents and ABS unique offenders are **different statistical products**. They are not interchangeable.

## What the platform delivers

| Deliverable | Location |
|---|---|
| Official CSA and ABS workbooks | `data/raw/` via `src/ingestion/download.py` |
| SQL analysis | `sql/crime_analysis.sql`, `stage2_analysis.sql`, `stage3_analysis.sql` |
| Python analytics | `src/analytics/` including `national.py` |
| Visualisations | 27 charts in `reports/generated/figures/` |
| Briefing | `reports/generated/victorian_crime_briefing.html` / `.xlsx` |
| Notebooks | `notebooks/01`–`11` |
| Data-quality score | `reports/generated/data_quality_report.html` |
| Streamlit data requests | `app/streamlit_app.py` |
| Tableau Public dashboards | `dashboard/tableau-public/` |
| Optional MySQL star schema | `docker-compose.yml`, `sql/schema.sql`, `src/database/load_data.py` |
| Documentation | `docs/architecture.md`, `data_dictionary.md`, `methodology.md`, `data_quality.md` |
| Tests | `tests/test_transformations.py`, `tests/test_stage3.py` |

## Data sources and download links

Publisher: **Crime Statistics Agency (Victoria)**. Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Publication date: 19 June 2026.

### Recorded offences

https://discover.data.vic.gov.au/dataset/data-tables-recorded-offences

- [Statewide](https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Recorded_Offences_Visualisation_Year_Ending_March_2026.xlsx)
- [By LGA](https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Recorded_Offences_Year_Ending_March_2026.xlsx)

### Criminal incidents

https://discover.data.vic.gov.au/dataset/criminal-incident

- [Statewide](https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Criminal_Incidents_Visualisation_Year_Ending_March_2026.xlsx)
- [By LGA](https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Criminal_Incidents_Year_Ending_March_2026.xlsx)

### Alleged offender incidents

https://discover.data.vic.gov.au/dataset/data-tables-alleged-offender-incidents

- [Statewide](https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Alleged_Offender_Incidents_Visualisation_Year_Ending_March_2026.xlsx)
- [By LGA](https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Alleged_Offenders_Year_Ending_March_2026.xlsx)

### ABS Recorded Crime – Offenders

https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/latest-release

- [Offenders, Australia](https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/1.%20Offenders%2C%20Australia.xlsx)
- [Offenders, states and territories](https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/2.%20Offenders%2C%20states%20and%20territories.xlsx)
- [Youth offenders](https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/3.%20Youth%20offenders.xlsx)

ABS counts **unique alleged offenders proceeded against** in a financial year. That is not CSA alleged offender incidents.

## Key results (year ending March 2026)

### Recorded offences
- **625,426** offences; rate **8,690.8** per 100,000; **+15.4%** since 2017

### Criminal incidents
- **468,711** incidents (**−1.0%** on 2025; **+12.6%** since 2017)
- About **1.3 recorded offences per criminal incident**
- Charge status: **55.6%** unsolved, **30.1%** charges laid, **14.3%** no charges laid

### Alleged offender incidents
- **195,342** alleged offender incidents (**+8.6%** on 2025; **+20.4%** since 2017)
- Among known sex: **78.4%** male, **21.6%** female
- Youth (ages 10–17): **22,654** incidents (**11.7%**); peak single year of age is **16**
- Leading principal offences: theft, assault, breaches of orders
- Highest alleged-offender **rate** LGA: **Latrobe** (not Melbourne)

These are alleged incidents, not unique people and not findings of guilt.

### ABS unique offenders (financial year 2024–25)
- Victoria: **59,693** offenders; rate **961.6** per 100,000 aged 10+ (**−3.0%** on 2023–24)
- Australia: **344,620** offenders; rate **1,419.8**
- Victoria’s rate is **67.7%** of the national rate and the lowest among the six states
- Victorian youth (10–17): **7,644** (**12.8%** of Victorian offenders)

Do not treat 59,693 ABS offenders as comparable to 195,342 CSA alleged offender incidents.

Overall loaded-table data-quality score: **100.0%** on CSA tables after ingest (missing counts, negatives and duplicate business keys were not found).

## Data is not in this repository

Official Excel workbooks, SQLite, CSV extracts and generated reports are excluded from git. Download the source files listed above (also in `data/README.md`) into `data/raw/` before running the pipeline.

## How to run

```bash
cd crime-justice-analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# download official workbooks into data/raw/ (see data/README.md)
export PYTHONPATH=.
python -m src.pipeline
pytest
PYTHONPATH=. streamlit run app/streamlit_app.py
```

Interactive Tableau Public dashboards (HTML you can open now, plus a Tableau workbook to publish):

```bash
PYTHONPATH=. python -m src.dashboard.build
open "dashboard/tableau-public/Victorian_Crime_Justice_Dashboard.html"
open -a "Tableau Desktop (Apple silicon) 2026.2" "dashboard/tableau-public/Victorian_Crime_Justice.twbx"
```

See `docs/tableau_guide.md` for the five dashboard tabs and how to **Save to Tableau Public**.

Refresh ABS tables only:

```bash
PYTHONPATH=. python -m src.pipeline --abs-only
```

Optional MySQL:

```bash
cp .env.example .env
docker compose up -d
PYTHONPATH=. python -m src.database.load_data
```

See `docs/architecture.md` and `docs/methodology.md`.

## Data governance

See `docs/data_governance.md`. Aggregate statistics only. Do not identify individuals.

## Author

Dhiraj Guha — Data Analyst / Data Engineer / BI portfolio project.
