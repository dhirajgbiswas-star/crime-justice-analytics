"""Criminal-incident analysis from official CSA tables."""

from __future__ import annotations

import pandas as pd

from src.analytics.descriptive import add_yoy, read_sql


def statewide_incident_totals() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            year_ending,
            SUM(incidents_recorded) AS incident_count,
            SUM(rate_per_100_000_population) AS rate_per_100000
        FROM statewide_incidents
        GROUP BY year, year_ending
        ORDER BY year
        """
    )


def incident_division_trends() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            offence_division,
            SUM(incidents_recorded) AS incident_count,
            SUM(rate_per_100_000_population) AS rate_per_100000
        FROM statewide_incidents
        GROUP BY year, offence_division
        ORDER BY year, offence_division
        """
    )


def latest_lga_incidents() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            police_region,
            local_government_area,
            metro_regional,
            incidents_recorded AS incident_count,
            rate_per_100_000_population AS rate_per_100000
        FROM lga_incident_totals
        WHERE is_region_total = 0
          AND year = (SELECT MAX(year) FROM lga_incident_totals)
        ORDER BY rate_per_100_000_population DESC
        """
    )


def charge_status_share() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            charge_status,
            SUM(incidents_recorded) AS incident_count,
            ROUND(
                100.0 * SUM(incidents_recorded)
                / SUM(SUM(incidents_recorded)) OVER (PARTITION BY year),
                1
            ) AS share_pct
        FROM statewide_incident_charge_status
        GROUP BY year, charge_status
        ORDER BY year, share_pct DESC
        """
    )


def statistical_product_comparison() -> pd.DataFrame:
    """Compare recorded offences, criminal incidents and alleged offender incidents."""
    return read_sql(
        """
        WITH offences AS (
            SELECT year, SUM(offence_count) AS recorded_offences
            FROM statewide_offences
            GROUP BY year
        ),
        incidents AS (
            SELECT year, SUM(incidents_recorded) AS criminal_incidents
            FROM statewide_incidents
            GROUP BY year
        ),
        offenders AS (
            SELECT year, SUM(alleged_offender_incidents) AS alleged_offender_incidents
            FROM statewide_offenders
            GROUP BY year
        )
        SELECT
            o.year,
            o.recorded_offences,
            i.criminal_incidents,
            f.alleged_offender_incidents,
            ROUND(1.0 * o.recorded_offences / i.criminal_incidents, 2) AS offences_per_incident,
            ROUND(1.0 * f.alleged_offender_incidents / i.criminal_incidents, 2) AS offenders_per_incident
        FROM offences o
        JOIN incidents i ON o.year = i.year
        JOIN offenders f ON o.year = f.year
        ORDER BY o.year
        """
    )


def incident_family_share() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            family_incident_flag,
            SUM(incidents_recorded) AS incident_count,
            SUM(rate_per_100_000_population) AS rate_per_100000
        FROM statewide_incident_family
        GROUP BY year, family_incident_flag
        ORDER BY year, family_incident_flag
        """
    )


def incident_trend_with_yoy() -> pd.DataFrame:
    return add_yoy(statewide_incident_totals(), "incident_count")
