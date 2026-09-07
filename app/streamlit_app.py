"""Streamlit data-request service for Victorian CSA aggregates."""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.analytics.descriptive import get_connection, read_sql
from src.config import SQLITE_PATH

REQUEST_TYPES = {
    "Recorded offences by LGA": {
        "table": "lga_offence_totals",
        "count_col": "offence_count",
        "category_col": None,
        "note": "Recorded offences are not unique criminal incidents.",
    },
    "Recorded offences by offence division": {
        "table": "lga_offences",
        "count_col": "offence_count",
        "category_col": "offence_division",
        "note": "LGA by offence division. One incident can generate multiple offences.",
    },
    "Criminal incidents by LGA": {
        "table": "lga_incident_totals",
        "count_col": "incidents_recorded",
        "category_col": None,
        "note": "Criminal incidents are a different CSA product from recorded offences.",
    },
    "Alleged offender incidents by LGA": {
        "table": "lga_offender_totals",
        "count_col": "alleged_offender_incidents",
        "category_col": None,
        "note": "Alleged offender incidents are not findings of guilt.",
    },
}


def _distinct(sql: str) -> list[str]:
    df = read_sql(sql)
    return [str(v) for v in df.iloc[:, 0].dropna().tolist()]


def next_request_id(conn: sqlite3.Connection) -> str:
    year = datetime.now().year
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM data_requests WHERE request_id LIKE ?",
        (f"DR-{year}-%",),
    ).fetchone()
    n = int(row[0] if row is not None else 0) + 1
    return f"DR-{year}-{n:04d}"


def run_query(spec: dict, lga: str, category: str | None, start_year: int, end_year: int) -> pd.DataFrame:
    table = spec["table"]
    count_col = spec["count_col"]
    clauses = ["year BETWEEN ? AND ?"]
    params: list = [start_year, end_year]
    if table.endswith("_totals"):
        clauses.append("is_region_total = 0")
    if lga != "All LGAs":
        clauses.append("local_government_area = ?")
        params.append(lga)
    select_extra = ""
    if spec["category_col"]:
        select_extra = f", {spec['category_col']}"
        if category and category != "All categories":
            clauses.append(f"{spec['category_col']} = ?")
            params.append(category)
    sql = f"""
        SELECT year, local_government_area{select_extra}, SUM({count_col}) AS measure_count
        FROM {table}
        WHERE {' AND '.join(clauses)}
        GROUP BY year, local_government_area{select_extra}
        ORDER BY year, local_government_area
    """
    return read_sql(sql, tuple(params))


def summarise(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total": 0, "yoy_pct": None, "years": 0}
    annual = df.groupby("year", as_index=False)["measure_count"].sum().sort_values("year")
    yoy = None
    if len(annual) >= 2 and annual.iloc[-2]["measure_count"]:
        yoy = 100.0 * (annual.iloc[-1]["measure_count"] - annual.iloc[-2]["measure_count"]) / annual.iloc[-2]["measure_count"]
    return {
        "total": float(df["measure_count"].sum()),
        "yoy_pct": yoy,
        "years": int(annual["year"].nunique()),
        "annual": annual,
    }


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()


def main() -> None:
    st.set_page_config(page_title="Victorian crime data request service", layout="wide")
    st.title("Victorian Crime & Justice data request service")
    st.caption(
        "Aggregate CSA statistics only. This service does not identify individuals "
        "and does not provide alleged-offender profiling."
    )
    st.info(
        "ABS Recorded Crime – Offenders counts unique alleged offenders proceeded "
        "against in a financial year. That figure is not CSA alleged offender incidents "
        "and is not available as a data-request extract from this form."
    )
    try:
        from src.analytics.national import abs_victoria_vs_australia

        abs_row = abs_victoria_vs_australia().iloc[0]
        with st.expander("ABS national comparison (read only, not a data request)"):
            c1, c2, c3 = st.columns(3)
            c1.metric("ABS Victoria offenders, 2024–25", f"{abs_row['victoria_offenders']:,.0f}")
            c2.metric("ABS Victoria rate / 100,000 aged 10+", f"{abs_row['victoria_rate']:,.1f}")
            c3.metric("ABS Australia rate / 100,000 aged 10+", f"{abs_row['australia_rate']:,.1f}")
            st.caption(str(abs_row["caveat"]))
    except Exception:
        pass

    if not SQLITE_PATH.exists():
        st.error("Analytical database not found. Run `python -m src.pipeline` first.")
        return

    lgas = ["All LGAs"] + _distinct(
        "SELECT DISTINCT local_government_area FROM lga_offence_totals "
        "WHERE is_region_total = 0 ORDER BY 1"
    )
    categories = ["All categories"] + _distinct(
        "SELECT DISTINCT offence_division FROM statewide_offences ORDER BY 1"
    )
    years = _distinct("SELECT DISTINCT year FROM statewide_offences ORDER BY 1")
    year_values = [int(y) for y in years]

    with st.form("request"):
        request_type = st.selectbox("Request type", list(REQUEST_TYPES))
        lga = st.selectbox("Local government area", lgas)
        category = st.selectbox("Offence category", categories)
        start_year, end_year = st.select_slider(
            "Reporting years (year ending March)",
            options=year_values,
            value=(min(year_values), max(year_values)),
        )
        output_format = st.radio("Output format", ["CSV", "Excel"], horizontal=True)
        submitted = st.form_submit_button("Submit request")

    if not submitted:
        return

    spec = REQUEST_TYPES[request_type]
    if spec["category_col"] is None and category != "All categories":
        st.warning("This request type is LGA totals and does not filter by offence category.")
        category_filter = None
    else:
        category_filter = None if category == "All categories" else category

    result = run_query(spec, lga, category_filter, int(start_year), int(end_year))
    stats = summarise(result)
    request_id = None
    with get_connection() as conn:
        request_id = next_request_id(conn)
        conn.execute(
            """
            INSERT INTO data_requests (
                request_id, requested_at, request_type, offence_category, lga,
                start_year, end_year, output_format, status, row_count, summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                datetime.now(timezone.utc).isoformat(),
                request_type,
                category,
                lga,
                int(start_year),
                int(end_year),
                output_format,
                "completed" if not result.empty else "no_rows",
                int(len(result)),
                f"total={stats['total']:.0f}",
            ),
        )
        conn.commit()

    st.subheader(f"Request ID: {request_id}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", f"{stats['total']:,.0f}")
    c2.metric("Rows returned", f"{len(result):,}")
    c3.metric(
        "Latest YoY change",
        "n/a" if stats["yoy_pct"] is None else f"{stats['yoy_pct']:.1f}%",
    )
    st.info(spec["note"] + " Crime rates should be used when comparing LGAs with different populations.")
    st.dataframe(result, use_container_width=True)
    if not result.empty:
        annual = stats["annual"].set_index("year")
        st.line_chart(annual)
        if output_format == "CSV":
            st.download_button(
                "Download CSV",
                result.to_csv(index=False).encode("utf-8"),
                file_name=f"{request_id}.csv",
                mime="text/csv",
            )
        else:
            st.download_button(
                "Download Excel",
                to_excel_bytes(result),
                file_name=f"{request_id}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


if __name__ == "__main__":
    main()
