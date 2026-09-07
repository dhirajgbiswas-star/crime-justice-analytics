"""Alleged-offender analysis from official CSA tables.

These are alleged offender incidents, not proven offences or unique people.
"""

from __future__ import annotations

import pandas as pd

from src.analytics.descriptive import add_yoy, read_sql


def statewide_offender_totals() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            year_ending,
            SUM(alleged_offender_incidents) AS alleged_offender_incidents,
            SUM(rate_per_100_000_population_10_years_and_older) AS rate_per_100000_age_10_plus
        FROM statewide_offenders
        GROUP BY year, year_ending
        ORDER BY year
        """
    )


def principal_offence_latest() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            offence_division,
            offence_subdivision,
            SUM(alleged_offender_incidents) AS alleged_offender_incidents
        FROM statewide_offenders
        WHERE year = (SELECT MAX(year) FROM statewide_offenders)
        GROUP BY year, offence_division, offence_subdivision
        ORDER BY alleged_offender_incidents DESC
        """
    )


def age_sex_distribution(year: int | None = None) -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            sex,
            age_group,
            is_youth,
            alleged_offender_incidents,
            rate_per_100_000_population_10_years_and_older AS rate_per_100000_age_10_plus
        FROM statewide_offenders_age_sex
        WHERE is_total_row = 0
          AND LOWER(sex) IN ('males', 'females')
          AND year = COALESCE(?, (SELECT MAX(year) FROM statewide_offenders_age_sex))
        ORDER BY sex, age_group
        """,
        (year,),
    )


def sex_distribution() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            sex,
            SUM(alleged_offender_incidents) AS alleged_offender_incidents
        FROM statewide_offenders_age_sex
        WHERE is_total_row = 0
          AND LOWER(sex) IN ('males', 'females')
        GROUP BY year, sex
        ORDER BY year, sex
        """
    )


def youth_vs_adult() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            CASE WHEN is_youth = 1 THEN 'Youth (10-17)' ELSE 'Adult (18+)' END AS age_band,
            SUM(alleged_offender_incidents) AS alleged_offender_incidents
        FROM statewide_offenders_age_sex
        WHERE is_total_row = 0
          AND LOWER(sex) IN ('males', 'females')
          AND LOWER(age_group) NOT LIKE '%unknown%'
        GROUP BY year, CASE WHEN is_youth = 1 THEN 'Youth (10-17)' ELSE 'Adult (18+)' END
        ORDER BY year, age_band
        """
    )


def youth_single_year_of_age(year: int | None = None) -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            sex,
            age_group,
            metric_value AS alleged_offender_incidents
        FROM statewide_youth_metrics
        WHERE category = 'Alleged Offender Incidents'
          AND LOWER(sex) IN ('males', 'females')
          AND CAST(age_group AS INTEGER) BETWEEN 10 AND 17
          AND year = COALESCE(?, (SELECT MAX(year) FROM statewide_youth_metrics))
        ORDER BY sex, CAST(age_group AS INTEGER)
        """,
        (year,),
    )


def offender_outcomes() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            outcome,
            SUM(alleged_offender_incidents) AS alleged_offender_incidents
        FROM statewide_offender_outcomes
        GROUP BY year, outcome
        ORDER BY year, alleged_offender_incidents DESC
        """
    )


def latest_lga_offenders() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            police_region,
            local_government_area,
            metro_regional,
            alleged_offender_incidents,
            rate_per_100_000_population AS rate_per_100000
        FROM lga_offender_totals
        WHERE is_region_total = 0
          AND year = (SELECT MAX(year) FROM lga_offender_totals)
        ORDER BY rate_per_100_000_population DESC
        """
    )


def sex_by_principal_offence(year: int | None = None) -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            year,
            sex,
            offence_division,
            SUM(alleged_offender_incidents) AS alleged_offender_incidents
        FROM statewide_offenders_sex_offence
        WHERE year = COALESCE(?, (SELECT MAX(year) FROM statewide_offenders_sex_offence))
          AND LOWER(sex) IN ('males', 'females')
        GROUP BY year, sex, offence_division
        ORDER BY offence_division, sex
        """,
        (year,),
    )


def offender_trend_with_yoy() -> pd.DataFrame:
    return add_yoy(statewide_offender_totals(), "alleged_offender_incidents")
