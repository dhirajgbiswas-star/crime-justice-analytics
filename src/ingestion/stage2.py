"""Ingest CSA criminal-incident and alleged-offender Excel tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import YOUTH_AGE_GROUPS
from src.ingestion.load_csa import (
    classify_metro_regional,
    load_excel_table,
    prepare_lga_totals,
)


def _to_numeric_counts(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "year" in out.columns:
        out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    for col in out.columns:
        if col in {
            "incidents_recorded",
            "alleged_offender_incidents",
            "metric_value",
            "offence_count",
        } or "rate_per" in col:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def _flag_totals(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    mask = False
    for col in columns:
        if col in out.columns:
            mask = mask | out[col].astype("string").str.lower().eq("total")
    out["is_total_row"] = mask.astype(int) if not isinstance(mask, bool) else 0
    return out


def prepare_lga_volume(df: pd.DataFrame, count_col: str) -> pd.DataFrame:
    """Reuse LGA total logic when the count column is not offence_count."""
    renamed = df.rename(columns={count_col: "offence_count"})
    if "rate_per_100_000_population" not in renamed.columns:
        renamed["rate_per_100_000_population"] = pd.NA
    prepared = prepare_lga_totals(renamed)
    return prepared.rename(columns={"offence_count": count_col})


def add_youth_flag(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "age_group" not in out.columns:
        return out

    def _youth(value: object) -> int:
        text = str(value).strip()
        if text in YOUTH_AGE_GROUPS:
            return 1
        if text.isdigit() and 10 <= int(text) <= 17:
            return 1
        return 0

    out["is_youth"] = out["age_group"].map(_youth)
    return out


def load_stage2_tables(
    incidents_vis: Path,
    incidents_lga: Path,
    offenders_vis: Path,
    offenders_lga: Path,
) -> dict[str, pd.DataFrame]:
    """Load analysis tables from official Stage 2 workbooks."""
    statewide_incidents = _to_numeric_counts(load_excel_table(incidents_vis, "Table 01"))
    statewide_incident_family = _to_numeric_counts(load_excel_table(incidents_vis, "Table 03"))
    statewide_incident_charge_status = _to_numeric_counts(
        load_excel_table(incidents_vis, "Table 04")
    )
    lga_incident_totals = prepare_lga_volume(
        load_excel_table(incidents_lga, "Table 01"), "incidents_recorded"
    )
    lga_incidents = _to_numeric_counts(load_excel_table(incidents_lga, "Table 02"))
    lga_incident_charge_status = _to_numeric_counts(
        load_excel_table(incidents_lga, "Table 05")
    )

    statewide_offenders = _to_numeric_counts(load_excel_table(offenders_vis, "Table 01"))
    statewide_offenders_age_sex = add_youth_flag(
        _flag_totals(
            _to_numeric_counts(load_excel_table(offenders_vis, "Table 02")),
            ["sex", "age_group"],
        )
    )
    statewide_offenders_sex_offence = _to_numeric_counts(
        load_excel_table(offenders_vis, "Table 03")
    )
    statewide_youth_metrics = add_youth_flag(
        _to_numeric_counts(load_excel_table(offenders_vis, "Table 07"))
    )
    statewide_offender_outcomes = _to_numeric_counts(
        load_excel_table(offenders_vis, "Table 05")
    )
    lga_offender_totals = prepare_lga_volume(
        load_excel_table(offenders_lga, "Table 01"), "alleged_offender_incidents"
    )
    lga_offenders_age = add_youth_flag(
        _to_numeric_counts(load_excel_table(offenders_lga, "Table 03"))
    )
    lga_offenders_sex = _to_numeric_counts(load_excel_table(offenders_lga, "Table 04"))
    lga_offenders_offence = _to_numeric_counts(load_excel_table(offenders_lga, "Table 02"))

    # Silence unused import if classify is only used via prepare_lga_totals.
    _ = classify_metro_regional

    return {
        "statewide_incidents": statewide_incidents,
        "statewide_incident_family": statewide_incident_family,
        "statewide_incident_charge_status": statewide_incident_charge_status,
        "lga_incident_totals": lga_incident_totals,
        "lga_incidents": lga_incidents,
        "lga_incident_charge_status": lga_incident_charge_status,
        "statewide_offenders": statewide_offenders,
        "statewide_offenders_age_sex": statewide_offenders_age_sex,
        "statewide_offenders_sex_offence": statewide_offenders_sex_offence,
        "statewide_youth_metrics": statewide_youth_metrics,
        "statewide_offender_outcomes": statewide_offender_outcomes,
        "lga_offender_totals": lga_offender_totals,
        "lga_offenders_age": lga_offenders_age,
        "lga_offenders_sex": lga_offenders_sex,
        "lga_offenders_offence": lga_offenders_offence,
    }
