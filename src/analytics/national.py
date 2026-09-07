"""ABS Recorded Crime – Offenders analysis.

Do not treat ABS unique offenders as comparable to CSA alleged offender incidents.
"""

from __future__ import annotations

import pandas as pd

from src.analytics.descriptive import add_yoy, read_sql
from src.config import ABS_STATISTICAL_PRODUCT


def abs_product_caveat() -> str:
    return ABS_STATISTICAL_PRODUCT


def abs_state_totals_latest() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            financial_year,
            year_end,
            jurisdiction,
            offender_count,
            rate_per_100000_age_10_plus
        FROM abs_offenders_states_totals
        WHERE offence_level = 'total'
          AND sex = 'Persons'
          AND age_group = 'All ages 10+'
        ORDER BY rate_per_100000_age_10_plus DESC
        """
    )


def abs_victoria_persons_trend() -> pd.DataFrame:
    return add_yoy(
        read_sql(
            """
            SELECT
                financial_year,
                year_end,
                jurisdiction,
                sex,
                offender_count,
                rate_per_100000_age_10_plus
            FROM abs_offenders_trend
            WHERE jurisdiction = 'Victoria'
              AND sex = 'Persons'
            ORDER BY year_end
            """
        ),
        "offender_count",
    )


def abs_australia_trend() -> pd.DataFrame:
    return add_yoy(
        read_sql(
            """
            SELECT
                financial_year,
                year_end,
                jurisdiction,
                offender_count,
                rate_per_100000_age_10_plus
            FROM abs_offenders_trend
            WHERE jurisdiction = 'Australia'
              AND sex = 'Persons'
            ORDER BY year_end
            """
        ),
        "offender_count",
    )


def abs_victoria_sex_latest() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            financial_year,
            sex,
            offender_count,
            rate_per_100000_age_10_plus
        FROM abs_offenders_trend
        WHERE jurisdiction = 'Victoria'
          AND year_end = (SELECT MAX(year_end) FROM abs_offenders_trend WHERE jurisdiction = 'Victoria')
        ORDER BY sex
        """
    )


def abs_youth_by_state_latest() -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            financial_year,
            year_end,
            jurisdiction,
            offender_count AS youth_offenders,
            rate_per_100000_age_10_plus AS youth_rate_per_100000
        FROM abs_youth_offenders
        WHERE year_end = (SELECT MAX(year_end) FROM abs_youth_offenders)
        ORDER BY youth_offenders DESC
        """
    )


def abs_victoria_youth_trend() -> pd.DataFrame:
    return add_yoy(
        read_sql(
            """
            SELECT
                financial_year,
                year_end,
                jurisdiction,
                offender_count,
                rate_per_100000_age_10_plus
            FROM abs_youth_offenders
            WHERE jurisdiction = 'Victoria'
            ORDER BY year_end
            """
        ),
        "offender_count",
    )


def abs_principal_offence_latest(jurisdiction: str = "Victoria") -> pd.DataFrame:
    return read_sql(
        """
        SELECT
            financial_year,
            jurisdiction,
            principal_offence,
            offence_level,
            offender_count,
            rate_per_100000_age_10_plus
        FROM abs_offenders
        WHERE financial_year = '2024–25'
          AND jurisdiction = ?
          AND sex = 'Persons'
          AND age_group = 'All ages 10+'
          AND offence_level IN ('division', 'total')
        ORDER BY CASE WHEN offence_level = 'total' THEN 1 ELSE 0 END, offender_count DESC
        """,
        (jurisdiction,),
    )


def abs_victoria_vs_australia() -> pd.DataFrame:
    """Compare ABS Victoria with ABS Australia on the ABS measure only."""
    states = abs_state_totals_latest()
    victoria = states.loc[states["jurisdiction"].eq("Victoria")].iloc[0]
    australia = states.loc[states["jurisdiction"].eq("Australia")].iloc[0]
    vic_trend = abs_victoria_persons_trend()
    previous = vic_trend.loc[vic_trend["year_end"].eq(int(victoria["year_end"]) - 1)]
    previous_count = float(previous["offender_count"].iloc[0]) if not previous.empty else None
    youth = abs_victoria_youth_trend()
    youth_latest = youth.loc[youth["year_end"].eq(int(victoria["year_end"]))].iloc[0]
    vic_count = float(victoria["offender_count"])
    aus_count = float(australia["offender_count"])
    return pd.DataFrame(
        [
            {
                "financial_year": victoria["financial_year"],
                "victoria_offenders": vic_count,
                "victoria_rate": float(victoria["rate_per_100000_age_10_plus"]),
                "australia_offenders": aus_count,
                "australia_rate": float(australia["rate_per_100000_age_10_plus"]),
                "victoria_share_of_australia_pct": round(100.0 * vic_count / aus_count, 1),
                "victoria_rate_vs_australia_pct": round(
                    100.0
                    * float(victoria["rate_per_100000_age_10_plus"])
                    / float(australia["rate_per_100000_age_10_plus"]),
                    1,
                ),
                "victoria_yoy_count_pct": None
                if previous_count is None
                else round(100.0 * (vic_count - previous_count) / previous_count, 1),
                "victoria_youth_offenders": float(youth_latest["offender_count"]),
                "victoria_youth_share_pct": round(
                    100.0 * float(youth_latest["offender_count"]) / vic_count, 1
                ),
                "caveat": ABS_STATISTICAL_PRODUCT,
            }
        ]
    )


def csa_vs_abs_product_note() -> pd.DataFrame:
    """Place CSA incidents and ABS offenders side by side with an explicit non-join."""
    csa = read_sql(
        """
        SELECT
            year,
            SUM(alleged_offender_incidents) AS alleged_offender_incidents
        FROM statewide_offenders
        WHERE year = (SELECT MAX(year) FROM statewide_offenders)
        GROUP BY year
        """
    )
    abs_vic = abs_victoria_persons_trend()
    latest_abs = abs_vic.loc[abs_vic["year_end"].eq(abs_vic["year_end"].max())].iloc[0]
    return pd.DataFrame(
        [
            {
                "csa_product": "Alleged offender incidents",
                "csa_period": f"Year ending March {int(csa['year'].iloc[0])}",
                "csa_measure": int(csa["alleged_offender_incidents"].iloc[0]),
                "abs_product": "Unique alleged offenders proceeded against",
                "abs_period": f"Financial year {latest_abs['financial_year']}",
                "abs_measure": int(latest_abs["offender_count"]),
                "comparable": 0,
                "reason": ABS_STATISTICAL_PRODUCT,
            }
        ]
    )
