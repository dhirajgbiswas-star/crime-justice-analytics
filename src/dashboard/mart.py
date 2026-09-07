"""Tableau-ready extracts for the Victorian crime intelligence dashboards.

One long-form mart powers the generated Tableau workbook. Separate tidy
sheets are also written so a Tableau Desktop user can rebuild or extend
the dashboards without blending statistical products into one measure.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.analytics.descriptive import (
    add_yoy,
    family_incident_share,
    investigation_status_trends,
    lga_yoy_change,
    metro_regional_trends,
    offence_division_trends,
    offence_subdivision_change,
    read_sql,
    statewide_annual_totals,
    top_subgroups,
)
from src.analytics.incidents import (
    charge_status_share,
    statistical_product_comparison,
    statewide_incident_totals,
)
from src.analytics.national import (
    abs_australia_trend,
    abs_principal_offence_latest,
    abs_product_caveat,
    abs_state_totals_latest,
    abs_victoria_persons_trend,
    abs_victoria_sex_latest,
    abs_victoria_vs_australia,
    abs_victoria_youth_trend,
    abs_youth_by_state_latest,
    csa_vs_abs_product_note,
)
from src.analytics.offender import (
    age_sex_distribution,
    latest_lga_offenders,
    principal_offence_latest,
    sex_distribution,
    statewide_offender_totals,
    youth_single_year_of_age,
    youth_vs_adult,
)
from src.config import DATA_EXPORTS, DASHBOARD_DIR, DIVISION_COLOURS, PALETTE, ensure_output_dirs
from src.validation.quality_checks import generate_quality_reports, score_quality, table_quality_frame

# Approximate LGA centroids for a Victoria-focused symbol map.
# Justice institutions and unincorporated areas are omitted from the map.
LGA_CENTROIDS: dict[str, tuple[float, float]] = {
    "Alpine": (-36.85, 146.90),
    "Ararat": (-37.28, 142.93),
    "Ballarat": (-37.56, 143.85),
    "Banyule": (-37.73, 145.08),
    "Bass Coast": (-38.50, 145.55),
    "Baw Baw": (-37.95, 146.15),
    "Bayside": (-37.94, 145.02),
    "Benalla": (-36.55, 145.98),
    "Boroondara": (-37.82, 145.06),
    "Brimbank": (-37.76, 144.80),
    "Buloke": (-35.95, 143.10),
    "Campaspe": (-36.35, 144.75),
    "Cardinia": (-38.05, 145.50),
    "Casey": (-38.10, 145.30),
    "Central Goldfields": (-37.05, 143.75),
    "Colac-Otway": (-38.40, 143.58),
    "Corangamite": (-38.25, 143.15),
    "Darebin": (-37.75, 145.03),
    "East Gippsland": (-37.50, 148.20),
    "Frankston": (-38.15, 145.14),
    "Gannawarra": (-35.70, 143.90),
    "Glen Eira": (-37.90, 145.05),
    "Glenelg": (-37.85, 141.40),
    "Golden Plains": (-37.85, 143.90),
    "Greater Bendigo": (-36.76, 144.28),
    "Greater Dandenong": (-38.00, 145.20),
    "Greater Geelong": (-38.15, 144.36),
    "Greater Shepparton": (-36.38, 145.40),
    "Hepburn": (-37.35, 144.15),
    "Hindmarsh": (-36.30, 141.70),
    "Hobsons Bay": (-37.86, 144.83),
    "Horsham": (-36.72, 142.20),
    "Hume": (-37.60, 144.85),
    "Indigo": (-36.20, 146.70),
    "Kingston": (-38.00, 145.10),
    "Knox": (-37.88, 145.25),
    "Latrobe": (-38.20, 146.45),
    "Loddon": (-36.40, 143.80),
    "Macedon Ranges": (-37.35, 144.60),
    "Manningham": (-37.76, 145.17),
    "Mansfield": (-37.05, 146.09),
    "Maribyrnong": (-37.80, 144.89),
    "Maroondah": (-37.81, 145.26),
    "Melbourne": (-37.8136, 144.9631),
    "Melton": (-37.68, 144.58),
    "Merri-bek": (-37.74, 144.96),
    "Mildura": (-34.19, 142.16),
    "Mitchell": (-37.20, 145.05),
    "Moira": (-36.05, 145.55),
    "Monash": (-37.90, 145.13),
    "Moonee Valley": (-37.75, 144.91),
    "Moorabool": (-37.65, 144.25),
    "Mornington Peninsula": (-38.35, 145.05),
    "Mount Alexander": (-37.07, 144.22),
    "Moyne": (-38.25, 142.40),
    "Murrindindi": (-37.30, 145.70),
    "Nillumbik": (-37.60, 145.20),
    "Northern Grampians": (-36.90, 142.85),
    "Port Phillip": (-37.85, 144.98),
    "Pyrenees": (-37.25, 143.35),
    "Queenscliffe": (-38.27, 144.66),
    "South Gippsland": (-38.50, 146.10),
    "Southern Grampians": (-37.60, 142.00),
    "Stonnington": (-37.86, 145.04),
    "Strathbogie": (-36.75, 145.45),
    "Surf Coast": (-38.33, 144.10),
    "Swan Hill": (-35.34, 143.55),
    "Towong": (-36.30, 147.50),
    "Wangaratta": (-36.36, 146.32),
    "Warrnambool": (-38.38, 142.48),
    "Wellington": (-38.00, 146.90),
    "West Wimmera": (-36.55, 141.35),
    "Whitehorse": (-37.83, 145.15),
    "Whittlesea": (-37.55, 145.10),
    "Wodonga": (-36.12, 146.88),
    "Wyndham": (-37.90, 144.66),
    "Yarra": (-37.80, 145.00),
    "Yarra Ranges": (-37.75, 145.55),
    "Yarriambiack": (-36.30, 142.40),
}

MAP_EXCLUSIONS = {
    "Justice Institutions and Immigration Facilities",
    "Unincorporated Vic",
}


def _lga_query(table: str, count_col: str, alias: str) -> pd.DataFrame:
    return read_sql(
        f"""
        SELECT
            year,
            police_region,
            local_government_area,
            metro_regional,
            {count_col} AS {alias},
            rate_per_100_000_population AS {alias}_rate
        FROM {table}
        WHERE is_region_total = 0
        ORDER BY year, local_government_area
        """
    )


def _attach_geo(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Country"] = "Australia"
    out["State"] = "Victoria"
    out["Latitude"] = out["local_government_area"].map(lambda x: LGA_CENTROIDS.get(x, (None, None))[0])
    out["Longitude"] = out["local_government_area"].map(lambda x: LGA_CENTROIDS.get(x, (None, None))[1])
    return out


def lga_profile() -> pd.DataFrame:
    offences = _lga_query("lga_offence_totals", "offence_count", "recorded_offences")
    incidents = _lga_query("lga_incident_totals", "incidents_recorded", "criminal_incidents")
    offenders = _lga_query("lga_offender_totals", "alleged_offender_incidents", "alleged_offender_incidents")
    profile = offences.merge(
        incidents,
        on=["year", "police_region", "local_government_area", "metro_regional"],
        how="outer",
    ).merge(
        offenders,
        on=["year", "police_region", "local_government_area", "metro_regional"],
        how="outer",
    )
    return _attach_geo(profile)


def _blank_mart() -> dict[str, list]:
    columns = [
        "Dataset",
        "Year",
        "Statistical Product",
        "Country",
        "State",
        "Local Government Area",
        "Police Region",
        "Metro Regional",
        "Offence Division",
        "Offence Subdivision",
        "Offence Subgroup",
        "Sex",
        "Age Group",
        "Charge Status",
        "Investigation Status",
        "Family Incident Flag",
        "Age Band",
        "Table Name",
        "Jurisdiction",
        "Financial Year",
        "Latitude",
        "Longitude",
        "Count",
        "Rate per 100000",
        "Share %",
        "YoY %",
        "YoY Count",
        "Quality Score",
    ]
    return {col: [] for col in columns}


def _append(mart: dict[str, list], **values) -> None:
    for key in mart:
        mart[key].append(values.get(key))


def build_tableau_mart() -> pd.DataFrame:
    mart = _blank_mart()

    offences = add_yoy(statewide_annual_totals(), "offence_count")
    incidents = add_yoy(statewide_incident_totals(), "incident_count")
    offenders = add_yoy(statewide_offender_totals(), "alleged_offender_incidents")

    for _, row in offences.iterrows():
        _append(
            mart,
            Dataset="Statewide products",
            Year=int(row["year"]),
            **{"Statistical Product": "Recorded offences"},
            Count=float(row["offence_count"]),
            **{"Rate per 100000": float(row["rate_per_100000"])},
            **{"YoY %": None if pd.isna(row["offence_count_yoy_pct"]) else float(row["offence_count_yoy_pct"])},
            **{"YoY Count": None if pd.isna(row["offence_count_yoy"]) else float(row["offence_count_yoy"])},
        )
    for _, row in incidents.iterrows():
        _append(
            mart,
            Dataset="Statewide products",
            Year=int(row["year"]),
            **{"Statistical Product": "Criminal incidents"},
            Count=float(row["incident_count"]),
            **{"Rate per 100000": float(row["rate_per_100000"])},
            **{"YoY %": None if pd.isna(row["incident_count_yoy_pct"]) else float(row["incident_count_yoy_pct"])},
            **{"YoY Count": None if pd.isna(row["incident_count_yoy"]) else float(row["incident_count_yoy"])},
        )
    for _, row in offenders.iterrows():
        _append(
            mart,
            Dataset="Statewide products",
            Year=int(row["year"]),
            **{"Statistical Product": "Alleged offender incidents"},
            Count=float(row["alleged_offender_incidents"]),
            **{"Rate per 100000": float(row["rate_per_100000_age_10_plus"])},
            **{"YoY %": None if pd.isna(row["alleged_offender_incidents_yoy_pct"]) else float(row["alleged_offender_incidents_yoy_pct"])},
            **{"YoY Count": None if pd.isna(row["alleged_offender_incidents_yoy"]) else float(row["alleged_offender_incidents_yoy"])},
        )

    for _, row in offence_division_trends().iterrows():
        _append(
            mart,
            Dataset="Recorded offence divisions",
            Year=int(row["year"]),
            **{"Statistical Product": "Recorded offences"},
            **{"Offence Division": row["offence_division"]},
            Count=float(row["offence_count"]),
            **{"Rate per 100000": float(row["rate_per_100000"])},
        )

    latest_year = int(offences["year"].max())
    start_year = int(offences["year"].min())
    for _, row in offence_subdivision_change(start_year, latest_year).iterrows():
        _append(
            mart,
            Dataset="Offence subdivision change",
            Year=latest_year,
            **{"Statistical Product": "Recorded offences"},
            **{"Offence Division": row["offence_division"]},
            **{"Offence Subdivision": row["offence_subdivision"]},
            Count=float(row["end_count"]),
            **{"YoY Count": float(row["change_count"])},
            **{"YoY %": None if pd.isna(row["change_pct"]) else float(row["change_pct"])},
        )

    profile = lga_profile()
    for _, row in profile.iterrows():
        year = int(row["year"])
        lga = row["local_government_area"]
        geo = {
            "Country": "Australia",
            "State": "Victoria",
            "Local Government Area": lga,
            "Police Region": row["police_region"],
            "Metro Regional": row["metro_regional"],
            "Latitude": None if pd.isna(row["Latitude"]) else float(row["Latitude"]),
            "Longitude": None if pd.isna(row["Longitude"]) else float(row["Longitude"]),
        }
        if pd.notna(row.get("recorded_offences")):
            _append(
                mart,
                Dataset="LGA recorded offences",
                Year=year,
                **{"Statistical Product": "Recorded offences"},
                Count=float(row["recorded_offences"]),
                **{"Rate per 100000": float(row["recorded_offences_rate"])},
                **geo,
            )
        if pd.notna(row.get("criminal_incidents")):
            _append(
                mart,
                Dataset="LGA criminal incidents",
                Year=year,
                **{"Statistical Product": "Criminal incidents"},
                Count=float(row["criminal_incidents"]),
                **{"Rate per 100000": float(row["criminal_incidents_rate"])},
                **geo,
            )
        if pd.notna(row.get("alleged_offender_incidents")):
            _append(
                mart,
                Dataset="LGA alleged offender incidents",
                Year=year,
                **{"Statistical Product": "Alleged offender incidents"},
                Count=float(row["alleged_offender_incidents"]),
                **{"Rate per 100000": float(row["alleged_offender_incidents_rate"])},
                **geo,
            )

    for _, row in metro_regional_trends().iterrows():
        _append(
            mart,
            Dataset="Metro regional recorded offences",
            Year=int(row["year"]),
            **{"Statistical Product": "Recorded offences"},
            **{"Metro Regional": row["metro_regional"]},
            Count=float(row["offence_count"]),
            **{"Rate per 100000": float(row["avg_lga_rate_per_100000"])},
        )

    yoy = lga_yoy_change()
    yoy_latest = yoy[yoy["year"] == yoy["year"].max()]
    for _, row in yoy_latest.iterrows():
        _append(
            mart,
            Dataset="LGA YoY recorded offences",
            Year=int(row["year"]),
            **{"Statistical Product": "Recorded offences"},
            **{"Local Government Area": row["local_government_area"]},
            **{"Police Region": row["police_region"]},
            **{"Metro Regional": row["metro_regional"]},
            Count=float(row["offence_count"]),
            **{"Rate per 100000": float(row["rate_per_100000"])},
            **{"YoY %": None if pd.isna(row["yoy_pct"]) else float(row["yoy_pct"])},
            **{"YoY Count": None if pd.isna(row["yoy_count"]) else float(row["yoy_count"])},
        )

    for _, row in top_subgroups().iterrows():
        _append(
            mart,
            Dataset="Recorded offence subgroups",
            Year=int(row["year"]),
            **{"Statistical Product": "Recorded offences"},
            **{"Offence Subgroup": row["offence_subgroup"]},
            Count=float(row["offence_count"]),
        )

    for _, row in investigation_status_trends().iterrows():
        _append(
            mart,
            Dataset="Investigation status",
            Year=int(row["year"]),
            **{"Statistical Product": "Recorded offences"},
            **{"Investigation Status": row["investigation_status"]},
            Count=float(row["offence_count"]),
        )

    family = family_incident_share()
    family_totals = family.groupby("year")["offence_count"].transform("sum")
    family = family.copy()
    family["share_pct"] = 100.0 * family["offence_count"] / family_totals
    for _, row in family.iterrows():
        _append(
            mart,
            Dataset="Family incident offences",
            Year=int(row["year"]),
            **{"Statistical Product": "Recorded offences"},
            **{"Family Incident Flag": row["family_incident_flag"]},
            Count=float(row["offence_count"]),
            **{"Rate per 100000": float(row["rate_per_100000"])},
            **{"Share %": float(row["share_pct"])},
        )

    for _, row in charge_status_share().iterrows():
        _append(
            mart,
            Dataset="Charge status",
            Year=int(row["year"]),
            **{"Statistical Product": "Criminal incidents"},
            **{"Charge Status": row["charge_status"]},
            Count=float(row["incident_count"]),
            **{"Share %": float(row["share_pct"])},
        )

    age = read_sql(
        """
        SELECT year, sex, age_group, is_youth, alleged_offender_incidents
        FROM statewide_offenders_age_sex
        WHERE is_total_row = 0
          AND LOWER(sex) IN ('males', 'females')
        ORDER BY year, sex, age_group
        """
    )
    for _, row in age.iterrows():
        _append(
            mart,
            Dataset="Alleged offender age-sex",
            Year=int(row["year"]),
            **{"Statistical Product": "Alleged offender incidents"},
            Sex=row["sex"],
            **{"Age Group": row["age_group"]},
            **{"Age Band": "Youth (10-17)" if int(row["is_youth"]) == 1 else "Adult (18+)"},
            Count=float(row["alleged_offender_incidents"]),
        )

    for _, row in youth_vs_adult().iterrows():
        _append(
            mart,
            Dataset="Youth vs adult",
            Year=int(row["year"]),
            **{"Statistical Product": "Alleged offender incidents"},
            **{"Age Band": row["age_band"]},
            Count=float(row["alleged_offender_incidents"]),
        )

    youth_age = read_sql(
        """
        SELECT year, sex, age_group, metric_value AS alleged_offender_incidents
        FROM statewide_youth_metrics
        WHERE category = 'Alleged Offender Incidents'
          AND LOWER(sex) IN ('males', 'females')
          AND CAST(age_group AS INTEGER) BETWEEN 10 AND 17
        ORDER BY year, sex, CAST(age_group AS INTEGER)
        """
    )
    for _, row in youth_age.iterrows():
        _append(
            mart,
            Dataset="Youth single year of age",
            Year=int(row["year"]),
            **{"Statistical Product": "Alleged offender incidents"},
            Sex=row["sex"],
            **{"Age Group": str(row["age_group"])},
            Count=float(row["alleged_offender_incidents"]),
        )

    principal = read_sql(
        """
        SELECT year, offence_division, offence_subdivision,
               SUM(alleged_offender_incidents) AS alleged_offender_incidents
        FROM statewide_offenders
        GROUP BY year, offence_division, offence_subdivision
        ORDER BY year, alleged_offender_incidents DESC
        """
    )
    for _, row in principal.iterrows():
        _append(
            mart,
            Dataset="Principal alleged offender offence",
            Year=int(row["year"]),
            **{"Statistical Product": "Alleged offender incidents"},
            **{"Offence Division": row["offence_division"]},
            **{"Offence Subdivision": row["offence_subdivision"]},
            Count=float(row["alleged_offender_incidents"]),
        )

    quality, _scores = _quality_table()
    for _, row in quality.iterrows():
        _append(
            mart,
            Dataset="Data quality",
            Year=latest_year,
            **{"Table Name": row["table_name"]},
            Count=float(row["row_count"]),
            **{"Quality Score": float(row["score_overall"])},
        )

    _append_abs_mart(mart)
    return pd.DataFrame(mart)


def _append_abs_mart(mart: dict[str, list]) -> None:
    """Add ABS unique-offender rows. Never write these into CSA product datasets."""
    try:
        states = abs_state_totals_latest()
        vic_trend = abs_victoria_persons_trend()
        aus_trend = abs_australia_trend()
        sex = abs_victoria_sex_latest()
        youth_states = abs_youth_by_state_latest()
        youth_trend = abs_victoria_youth_trend()
        offences = abs_principal_offence_latest("Victoria")
        note = csa_vs_abs_product_note().iloc[0]
    except Exception:
        return

    product = "ABS unique offenders"
    for _, row in states.iterrows():
        _append(
            mart,
            Dataset="ABS state totals",
            Year=int(row["year_end"]),
            **{"Statistical Product": product},
            Jurisdiction=row["jurisdiction"],
            **{"Financial Year": row["financial_year"]},
            **{"Age Band": "All ages 10+"},
            Count=float(row["offender_count"]),
            **{"Rate per 100000": float(row["rate_per_100000_age_10_plus"])},
        )
    for frame, jurisdiction in ((vic_trend, "Victoria"), (aus_trend, "Australia")):
        for _, row in frame.iterrows():
            _append(
                mart,
                Dataset="ABS Victoria Australia trend",
                Year=int(row["year_end"]),
                **{"Statistical Product": product},
                Jurisdiction=jurisdiction,
                **{"Financial Year": row["financial_year"]},
                **{"Age Band": "All ages 10+"},
                Count=float(row["offender_count"]),
                **{"Rate per 100000": float(row["rate_per_100000_age_10_plus"])},
                **{"YoY %": None if pd.isna(row.get("offender_count_yoy_pct")) else float(row["offender_count_yoy_pct"])},
            )
    for _, row in sex.iterrows():
        _append(
            mart,
            Dataset="ABS Victoria sex",
            Year=int(states["year_end"].iloc[0]),
            **{"Statistical Product": product},
            Jurisdiction="Victoria",
            **{"Financial Year": row["financial_year"]},
            Sex=row["sex"],
            **{"Age Band": "All ages 10+"},
            Count=float(row["offender_count"]),
            **{"Rate per 100000": float(row["rate_per_100000_age_10_plus"])},
        )
    for _, row in youth_states.iterrows():
        _append(
            mart,
            Dataset="ABS youth by state",
            Year=int(row["year_end"]),
            **{"Statistical Product": product},
            Jurisdiction=row["jurisdiction"],
            **{"Financial Year": row["financial_year"]},
            **{"Age Band": "Youth (10-17)"},
            Count=float(row["youth_offenders"]),
            **{"Rate per 100000": float(row["youth_rate_per_100000"])},
        )
    for _, row in youth_trend.iterrows():
        _append(
            mart,
            Dataset="ABS Victoria youth trend",
            Year=int(row["year_end"]),
            **{"Statistical Product": product},
            Jurisdiction="Victoria",
            **{"Financial Year": row["financial_year"]},
            **{"Age Band": "Youth (10-17)"},
            Count=float(row["offender_count"]),
            **{"Rate per 100000": float(row["rate_per_100000_age_10_plus"])},
            **{"YoY %": None if pd.isna(row.get("offender_count_yoy_pct")) else float(row["offender_count_yoy_pct"])},
        )
    for _, row in offences.iterrows():
        if row["offence_level"] != "division":
            continue
        _append(
            mart,
            Dataset="ABS Victoria principal offence",
            Year=int(states["year_end"].iloc[0]),
            **{"Statistical Product": product},
            Jurisdiction="Victoria",
            **{"Financial Year": row["financial_year"]},
            **{"Offence Division": row["principal_offence"]},
            **{"Age Band": "All ages 10+"},
            Count=float(row["offender_count"]),
            **{"Rate per 100000": float(row["rate_per_100000_age_10_plus"])},
        )
    _append(
        mart,
        Dataset="ABS vs CSA note",
        Year=2026,
        **{"Statistical Product": "Alleged offender incidents"},
        Jurisdiction="Victoria",
        **{"Table Name": note["csa_product"]},
        **{"Financial Year": note["csa_period"]},
        Count=float(note["csa_measure"]),
        **{"Share %": 0},
    )
    _append(
        mart,
        Dataset="ABS vs CSA note",
        Year=2025,
        **{"Statistical Product": product},
        Jurisdiction="Victoria",
        **{"Table Name": note["abs_product"]},
        **{"Financial Year": note["abs_period"]},
        Count=float(note["abs_measure"]),
        **{"Share %": 0},
    )


def dashboard_payload() -> dict:
    offences = add_yoy(statewide_annual_totals(), "offence_count")
    incidents = add_yoy(statewide_incident_totals(), "incident_count")
    offenders = add_yoy(statewide_offender_totals(), "alleged_offender_incidents")
    products = statistical_product_comparison()
    latest = int(offences["year"].max())
    profile = lga_profile()
    profile_map = profile[
        ~profile["local_government_area"].isin(MAP_EXCLUSIONS)
        & profile["Latitude"].notna()
    ].copy()
    quality, scores = _quality_table()
    yoy = lga_yoy_change()
    heatmap_all = read_sql(
        """
        SELECT year, local_government_area, offence_division, SUM(offence_count) AS offence_count
        FROM lga_offences
        GROUP BY year, local_government_area, offence_division
        """
    )
    offender_lgas = read_sql(
        """
        SELECT year, police_region, local_government_area, metro_regional,
               alleged_offender_incidents,
               rate_per_100_000_population AS rate_per_100000
        FROM lga_offender_totals
        WHERE is_region_total = 0
        """
    )

    return {
        "meta": {
            "title": "Victorian Crime & Justice Intelligence",
            "subtitle": "Official CSA and ABS open data · CSA year ending March 2017–2026 · ABS financial years 2008–09 to 2024–25",
            "publisher": "Crime Statistics Agency (Victoria) and Australian Bureau of Statistics",
            "licence": "Creative Commons Attribution 4.0 International",
            "publicationDate": "19 June 2026",
            "absPublicationDate": "18 March 2026",
            "latestYear": latest,
            "attribution": "Source: Crime Statistics Agency (Victoria) and Australian Bureau of Statistics. CC BY 4.0.",
            "absCaveat": abs_product_caveat(),
            "notes": [
                "Recorded offences, criminal incidents and alleged offender incidents are different statistical products and are not interchangeable.",
                "Alleged offender incidents are not unique people and are not findings of guilt.",
                "Metropolitan / regional is an analytical grouping (police region contains Metro, plus selected Eastern LGAs), not official CSA geography.",
                "ABS Recorded Crime – Offenders counts unique alleged offenders proceeded against in a financial year. That is not CSA alleged offender incidents.",
            ],
            "catalogue": [
                {
                    "name": "Recorded offences",
                    "url": "https://discover.data.vic.gov.au/dataset/data-tables-recorded-offences",
                },
                {
                    "name": "Criminal incidents",
                    "url": "https://discover.data.vic.gov.au/dataset/criminal-incident",
                },
                {
                    "name": "Alleged offender incidents",
                    "url": "https://discover.data.vic.gov.au/dataset/data-tables-alleged-offender-incidents",
                },
                {
                    "name": "ABS Recorded Crime – Offenders",
                    "url": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/latest-release",
                },
            ],
        },
        "palette": PALETTE,
        "divisionColours": DIVISION_COLOURS,
        "offences": _records(offences),
        "incidents": _records(incidents),
        "offenders": _records(offenders),
        "products": _records(products),
        "divisions": _records(offence_division_trends()),
        "subdivisions": _records(offence_subdivision_change(int(offences["year"].min()), latest)),
        "lgas": _records(profile),
        "lgaMap": _records(profile_map),
        "metro": _records(metro_regional_trends()),
        "lgaYoy": _records(yoy),
        "subgroups": _records(top_subgroups()),
        "heatmap": _records(heatmap_all),
        "investigation": _records(investigation_status_trends()),
        "family": _records(family_incident_share()),
        "charge": _records(charge_status_share()),
        "ageSex": _records(
            read_sql(
                """
                SELECT year, sex, age_group, is_youth, alleged_offender_incidents
                FROM statewide_offenders_age_sex
                WHERE is_total_row = 0
                  AND LOWER(sex) IN ('males', 'females')
                ORDER BY year, sex, age_group
                """
            )
        ),
        "sex": _records(sex_distribution()),
        "youthAdult": _records(youth_vs_adult()),
        "youthAge": _records(
            read_sql(
                """
                SELECT year, sex, age_group, metric_value AS alleged_offender_incidents
                FROM statewide_youth_metrics
                WHERE category = 'Alleged Offender Incidents'
                  AND LOWER(sex) IN ('males', 'females')
                  AND CAST(age_group AS INTEGER) BETWEEN 10 AND 17
                ORDER BY year, sex, CAST(age_group AS INTEGER)
                """
            )
        ),
        "principal": _records(
            read_sql(
                """
                SELECT year, offence_division, offence_subdivision,
                       SUM(alleged_offender_incidents) AS alleged_offender_incidents
                FROM statewide_offenders
                GROUP BY year, offence_division, offence_subdivision
                ORDER BY year, alleged_offender_incidents DESC
                """
            )
        ),
        "offenderLgas": _records(offender_lgas),
        "quality": _records(quality),
        "qualityScores": scores,
        **_abs_payload(),
    }


def _abs_payload() -> dict:
    try:
        return {
            "absStates": _records(abs_state_totals_latest()),
            "absCompare": _records(abs_victoria_vs_australia())[0],
            "absVicTrend": _records(abs_victoria_persons_trend()),
            "absAusTrend": _records(abs_australia_trend()),
            "absVicSex": _records(abs_victoria_sex_latest()),
            "absYouthStates": _records(abs_youth_by_state_latest()),
            "absYouthTrend": _records(abs_victoria_youth_trend()),
            "absPrincipal": _records(
                abs_principal_offence_latest("Victoria").query("offence_level == 'division'")
            ),
            "absProductNote": _records(csa_vs_abs_product_note())[0],
        }
    except Exception:
        return {}


def _quality_table() -> tuple[pd.DataFrame, dict]:
    generate_quality_reports()
    detail = pd.read_csv(DATA_EXPORTS / "data_quality_report.csv")
    scores = score_quality(table_quality_frame())
    return detail, scores


def _records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records"))


def write_tableau_extracts(output_dir: Path | None = None) -> dict[str, Path]:
    ensure_output_dirs()
    folder = Path(output_dir) if output_dir else DASHBOARD_DIR / "data"
    folder.mkdir(parents=True, exist_ok=True)

    mart = build_tableau_mart()
    offences = add_yoy(statewide_annual_totals(), "offence_count")
    incidents = add_yoy(statewide_incident_totals(), "incident_count")
    offenders = add_yoy(statewide_offender_totals(), "alleged_offender_incidents")
    products = statistical_product_comparison()
    profile = lga_profile()
    quality, _scores = _quality_table()

    statewide = pd.concat(
        [
            offences.assign(**{"Statistical Product": "Recorded offences"})
            .rename(columns={"offence_count": "Count", "rate_per_100000": "Rate per 100000",
                             "offence_count_yoy": "YoY Count", "offence_count_yoy_pct": "YoY %"}),
            incidents.assign(**{"Statistical Product": "Criminal incidents"})
            .rename(columns={"incident_count": "Count", "rate_per_100000": "Rate per 100000",
                             "incident_count_yoy": "YoY Count", "incident_count_yoy_pct": "YoY %"}),
            offenders.assign(**{"Statistical Product": "Alleged offender incidents"})
            .rename(columns={"alleged_offender_incidents": "Count",
                             "rate_per_100000_age_10_plus": "Rate per 100000",
                             "alleged_offender_incidents_yoy": "YoY Count",
                             "alleged_offender_incidents_yoy_pct": "YoY %"}),
        ],
        ignore_index=True,
    )[["Statistical Product", "year", "year_ending", "Count", "Rate per 100000", "YoY Count", "YoY %"]]
    statewide = statewide.rename(columns={"year": "Year", "year_ending": "Year Ending"})

    lga_sheet = profile.rename(
        columns={
            "year": "Year",
            "police_region": "Police Region",
            "local_government_area": "Local Government Area",
            "metro_regional": "Metro Regional",
            "recorded_offences": "Recorded Offences",
            "recorded_offences_rate": "Offence Rate per 100000",
            "criminal_incidents": "Criminal Incidents",
            "criminal_incidents_rate": "Incident Rate per 100000",
            "alleged_offender_incidents": "Alleged Offender Incidents",
            "alleged_offender_incidents_rate": "Alleged Offender Rate per 100000",
        }
    )

    paths: dict[str, Path] = {}
    csv_writes = {
        "tableau_mart.csv": mart,
        "statewide_products.csv": statewide,
        "offence_divisions.csv": offence_division_trends(),
        "lga_profile.csv": lga_sheet,
        "metro_regional.csv": metro_regional_trends(),
        "lga_yoy.csv": lga_yoy_change(),
        "investigation_status.csv": investigation_status_trends(),
        "family_incidents.csv": family_incident_share(),
        "charge_status.csv": charge_status_share(),
        "age_sex.csv": age_sex_distribution(),
        "sex_distribution.csv": sex_distribution(),
        "youth_adult.csv": youth_vs_adult(),
        "youth_single_year.csv": youth_single_year_of_age(),
        "principal_offence.csv": principal_offence_latest(),
        "offender_lgas.csv": latest_lga_offenders(),
        "data_quality.csv": quality,
        "statistical_products.csv": products,
        "abs_state_totals.csv": abs_state_totals_latest(),
        "abs_victoria_trend.csv": abs_victoria_persons_trend(),
        "abs_youth_by_state.csv": abs_youth_by_state_latest(),
        "abs_vs_csa_note.csv": csa_vs_abs_product_note(),
    }
    for name, df in csv_writes.items():
        path = folder / name
        df.to_csv(path, index=False)
        paths[name] = path

    excel_path = folder / "Victorian_Crime_Intelligence.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        statewide.to_excel(writer, sheet_name="Statewide Products", index=False)
        offence_division_trends().to_excel(writer, sheet_name="Offence Divisions", index=False)
        lga_sheet.to_excel(writer, sheet_name="LGA Profile", index=False)
        metro_regional_trends().to_excel(writer, sheet_name="Metro Regional", index=False)
        charge_status_share().to_excel(writer, sheet_name="Charge Status", index=False)
        investigation_status_trends().to_excel(writer, sheet_name="Investigation Status", index=False)
        age_sex_distribution().to_excel(writer, sheet_name="Age and Sex", index=False)
        youth_vs_adult().to_excel(writer, sheet_name="Youth vs Adult", index=False)
        principal_offence_latest().to_excel(writer, sheet_name="Principal Offence", index=False)
        quality.to_excel(writer, sheet_name="Data Quality", index=False)
        abs_state_totals_latest().to_excel(writer, sheet_name="ABS States", index=False)
        abs_victoria_persons_trend().to_excel(writer, sheet_name="ABS Vic Trend", index=False)
        abs_youth_by_state_latest().to_excel(writer, sheet_name="ABS Youth", index=False)
        csa_vs_abs_product_note().to_excel(writer, sheet_name="ABS vs CSA note", index=False)
        mart.to_excel(writer, sheet_name="Tableau Mart", index=False)
    paths["Victorian_Crime_Intelligence.xlsx"] = excel_path
    paths["tableau_mart.csv"] = folder / "tableau_mart.csv"
    return paths
