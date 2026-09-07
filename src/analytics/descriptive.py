"""Descriptive, trend, geographic and offence-composition analysis."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.config import SQLITE_PATH


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or SQLITE_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def read_sql(sql: str, params: tuple | dict | None = None) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def statewide_annual_totals() -> pd.DataFrame:
    """Victoria-wide recorded offence counts and rates by year."""
    return read_sql(
        """
        SELECT
            year,
            year_ending,
            SUM(offence_count) AS offence_count,
            SUM(rate_per_100_000_population) AS rate_per_100000
        FROM statewide_offences
        GROUP BY year, year_ending
        ORDER BY year
        """
    )


def add_yoy(
    df: pd.DataFrame,
    value_col: str,
    prefix: str | None = None,
    year_col: str = "year",
) -> pd.DataFrame:
    """Add year-on-year count and percentage change columns."""
    sort_col = year_col if year_col in df.columns else "year_end"
    out = df.sort_values(sort_col).copy()
    label = prefix or value_col
    out[f"{label}_yoy"] = out[value_col].diff()
    out[f"{label}_yoy_pct"] = out[value_col].pct_change() * 100
    out[f"{label}_3yr_avg"] = out[value_col].rolling(3, min_periods=3).mean()
    return out


def offence_division_trends() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            offence_division,
            SUM(offence_count) AS offence_count,
            SUM(rate_per_100_000_population) AS rate_per_100000
        FROM statewide_offences
        GROUP BY year, offence_division
        ORDER BY year, offence_division
        """
    )


def offence_subdivision_change(start_year: int, end_year: int) -> pd.DataFrame:
    return read_sql(
        """
        WITH base AS (
            SELECT
                year,
                offence_division,
                offence_subdivision,
                SUM(offence_count) AS offence_count,
                SUM(rate_per_100_000_population) AS rate_per_100000
            FROM statewide_offences
            WHERE year IN (?, ?)
            GROUP BY year, offence_division, offence_subdivision
        )
        SELECT
            a.offence_division,
            a.offence_subdivision,
            a.offence_count AS start_count,
            b.offence_count AS end_count,
            b.offence_count - a.offence_count AS change_count,
            CASE WHEN a.offence_count = 0 THEN NULL
                 ELSE 100.0 * (b.offence_count - a.offence_count) / a.offence_count
            END AS change_pct,
            a.rate_per_100000 AS start_rate,
            b.rate_per_100000 AS end_rate
        FROM base a
        JOIN base b
          ON a.offence_subdivision = b.offence_subdivision
         AND a.offence_division = b.offence_division
        WHERE a.year = ? AND b.year = ?
        ORDER BY change_pct DESC
        """,
        (start_year, end_year, start_year, end_year),
    )


def latest_lga_snapshot() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            police_region,
            local_government_area,
            metro_regional,
            offence_count,
            rate_per_100_000_population AS rate_per_100000
        FROM lga_offence_totals
        WHERE is_region_total = 0
          AND year = (SELECT MAX(year) FROM lga_offence_totals)
        ORDER BY rate_per_100_000_population DESC
        """
    )


def lga_yoy_change() -> pd.DataFrame:
    return read_sql(
        """
        WITH ranked AS (
            SELECT
                year,
                police_region,
                local_government_area,
                metro_regional,
                offence_count,
                rate_per_100_000_population AS rate_per_100000,
                LAG(offence_count) OVER (
                    PARTITION BY local_government_area ORDER BY year
                ) AS prev_count,
                LAG(rate_per_100_000_population) OVER (
                    PARTITION BY local_government_area ORDER BY year
                ) AS prev_rate
            FROM lga_offence_totals
            WHERE is_region_total = 0
        )
        SELECT
            year,
            police_region,
            local_government_area,
            metro_regional,
            offence_count,
            rate_per_100000,
            offence_count - prev_count AS yoy_count,
            CASE WHEN prev_count = 0 THEN NULL
                 ELSE 100.0 * (offence_count - prev_count) / prev_count
            END AS yoy_pct,
            rate_per_100000 - prev_rate AS yoy_rate
        FROM ranked
        WHERE prev_count IS NOT NULL
        ORDER BY year, yoy_pct DESC
        """
    )


def metro_regional_trends() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            metro_regional,
            SUM(offence_count) AS offence_count,
            AVG(rate_per_100_000_population) AS avg_lga_rate_per_100000,
            COUNT(DISTINCT local_government_area) AS lga_count
        FROM lga_offence_totals
        WHERE is_region_total = 0
          AND metro_regional IS NOT NULL
        GROUP BY year, metro_regional
        ORDER BY year, metro_regional
        """
    )


def offence_composition_by_lga(year: int | None = None) -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            local_government_area,
            offence_division,
            SUM(offence_count) AS offence_count
        FROM lga_offences
        WHERE year = COALESCE(?, (SELECT MAX(year) FROM lga_offences))
        GROUP BY year, local_government_area, offence_division
        ORDER BY local_government_area, offence_count DESC
        """,
        (year,),
    )


def investigation_status_trends() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            investigation_status,
            SUM(offence_count) AS offence_count
        FROM statewide_investigation_status
        GROUP BY year, investigation_status
        ORDER BY year, offence_count DESC
        """
    )


def family_incident_share() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            family_incident_flag,
            SUM(offence_count) AS offence_count,
            SUM(rate_per_100_000_population) AS rate_per_100000
        FROM statewide_family_incidents
        GROUP BY year, family_incident_flag
        ORDER BY year, family_incident_flag
        """
    )


def data_quality_snapshot() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            'lga_offence_totals' AS table_name,
            COUNT(*) AS row_count,
            SUM(CASE WHEN local_government_area IS NULL OR local_government_area = '' THEN 1 ELSE 0 END) AS missing_lga,
            SUM(CASE WHEN offence_count IS NULL THEN 1 ELSE 0 END) AS missing_count,
            SUM(CASE WHEN offence_count < 0 THEN 1 ELSE 0 END) AS negative_count,
            SUM(CASE WHEN rate_per_100_000_population < 0 THEN 1 ELSE 0 END) AS negative_rate,
            COUNT(*) - COUNT(DISTINCT year || '|' || police_region || '|' || local_government_area) AS duplicate_keys
        FROM lga_offence_totals
        UNION ALL
        SELECT
            'lga_offences',
            COUNT(*),
            SUM(CASE WHEN local_government_area IS NULL OR local_government_area = '' THEN 1 ELSE 0 END),
            SUM(CASE WHEN offence_count IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN offence_count < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN lga_rate_per_100_000_population < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year || '|' || local_government_area || '|' || offence_subgroup)
        FROM lga_offences
        UNION ALL
        SELECT
            'statewide_offences',
            COUNT(*),
            0,
            SUM(CASE WHEN offence_count IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN offence_count < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rate_per_100_000_population < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year || '|' || offence_subgroup)
        FROM statewide_offences
        """
    )


def top_subgroups(year: int | None = None, n: int = 15) -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            offence_division,
            offence_subdivision,
            offence_subgroup,
            offence_count,
            rate_per_100_000_population AS rate_per_100000
        FROM statewide_offences
        WHERE year = COALESCE(?, (SELECT MAX(year) FROM statewide_offences))
        ORDER BY offence_count DESC
        LIMIT ?
        """,
        (year, n),
    )
