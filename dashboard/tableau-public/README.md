# Public dashboards

Generated HTML, Tableau extracts and `.twbx` packages are not stored in git because they contain statistical extracts.

Rebuild after the SQLite database exists:

```bash
export PYTHONPATH=.
python -m src.dashboard.build
```

Then open:

- `Victorian_Crime_Justice_Dashboard.html`
- `Victorian_Crime_Justice.twbx` in Tableau Desktop, and publish to Tableau Public if required

See `docs/tableau_guide.md`.
