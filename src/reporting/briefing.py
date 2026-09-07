"""Automated HTML and Excel briefing from official CSA and ABS tables."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.analytics.descriptive import add_yoy, statewide_annual_totals
from src.analytics.incidents import statistical_product_comparison, statewide_incident_totals
from src.analytics.national import (
    abs_product_caveat,
    abs_state_totals_latest,
    abs_victoria_persons_trend,
    abs_victoria_vs_australia,
    abs_victoria_youth_trend,
    abs_youth_by_state_latest,
    csa_vs_abs_product_note,
)
from src.analytics.offender import statewide_offender_totals, youth_vs_adult
from src.config import DATA_EXPORTS, REPORTS_DIR, ensure_output_dirs
from src.validation.quality_checks import score_quality, table_quality_frame


def _fmt(value: float, digits: int = 0) -> str:
    if digits == 0:
        return f"{value:,.0f}"
    return f"{value:,.{digits}f}"


def briefing_payload() -> dict:
    offences = add_yoy(statewide_annual_totals(), "offence_count")
    incidents = add_yoy(statewide_incident_totals(), "incident_count")
    offenders = add_yoy(statewide_offender_totals(), "alleged_offender_incidents")
    products = statistical_product_comparison()
    youth = youth_vs_adult()
    abs_compare = abs_victoria_vs_australia().iloc[0]
    abs_states = abs_state_totals_latest()
    abs_vic = abs_victoria_persons_trend()
    abs_youth = abs_victoria_youth_trend()
    youth_states = abs_youth_by_state_latest()
    product_note = csa_vs_abs_product_note().iloc[0]
    quality = score_quality(table_quality_frame())

    latest_off = offences.iloc[-1]
    first_off = offences.iloc[0]
    latest_inc = incidents.iloc[-1]
    latest_aoi = offenders.iloc[-1]
    youth_latest = youth.loc[youth["year"].eq(youth["year"].max())]
    youth_count = float(
        youth_latest.loc[youth_latest["age_band"].eq("Youth (10-17)"), "alleged_offender_incidents"].iloc[0]
    )
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "offence_count": float(latest_off["offence_count"]),
        "offence_rate": float(latest_off["rate_per_100000"]),
        "offence_yoy": float(latest_off["offence_count_yoy_pct"]),
        "offence_long_term": 100.0
        * (float(latest_off["offence_count"]) - float(first_off["offence_count"]))
        / float(first_off["offence_count"]),
        "incident_count": float(latest_inc["incident_count"]),
        "incident_yoy": float(latest_inc["incident_count_yoy_pct"]),
        "aoi_count": float(latest_aoi["alleged_offender_incidents"]),
        "aoi_yoy": float(latest_aoi["alleged_offender_incidents_yoy_pct"]),
        "youth_aoi": youth_count,
        "youth_aoi_share": 100.0 * youth_count / float(latest_aoi["alleged_offender_incidents"]),
        "abs_vic_count": float(abs_compare["victoria_offenders"]),
        "abs_vic_rate": float(abs_compare["victoria_rate"]),
        "abs_aus_count": float(abs_compare["australia_offenders"]),
        "abs_aus_rate": float(abs_compare["australia_rate"]),
        "abs_vic_share": float(abs_compare["victoria_share_of_australia_pct"]),
        "abs_vic_rate_index": float(abs_compare["victoria_rate_vs_australia_pct"]),
        "abs_vic_yoy": float(abs_compare["victoria_yoy_count_pct"]),
        "abs_youth": float(abs_compare["victoria_youth_offenders"]),
        "abs_youth_share": float(abs_compare["victoria_youth_share_pct"]),
        "quality": quality["overall"],
        "caveat": abs_product_caveat(),
        "products": products,
        "abs_states": abs_states,
        "abs_vic_trend": abs_vic,
        "abs_youth_trend": abs_youth,
        "abs_youth_states": youth_states,
        "product_note": product_note,
        "offences": offences,
        "incidents": incidents,
        "offenders": offenders,
        "youth": youth,
    }


def render_html(payload: dict) -> str:
    states_rows = "\n".join(
        f"<tr{' class=\"vic\"' if r.jurisdiction == 'Victoria' else ''}>"
        f"<td>{r.jurisdiction}</td><td>{_fmt(r.offender_count)}</td>"
        f"<td>{_fmt(r.rate_per_100000_age_10_plus, 1)}</td></tr>"
        for r in payload["abs_states"].itertuples()
    )
    note = payload["product_note"]
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<title>Victorian Crime &amp; Justice briefing</title>
<style>
body {{ font-family: "Source Serif 4", Georgia, serif; margin: 0; color: #1B365D; background: #F3EEE4; }}
header {{ background: #0E2140; color: #FFFDF8; padding: 36px 48px 28px; }}
header p {{ color: #C4A35A; margin: 8px 0 0; }}
main {{ padding: 32px 48px 48px; max-width: 1100px; }}
h1, h2 {{ margin: 0 0 12px; }}
h2 {{ margin-top: 36px; }}
.kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 24px 0; }}
.card {{ background: #FFFDF8; border: 1px solid #E4DDD0; padding: 16px 18px; }}
.card strong {{ display: block; font-size: 26px; }}
.card span {{ color: #5B6B7A; font-size: 13px; }}
.callout {{ background: #FFF7E8; border-left: 4px solid #C4A35A; padding: 14px 16px; margin: 20px 0; }}
table {{ border-collapse: collapse; width: 100%; background: #FFFDF8; }}
th, td {{ border-bottom: 1px solid #E4DDD0; padding: 8px 10px; text-align: left; }}
tr.vic {{ background: #F7F1E2; font-weight: 600; }}
footer {{ color: #5B6B7A; font-size: 13px; margin-top: 36px; }}
</style>
</head>
<body>
<header>
<h1>Victorian Crime &amp; Justice Intelligence briefing</h1>
<p>Official CSA and ABS aggregates only. Generated {payload["generated"]}.</p>
</header>
<main>
<p>This briefing summarises Crime Statistics Agency products for year ending March 2026
and Australian Bureau of Statistics Recorded Crime – Offenders for 2024–25.
The two agencies measure different things and are not interchangeable.</p>

<div class="kpis">
  <div class="card"><strong>{_fmt(payload["offence_count"])}</strong><span>CSA recorded offences, 2026</span></div>
  <div class="card"><strong>{_fmt(payload["incident_count"])}</strong><span>CSA criminal incidents, 2026</span></div>
  <div class="card"><strong>{_fmt(payload["aoi_count"])}</strong><span>CSA alleged offender incidents, 2026</span></div>
  <div class="card"><strong>{_fmt(payload["abs_vic_count"])}</strong><span>ABS Victoria unique offenders, 2024–25</span></div>
</div>

<div class="callout">{payload["caveat"]}</div>

<h2>CSA Victoria, year ending March 2026</h2>
<ul>
<li>Recorded offences: {_fmt(payload["offence_count"])} (rate {_fmt(payload["offence_rate"], 1)} per 100,000; {payload["offence_yoy"]:+.1f}% on 2025; {payload["offence_long_term"]:+.1f}% since 2017).</li>
<li>Criminal incidents: {_fmt(payload["incident_count"])} ({payload["incident_yoy"]:+.1f}% on 2025).</li>
<li>Alleged offender incidents: {_fmt(payload["aoi_count"])} ({payload["aoi_yoy"]:+.1f}% on 2025). Youth 10–17: {_fmt(payload["youth_aoi"])} ({payload["youth_aoi_share"]:.1f}%).</li>
</ul>

<h2>ABS unique offenders, 2024–25</h2>
<ul>
<li>Victoria: {_fmt(payload["abs_vic_count"])} offenders; rate {_fmt(payload["abs_vic_rate"], 1)} per 100,000 aged 10+ ({payload["abs_vic_yoy"]:+.1f}% on 2023–24).</li>
<li>Australia: {_fmt(payload["abs_aus_count"])} offenders; rate {_fmt(payload["abs_aus_rate"], 1)}.</li>
<li>Victoria is {payload["abs_vic_share"]:.1f}% of Australian offenders and its rate is {payload["abs_vic_rate_index"]:.1f}% of the national rate.</li>
<li>Victorian youth offenders (10–17): {_fmt(payload["abs_youth"])} ({payload["abs_youth_share"]:.1f}% of Victorian offenders).</li>
</ul>

<table>
<thead><tr><th>Jurisdiction</th><th>ABS offenders</th><th>Rate per 100,000 aged 10+</th></tr></thead>
<tbody>{states_rows}</tbody>
</table>

<h2>Why CSA 195,342 is not ABS 59,693</h2>
<p>CSA {note["csa_product"]} for {note["csa_period"]}: <strong>{_fmt(note["csa_measure"])}</strong>.</p>
<p>ABS {note["abs_product"]} for {note["abs_period"]}: <strong>{_fmt(note["abs_measure"])}</strong>.</p>
<p>These figures must not be subtracted, ratioed or presented as a clearance rate.</p>

<h2>Data quality</h2>
<p>Loaded-table quality score: <strong>{payload["quality"]}%</strong>. Scores measure missing counts, negatives and duplicate keys in ingested tables, not police recording practice.</p>

<footer>
<p>Sources: Crime Statistics Agency (CC BY 4.0), year ending March 2026; Australian Bureau of Statistics, Recorded Crime – Offenders, 2024–25 (CC BY 4.0). Cells in ABS tables are randomly adjusted for confidentiality.</p>
<p>Aggregate analysis only. No individual-level identification.</p>
</footer>
</main>
</body>
</html>
"""


def write_excel(payload: dict, path: Path) -> Path:
    cover = pd.DataFrame(
        [
            {"item": "Generated (UTC)", "value": payload["generated"]},
            {"item": "CSA recorded offences 2026", "value": payload["offence_count"]},
            {"item": "CSA criminal incidents 2026", "value": payload["incident_count"]},
            {"item": "CSA alleged offender incidents 2026", "value": payload["aoi_count"]},
            {"item": "ABS Victoria unique offenders 2024-25", "value": payload["abs_vic_count"]},
            {"item": "ABS Victoria rate per 100,000 aged 10+", "value": payload["abs_vic_rate"]},
            {"item": "ABS Australia unique offenders 2024-25", "value": payload["abs_aus_count"]},
            {"item": "ABS Australia rate per 100,000 aged 10+", "value": payload["abs_aus_rate"]},
            {"item": "ABS Victoria youth offenders 10-17", "value": payload["abs_youth"]},
            {"item": "Loaded-table quality score", "value": payload["quality"]},
            {"item": "ABS caveat", "value": payload["caveat"]},
        ]
    )
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        cover.to_excel(writer, sheet_name="Cover", index=False)
        payload["products"].to_excel(writer, sheet_name="CSA products", index=False)
        payload["abs_states"].to_excel(writer, sheet_name="ABS states", index=False)
        payload["abs_vic_trend"].to_excel(writer, sheet_name="ABS Victoria trend", index=False)
        payload["abs_youth_trend"].to_excel(writer, sheet_name="ABS Vic youth", index=False)
        payload["abs_youth_states"].to_excel(writer, sheet_name="ABS youth by state", index=False)
        pd.DataFrame([payload["product_note"]]).to_excel(
            writer, sheet_name="Do not compare", index=False
        )
    return path


def generate_briefing() -> dict[str, Path]:
    ensure_output_dirs()
    payload = briefing_payload()
    html_path = REPORTS_DIR / "victorian_crime_briefing.html"
    excel_path = REPORTS_DIR / "victorian_crime_briefing.xlsx"
    html_path.write_text(render_html(payload))
    write_excel(payload, excel_path)
    payload["products"].to_csv(DATA_EXPORTS / "abs_csa_product_separation.csv", index=False)
    payload["abs_states"].to_csv(DATA_EXPORTS / "abs_state_totals_latest.csv", index=False)
    payload["abs_vic_trend"].to_csv(DATA_EXPORTS / "abs_victoria_trend.csv", index=False)
    print(f"wrote {html_path}")
    print(f"wrote {excel_path}")
    return {"html": html_path, "excel": excel_path}


if __name__ == "__main__":
    generate_briefing()
