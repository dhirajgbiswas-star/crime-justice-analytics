"""Optional MySQL star-schema load from the SQLite analytical database."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from src.config import PROJECT_ROOT, SQLITE_PATH

ANALYTICAL_TABLES = [
    "statewide_offences",
    "lga_offence_totals",
    "lga_offences",
    "statewide_incidents",
    "lga_incident_totals",
    "statewide_offenders",
    "lga_offender_totals",
    "abs_offenders",
    "abs_offenders_trend",
    "abs_offenders_states_latest",
    "abs_offenders_states_totals",
    "abs_youth_offenders",
    "data_requests",
]


def mysql_config() -> dict[str, str]:
    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": os.getenv("MYSQL_PORT", "3306"),
        "database": os.getenv("MYSQL_DATABASE", "victorian_crime"),
        "user": os.getenv("MYSQL_USER", "crime_analyst"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
    }


def _mysql_engine():
    from sqlalchemy import create_engine

    cfg = mysql_config()
    if not cfg["password"]:
        raise RuntimeError("MYSQL_PASSWORD is not set. Copy .env.example to .env.")
    url = (
        f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    )
    return create_engine(url)


def build_star_frames() -> dict[str, pd.DataFrame]:
    """Construct dimension and fact tables from official CSA/ABS extracts."""
    sqlite_url = f"sqlite:///{SQLITE_PATH}"
    from sqlalchemy import create_engine

    sqlite_engine = create_engine(sqlite_url)
    offences = pd.read_sql_query(
        """
        SELECT year, local_government_area, police_region, metro_regional,
               offence_count, rate_per_100_000_population AS rate_per_100000
        FROM lga_offence_totals
        WHERE is_region_total = 0
        """,
        sqlite_engine,
    )
    incidents = pd.read_sql_query(
        """
        SELECT year, local_government_area, police_region, metro_regional,
               incidents_recorded AS incident_count,
               rate_per_100_000_population AS rate_per_100000
        FROM lga_incident_totals
        WHERE is_region_total = 0
        """,
        sqlite_engine,
    )
    offenders = pd.read_sql_query(
        """
        SELECT year, local_government_area, police_region, metro_regional,
               alleged_offender_incidents,
               rate_per_100_000_population AS rate_per_100000
        FROM lga_offender_totals
        WHERE is_region_total = 0
        """,
        sqlite_engine,
    )
    lga_rows = pd.concat(
        [
            offences[["local_government_area", "police_region", "metro_regional"]],
            incidents[["local_government_area", "police_region", "metro_regional"]],
            offenders[["local_government_area", "police_region", "metro_regional"]],
        ],
        ignore_index=True,
    ).drop_duplicates(subset=["local_government_area"])
    dim_lga = lga_rows.reset_index(drop=True)
    dim_lga.insert(0, "lga_key", range(1, len(dim_lga) + 1))

    years = sorted(
        set(offences["year"].dropna().astype(int))
        | set(incidents["year"].dropna().astype(int))
        | set(offenders["year"].dropna().astype(int))
    )
    dim_date = pd.DataFrame(
        {
            "date_key": years,
            "year": years,
            "year_ending": [f"March {year}" for year in years],
        }
    )
    offence_dim_src = pd.read_sql_query(
        """
        SELECT DISTINCT offence_division, offence_subdivision, offence_subgroup
        FROM statewide_offences
        """,
        sqlite_engine,
    )
    dim_offence = offence_dim_src.reset_index(drop=True)
    dim_offence.insert(0, "offence_key", range(1, len(dim_offence) + 1))

    fact_recorded = offences.merge(
        dim_lga[["lga_key", "local_government_area"]],
        on="local_government_area",
        how="left",
    )[["year", "lga_key", "offence_count", "rate_per_100000"]]
    fact_incident = incidents.merge(
        dim_lga[["lga_key", "local_government_area"]],
        on="local_government_area",
        how="left",
    )[["year", "lga_key", "incident_count", "rate_per_100000"]]
    fact_offender = offenders.merge(
        dim_lga[["lga_key", "local_government_area"]],
        on="local_government_area",
        how="left",
    )[["year", "lga_key", "alleged_offender_incidents", "rate_per_100000"]]

    try:
        fact_abs = pd.read_sql_query(
            """
            SELECT year_end, financial_year, jurisdiction, sex, age_group,
                   principal_offence, offence_level, offender_count,
                   rate_per_100000_age_10_plus
            FROM abs_offenders
            """,
            sqlite_engine,
        )
    except Exception:
        fact_abs = pd.DataFrame()

    return {
        "dim_date": dim_date,
        "dim_lga": dim_lga,
        "dim_offence": dim_offence,
        "fact_recorded_offence": fact_recorded,
        "fact_criminal_incident": fact_incident,
        "fact_alleged_offender": fact_offender,
        "fact_abs_offender": fact_abs,
    }


def load_sqlite_table_to_mysql(table_name: str) -> None:
    """Copy one SQLite table into MySQL if the server is reachable."""
    from sqlalchemy import create_engine

    sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH}")
    mysql_engine = _mysql_engine()
    df = pd.read_sql_table(table_name, sqlite_engine)
    df.to_sql(table_name, mysql_engine, if_exists="replace", index=False)


def load_mysql_warehouse() -> list[str]:
    """Load star-schema tables and selected analytical copies into MySQL."""
    from sqlalchemy import create_engine, text

    mysql_engine = _mysql_engine()
    sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH}")
    written: list[str] = []
    for name, frame in build_star_frames().items():
        if frame.empty:
            continue
        frame.to_sql(name, mysql_engine, if_exists="replace", index=False)
        written.append(name)
    for table_name in ANALYTICAL_TABLES:
        try:
            df = pd.read_sql_table(table_name, sqlite_engine)
        except Exception:
            continue
        df.to_sql(table_name, mysql_engine, if_exists="replace", index=False)
        written.append(table_name)
    with mysql_engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE OR REPLACE VIEW vw_crime_summary AS
                SELECT year, SUM(offence_count) AS recorded_offences
                FROM fact_recorded_offence
                GROUP BY year
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE OR REPLACE VIEW vw_abs_offender_summary AS
                SELECT year_end, jurisdiction, SUM(offender_count) AS offenders
                FROM fact_abs_offender
                WHERE offence_level = 'total'
                  AND sex = 'Persons'
                  AND age_group = 'All ages 10+'
                GROUP BY year_end, jurisdiction
                """
            )
        )
    return written


def try_load_mysql() -> list[str] | None:
    """Load MySQL when credentials and a server are available; otherwise skip."""
    if not mysql_config()["password"]:
        print("MySQL skipped: MYSQL_PASSWORD is not set.")
        return None
    if not SQLITE_PATH.exists():
        print("MySQL skipped: SQLite database is missing.")
        return None
    try:
        written = load_mysql_warehouse()
    except Exception as exc:
        print(f"MySQL skipped: {exc}")
        return None
    print(f"MySQL loaded {len(written)} tables")
    return written


if __name__ == "__main__":
    print("Optional MySQL load. Start Docker with `docker compose up -d`, then:")
    print("  PYTHONPATH=. python -m src.database.load_data")
    print(f"SQLite source: {SQLITE_PATH}")
    print(f"Schema file: {PROJECT_ROOT / 'sql' / 'schema.sql'}")
    result = try_load_mysql()
    if result:
        for name in result:
            print(f"  {name}")
