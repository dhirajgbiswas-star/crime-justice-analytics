# Architecture

The Victorian Crime & Justice Intelligence Analytics Platform is a local-first analytics stack. Official Excel releases are ingested once, analysed in SQLite, and published as CSV, HTML, figures and Tableau extracts.

```
Official CSA / ABS Excel
        │
        ▼
src/ingestion  →  data/raw (never overwritten)
        │
        ▼
SQLite  data/processed/victorian_crime.db
        │
        ├── src/analytics   SQL + Python descriptive analysis
        ├── src/validation  loaded-table quality scores
        ├── src/reporting   HTML / Excel briefing
        ├── src/dashboard   Tableau Public workbook and HTML
        ├── app/            Streamlit data-request service
        └── src/database    optional MySQL star schema
```

## Defaults

- **SQLite** is the analytical database. It is rebuilt by `python -m src.pipeline`.
- **`data_requests`** is exported before a rebuild and restored afterwards so the Streamlit audit log survives re-ingest.
- **MySQL** is optional. `docker compose up -d` starts MySQL 8.4. `src/database/load_data.py` copies dimension, fact and selected analytical tables when `.env` credentials work.
- **ABS tables** live beside CSA tables. They are never unioned into CSA alleged-offender incident measures.

## Runtime

Run commands from `crime-justice-analytics/` with `PYTHONPATH=.`.

| Command | Purpose |
|---|---|
| `python -m src.pipeline` | Full ingest, exports, figures, briefing, dashboards |
| `python -m src.pipeline --abs-only` | Refresh ABS tables only |
| `python -m src.pipeline --skip-ingest` | Reuse SQLite |
| `pytest` | Transformation and parser tests |
| `streamlit run app/streamlit_app.py` | Data-request service |

## Layers

- **Ingestion:** `src/ingestion/load_csa.py`, `stage2.py`, `abs_offenders.py`
- **Analysis:** `src/analytics/descriptive.py`, `incidents.py`, `offender.py`, `national.py`
- **SQL:** `sql/crime_analysis.sql`, `stage2_analysis.sql`, `stage3_analysis.sql`
- **Presentation:** matplotlib figures, Streamlit, Plotly HTML dashboard, Tableau workbook
