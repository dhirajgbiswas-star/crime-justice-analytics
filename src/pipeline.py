"""Run CSA ingestion, SQL analysis exports and Python visualisations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics.descriptive import (
    add_yoy,
    data_quality_snapshot,
    family_incident_share,
    investigation_status_trends,
    latest_lga_snapshot,
    lga_yoy_change,
    metro_regional_trends,
    offence_division_trends,
    offence_subdivision_change,
    statewide_annual_totals,
    top_subgroups,
)
from src.analytics.incidents import statistical_product_comparison, statewide_incident_totals
from src.analytics.national import abs_state_totals_latest, abs_victoria_vs_australia
from src.analytics.offender import (
    sex_distribution,
    statewide_offender_totals,
    youth_vs_adult,
)
from src.analytics.visualisation import generate_all_figures
from src.config import DATA_EXPORTS, SQLITE_PATH, ensure_output_dirs
from src.ingestion.load_csa import ingest_abs_only, ingest_all
from src.logging_utils import get_logger
from src.reporting.briefing import generate_briefing
from src.validation.quality_checks import generate_quality_reports


def export_analysis_tables() -> None:
    ensure_output_dirs()
    trend = add_yoy(statewide_annual_totals(), "offence_count")
    latest_year = int(trend["year"].max())
    start_year = int(trend["year"].min())

    outputs = {
        "statewide_annual_totals.csv": trend,
        "offence_division_trends.csv": offence_division_trends(),
        "offence_subdivision_long_term_change.csv": offence_subdivision_change(
            start_year, latest_year
        ),
        "lga_latest_snapshot.csv": latest_lga_snapshot(),
        "lga_yoy_change.csv": lga_yoy_change(),
        "metro_regional_trends.csv": metro_regional_trends(),
        "top_subgroups_latest.csv": top_subgroups(),
        "investigation_status_trends.csv": investigation_status_trends(),
        "family_incident_share.csv": family_incident_share(),
        "data_quality_snapshot.csv": data_quality_snapshot(),
        "statistical_product_comparison.csv": statistical_product_comparison(),
        "statewide_incident_totals.csv": statewide_incident_totals(),
        "statewide_offender_totals.csv": statewide_offender_totals(),
        "offender_sex_distribution.csv": sex_distribution(),
        "youth_vs_adult.csv": youth_vs_adult(),
        "abs_state_totals_latest.csv": abs_state_totals_latest(),
        "abs_victoria_vs_australia.csv": abs_victoria_vs_australia(),
    }
    for name, df in outputs.items():
        df.to_csv(DATA_EXPORTS / name, index=False)
        print(f"exported {name}: {len(df):,} rows")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Reuse the existing SQLite database.",
    )
    parser.add_argument(
        "--abs-only",
        action="store_true",
        help="Refresh ABS tables in the existing database without rebuilding CSA tables.",
    )
    args = parser.parse_args()
    logger = get_logger("pipeline")
    logger.info("pipeline start")

    if args.abs_only and SQLITE_PATH.exists():
        print("Refreshing ABS Recorded Crime – Offenders tables...")
        tables = ingest_abs_only()
        for name, df in tables.items():
            print(f"  {name}: {len(df):,} rows")
    elif not args.skip_ingest or not SQLITE_PATH.exists():
        print("Ingesting CSA and ABS Excel tables...")
        logger.info("ingestion start")
        tables = ingest_all()
        for name, df in tables.items():
            print(f"  {name}: {len(df):,} rows")
            logger.info("loaded %s rows=%s", name, len(df))
        print(f"SQLite written to {SQLITE_PATH}")
        logger.info("sqlite written %s", SQLITE_PATH)
    else:
        print(f"Using existing database {SQLITE_PATH}")
        logger.info("skip ingest")

    export_analysis_tables()
    generate_quality_reports()
    print("Generating figures...")
    for path in generate_all_figures():
        print(f"  {path.name}")
    print("Writing briefing report...")
    generate_briefing()
    print("Building public dashboards...")
    from src.dashboard.build import build_dashboards

    build_dashboards(include_tableau=True)
    from src.database.load_data import try_load_mysql

    try_load_mysql()
    logger.info("pipeline complete")


if __name__ == "__main__":
    main()
