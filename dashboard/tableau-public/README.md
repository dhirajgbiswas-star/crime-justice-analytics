# Public dashboards

Interactive HTML and Tableau workbook files in this folder are built from official CSA and ABS aggregates.

- [Victorian_Crime_Justice_Dashboard.html](Victorian_Crime_Justice_Dashboard.html) — open in a browser (Plotly; needs internet for the chart library)
- [Victorian_Crime_Justice.twbx](Victorian_Crime_Justice.twbx) — open in Tableau Desktop and save to Tableau Public

Five tabs: Overview, Geographic intelligence, Offenders and justice, National comparison, Data quality.

Do not blend recorded offences, criminal incidents, alleged offender incidents and ABS unique offenders.

CSV extracts under `data/` are not stored in git. Rebuild if required:

```bash
export PYTHONPATH=.
python -m src.dashboard.build
```

See `docs/tableau_guide.md`.
