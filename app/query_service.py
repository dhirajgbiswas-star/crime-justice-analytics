"""Query helpers for the data-request service."""

from src.analytics.descriptive import read_sql


def available_lgas() -> list[str]:
    df = read_sql(
        """
        SELECT DISTINCT local_government_area
        FROM lga_offence_totals
        WHERE is_region_total = 0
        ORDER BY 1
        """
    )
    return df["local_government_area"].tolist()
