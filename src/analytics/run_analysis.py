"""Standalone Python analysis script mirroring the notebooks.

Run from the project root:

    PYTHONPATH=. python src/analytics/run_analysis.py
"""

from __future__ import annotations

from src.analytics.descriptive import (
    add_yoy,
    data_quality_snapshot,
    family_incident_share,
    latest_lga_snapshot,
    lga_yoy_change,
    metro_regional_trends,
    offence_division_trends,
    offence_subdivision_change,
    statewide_annual_totals,
    top_subgroups,
)
from src.analytics.sql_analysis import run_sql_analysis
from src.analytics.visualisation import generate_all_figures


def print_section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    print_section("Statewide trend")
    trend = add_yoy(statewide_annual_totals(), "offence_count")
    print(trend.to_string(index=False))
    start_year, end_year = int(trend["year"].min()), int(trend["year"].max())
    start, end = trend.iloc[0]["offence_count"], trend.iloc[-1]["offence_count"]
    print(
        f"Long-term change {start_year}-{end_year}: "
        f"{end - start:,.0f} ({100 * (end - start) / start:.1f}%)"
    )

    print_section("Offence division change")
    div = offence_division_trends().pivot(
        index="year", columns="offence_division", values="offence_count"
    )
    print(((div.iloc[-1] - div.iloc[0]) / div.iloc[0] * 100).sort_values(ascending=False))

    print_section("Subdivision long-term change")
    chg = offence_subdivision_change(start_year, end_year).dropna(subset=["change_pct"])
    print("Increases")
    print(chg.head(8).to_string(index=False))
    print("Declines")
    print(chg.tail(8).to_string(index=False))

    print_section("LGA snapshot")
    lga = latest_lga_snapshot()
    print("Highest counts")
    print(lga.nlargest(10, "offence_count").to_string(index=False))
    print("Highest rates")
    print(lga.nlargest(10, "rate_per_100000").to_string(index=False))

    print_section("Largest LGA YoY increases")
    yoy = lga_yoy_change()
    latest = yoy[yoy["year"] == yoy["year"].max()]
    print(latest.nlargest(10, "yoy_pct").to_string(index=False))

    print_section("Metro vs regional")
    print(metro_regional_trends().to_string(index=False))

    print_section("Most common subgroups")
    print(top_subgroups().to_string(index=False))

    print_section("Family incident share")
    print(family_incident_share().to_string(index=False))

    print_section("Data quality")
    print(data_quality_snapshot().to_string(index=False))

    print_section("SQL analysis exports")
    run_sql_analysis()

    print_section("Visualisations")
    for path in generate_all_figures():
        print(path)


if __name__ == "__main__":
    main()
