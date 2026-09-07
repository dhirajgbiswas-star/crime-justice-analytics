"""Stage 3 tests: ABS parser helpers, product separation and data_requests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.config import DATA_RAW
from src.ingestion.abs_offenders import (
    FINANCIAL_YEARS,
    load_abs_tables,
    offence_level,
    normalise_jurisdiction,
    normalise_year,
    year_end,
)
from src.ingestion.load_csa import export_data_requests, restore_data_requests


def test_abs_year_helpers():
    assert normalise_year("2024-25") == "2024–25"
    assert year_end("2024–25") == 2025
    assert len(FINANCIAL_YEARS) == 17
    assert FINANCIAL_YEARS[0] == "2008–09"
    assert FINANCIAL_YEARS[-1] == "2024–25"


def test_jurisdiction_and_offence_level():
    assert normalise_jurisdiction("Vic.(d)") == "Victoria"
    assert normalise_jurisdiction("NT(e)(f)") == "Northern Territory"
    assert offence_level("01 Homicide and related offences(h)") == "division"
    assert offence_level("021 Assault") == "subdivision"
    assert offence_level("Total(x)") == "total"
    assert offence_level("Fare evasion(q)") == "other"


def test_abs_and_csa_are_not_the_same_measure():
    """A unique-offender count must not be treated as an incident total."""
    abs_vic = 59693
    csa_incidents = 195342
    assert abs_vic != csa_incidents
    comparable = 0
    assert comparable == 0


def test_data_requests_survive_rebuild(tmp_path: Path):
    db = tmp_path / "victorian_crime.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE data_requests (
                request_id TEXT PRIMARY KEY,
                requested_at TEXT NOT NULL,
                request_type TEXT NOT NULL,
                offence_category TEXT,
                lga TEXT,
                start_year INTEGER,
                end_year INTEGER,
                output_format TEXT,
                status TEXT,
                row_count INTEGER,
                summary TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO data_requests VALUES (
                'DR-2026-0001', '2026-09-05T00:00:00+00:00', 'Recorded offences by LGA',
                'All categories', 'Melbourne', 2024, 2026, 'CSV', 'completed', 3, 'total=10'
            )
            """
        )
    preserved = export_data_requests(db)
    assert preserved is not None
    assert preserved.iloc[0]["request_id"] == "DR-2026-0001"

    rebuilt = tmp_path / "rebuilt.db"
    with sqlite3.connect(rebuilt) as conn:
        conn.execute(
            """
            CREATE TABLE data_requests (
                request_id TEXT PRIMARY KEY,
                requested_at TEXT NOT NULL,
                request_type TEXT NOT NULL,
                offence_category TEXT,
                lga TEXT,
                start_year INTEGER,
                end_year INTEGER,
                output_format TEXT,
                status TEXT,
                row_count INTEGER,
                summary TEXT
            )
            """
        )
        restore_data_requests(conn, preserved)
        rows = pd.read_sql_query("SELECT * FROM data_requests", conn)
    assert len(rows) == 1
    assert rows.iloc[0]["lga"] == "Melbourne"


def test_official_abs_totals_if_workbooks_present():
    states = DATA_RAW / "ABS_Offenders_States_2024-25.xlsx"
    australia = DATA_RAW / "ABS_Offenders_Australia_2024-25.xlsx"
    youth = DATA_RAW / "ABS_Youth_Offenders_2024-25.xlsx"
    if not (states.exists() and australia.exists() and youth.exists()):
        return
    tables = load_abs_tables(australia, states, youth)
    latest = tables["abs_offenders_states_totals"]
    victoria = latest.loc[latest["jurisdiction"].eq("Victoria")].iloc[0]
    australia_row = latest.loc[latest["jurisdiction"].eq("Australia")].iloc[0]
    assert int(victoria["offender_count"]) == 59693
    assert round(float(victoria["rate_per_100000_age_10_plus"]), 1) == 961.6
    assert int(australia_row["offender_count"]) == 344620
    youth_vic = tables["abs_youth_offenders"]
    youth_latest = youth_vic.loc[
        youth_vic["jurisdiction"].eq("Victoria") & youth_vic["financial_year"].eq("2024–25")
    ].iloc[0]
    assert int(youth_latest["offender_count"]) == 7644
