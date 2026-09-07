# Data request process

1. User submits a request in the Streamlit app (`app/streamlit_app.py`).
2. The app validates years, LGA and request type against the analytical database.
3. It queries SQLite (MySQL optional) and returns aggregate statistics only.
4. A request ID of the form `DR-YYYY-0001` is stored in `data_requests`. Re-ingest exports and restores this table so the audit log is not wiped.
5. CSV or Excel is generated for download.
6. Each response includes a methodology note distinguishing offences, incidents and alleged offender incidents.

Sensitive individual-level extracts are out of scope.
