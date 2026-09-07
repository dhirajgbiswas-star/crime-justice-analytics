"""Automated data-quality scoring for loaded CSA tables."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from src.analytics.descriptive import read_sql
from src.config import DATA_EXPORTS, REPORTS_DIR, ensure_output_dirs


def _score(value: float) -> float:
    return max(0.0, min(100.0, value))


def table_quality_frame() -> pd.DataFrame:
    return read_sql(
        """
        SELECT 'lga_offence_totals' AS table_name, COUNT(*) AS row_count,
            SUM(CASE WHEN offence_count IS NULL THEN 1 ELSE 0 END) AS missing_count,
            SUM(CASE WHEN offence_count < 0 THEN 1 ELSE 0 END) AS negative_count,
            SUM(CASE WHEN rate_per_100_000_population < 0 THEN 1 ELSE 0 END) AS negative_rate,
            COUNT(*) - COUNT(DISTINCT year || '|' || police_region || '|' || local_government_area) AS duplicate_keys,
            MIN(year) AS min_year, MAX(year) AS max_year
        FROM lga_offence_totals
        UNION ALL
        SELECT 'statewide_offences', COUNT(*),
            SUM(CASE WHEN offence_count IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN offence_count < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rate_per_100_000_population < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year || '|' || offence_subgroup),
            MIN(year), MAX(year)
        FROM statewide_offences
        UNION ALL
        SELECT 'statewide_incidents', COUNT(*),
            SUM(CASE WHEN incidents_recorded IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN incidents_recorded < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rate_per_100_000_population < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year || '|' || offence_subgroup),
            MIN(year), MAX(year)
        FROM statewide_incidents
        UNION ALL
        SELECT 'lga_incident_totals', COUNT(*),
            SUM(CASE WHEN incidents_recorded IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN incidents_recorded < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rate_per_100_000_population < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year || '|' || police_region || '|' || local_government_area),
            MIN(year), MAX(year)
        FROM lga_incident_totals
        UNION ALL
        SELECT 'statewide_offenders', COUNT(*),
            SUM(CASE WHEN alleged_offender_incidents IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN alleged_offender_incidents < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rate_per_100_000_population_10_years_and_older < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year || '|' || offence_subdivision || '|' || COALESCE(offence_group,'')),
            MIN(year), MAX(year)
        FROM statewide_offenders
        UNION ALL
        SELECT 'statewide_offenders_age_sex', COUNT(*),
            SUM(CASE WHEN alleged_offender_incidents IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN alleged_offender_incidents < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rate_per_100_000_population_10_years_and_older < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year || '|' || sex || '|' || age_group),
            MIN(year), MAX(year)
        FROM statewide_offenders_age_sex
        UNION ALL
        SELECT 'lga_offender_totals', COUNT(*),
            SUM(CASE WHEN alleged_offender_incidents IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN alleged_offender_incidents < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rate_per_100_000_population < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year || '|' || police_region || '|' || local_government_area),
            MIN(year), MAX(year)
        FROM lga_offender_totals
        UNION ALL
        SELECT 'abs_offenders_trend', COUNT(*),
            SUM(CASE WHEN offender_count IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN offender_count < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rate_per_100000_age_10_plus < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year_end || '|' || jurisdiction || '|' || sex),
            MIN(year_end), MAX(year_end)
        FROM abs_offenders_trend
        UNION ALL
        SELECT 'abs_youth_offenders', COUNT(*),
            SUM(CASE WHEN offender_count IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN offender_count < 0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN rate_per_100000_age_10_plus < 0 THEN 1 ELSE 0 END),
            COUNT(*) - COUNT(DISTINCT year_end || '|' || jurisdiction),
            MIN(year_end), MAX(year_end)
        FROM abs_youth_offenders
        """
    )


def score_quality(df: pd.DataFrame) -> dict[str, float]:
    total_rows = float(df["row_count"].sum()) or 1.0
    missing = float(df["missing_count"].sum())
    negatives = float(df["negative_count"].sum() + df["negative_rate"].sum())
    duplicates = float(df["duplicate_keys"].sum())
    expected_max_year = 2026
    latest = int(df["max_year"].max())
    completeness = _score(100.0 * (1 - missing / total_rows))
    validity = _score(100.0 * (1 - negatives / total_rows))
    uniqueness = _score(100.0 * (1 - duplicates / total_rows))
    year_span = (df["max_year"] - df["min_year"] + 1).fillna(0)
    consistency = _score(100.0 if (year_span >= 8).all() else 90.0)
    timeliness = _score(100.0 if latest >= expected_max_year else 80.0)
    overall = round(
        0.25 * completeness
        + 0.25 * validity
        + 0.20 * uniqueness
        + 0.15 * consistency
        + 0.15 * timeliness,
        1,
    )
    return {
        "completeness": round(completeness, 1),
        "validity": round(validity, 1),
        "uniqueness": round(uniqueness, 1),
        "consistency": round(consistency, 1),
        "timeliness": round(timeliness, 1),
        "overall": overall,
    }


def generate_quality_reports() -> dict[str, float]:
    ensure_output_dirs()
    detail = table_quality_frame()
    scores = score_quality(detail)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    csv_path = DATA_EXPORTS / "data_quality_report.csv"
    detail.assign(**{f"score_{k}": v for k, v in scores.items()}).to_csv(csv_path, index=False)

    rows_html = "\n".join(
        f"<tr><td>{r.table_name}</td><td>{int(r.row_count):,}</td>"
        f"<td>{int(r.missing_count)}</td><td>{int(r.negative_count)}</td>"
        f"<td>{int(r.duplicate_keys)}</td><td>{int(r.min_year)}-{int(r.max_year)}</td></tr>"
        for r in detail.itertuples()
    )
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>CSA data quality report</title>
<style>
body {{ font-family: Georgia, serif; margin: 32px; color: #1B365D; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #D6D9DE; padding: 8px 10px; text-align: left; }}
.score {{ font-size: 28px; font-weight: 700; }}
</style></head><body>
<h1>Victorian crime statistics data-quality report</h1>
<p>Generated {generated}. Sources: Crime Statistics Agency recorded offences, criminal incidents and alleged offender incidents, year ending March 2026; ABS Recorded Crime – Offenders, 2024–25.</p>
<p class="score">Overall data quality score: {scores['overall']}%</p>
<ul>
<li>Completeness {scores['completeness']}%</li>
<li>Validity {scores['validity']}%</li>
<li>Uniqueness {scores['uniqueness']}%</li>
<li>Consistency {scores['consistency']}%</li>
<li>Timeliness {scores['timeliness']}%</li>
</ul>
<table>
<thead><tr><th>Table</th><th>Rows</th><th>Missing counts</th><th>Negatives</th><th>Duplicate keys</th><th>Years</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
<p>Scores measure the loaded statistical tables, not underlying police recording practice. Duplicate-key checks use the natural business key for each table.</p>
</body></html>
"""
    html_path = REPORTS_DIR / "data_quality_report.html"
    html_path.write_text(html)
    print(f"Overall Data Quality Score: {scores['overall']}%")
    print(f"wrote {csv_path}")
    print(f"wrote {html_path}")
    return scores


if __name__ == "__main__":
    generate_quality_reports()
