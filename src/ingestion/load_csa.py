"""Load CSA Excel tables into cleaned DataFrames and a SQLite analysis database."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import (
    DATA_PROCESSED,
    DATA_RAW,
    EASTERN_METRO_LGAS,
    SQLITE_PATH,
    SOURCE_FILES,
    ensure_output_dirs,
    source_path,
)


def _standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Snake-case column names without inventing business fields."""
    out = df.copy()
    out.columns = (
        out.columns.astype(str)
        .str.strip()
        .str.replace(r"[^0-9A-Za-z]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
        .str.lower()
    )
    return out


def _strip_text(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].astype("string").str.strip()
    return out


def classify_metro_regional(police_region: str, lga: str) -> str:
    """Classify an LGA as Metropolitan or Regional using police region plus Eastern metro LGAs."""
    region = (police_region or "").strip()
    area = (lga or "").strip()
    if "Metro" in region:
        return "Metropolitan"
    if area in EASTERN_METRO_LGAS:
        return "Metropolitan"
    return "Regional"


def load_excel_table(workbook: Path, sheet: str) -> pd.DataFrame:
    """Read one CSA table sheet and standardise names."""
    df = pd.read_excel(workbook, sheet_name=sheet, engine="openpyxl")
    df = _standardise_columns(df)
    df = _strip_text(df)
    df = df.dropna(how="all")
    return df


def prepare_lga_totals(df: pd.DataFrame) -> pd.DataFrame:
    """LGA recorded-offence totals (Table 01), excluding region Total rows."""
    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["offence_count"] = pd.to_numeric(out["offence_count"], errors="coerce")
    out["rate_per_100_000_population"] = pd.to_numeric(
        out["rate_per_100_000_population"], errors="coerce"
    )
    out["is_region_total"] = (
        out["local_government_area"].str.lower().eq("total").astype(int)
    )
    out["geography_type"] = out["is_region_total"].map(
        {1: "Police region total", 0: "LGA"}
    )
    out["metro_regional"] = [
        classify_metro_regional(region, lga)
        for region, lga in zip(out["police_region"], out["local_government_area"])
    ]
    out.loc[out["is_region_total"] == 1, "metro_regional"] = pd.NA
    return out


def prepare_lga_offences(df: pd.DataFrame) -> pd.DataFrame:
    """Offence type by LGA (Table 02)."""
    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["offence_count"] = pd.to_numeric(out["offence_count"], errors="coerce")
    out["lga_rate_per_100_000_population"] = pd.to_numeric(
        out["lga_rate_per_100_000_population"], errors="coerce"
    )
    out["psa_rate_per_100_000_population"] = pd.to_numeric(
        out["psa_rate_per_100_000_population"], errors="coerce"
    )
    return out


def prepare_statewide_offences(df: pd.DataFrame) -> pd.DataFrame:
    """Statewide offence counts and rates (visualisation Table 01)."""
    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["offence_count"] = pd.to_numeric(out["offence_count"], errors="coerce")
    out["rate_per_100_000_population"] = pd.to_numeric(
        out["rate_per_100_000_population"], errors="coerce"
    )
    return out


def prepare_family_incidents(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["offence_count"] = pd.to_numeric(out["offence_count"], errors="coerce")
    out["rate_per_100_000_population"] = pd.to_numeric(
        out["rate_per_100_000_population"], errors="coerce"
    )
    return out


def prepare_investigation_status(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["offence_count"] = pd.to_numeric(out["offence_count"], errors="coerce")
    return out


def prepare_location_type(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["offence_count"] = pd.to_numeric(out["offence_count"], errors="coerce")
    return out


def write_source_metadata() -> Path:
    ensure_output_dirs()
    records = []
    extracted = datetime.now(timezone.utc).isoformat()
    for key, meta in SOURCE_FILES.items():
        try:
            path = source_path(key)
        except FileNotFoundError:
            continue
        records.append(
            {
                "source_key": key,
                "dataset_name": meta["dataset_name"],
                "local_filename": path.name,
                "bytes": path.stat().st_size,
                "catalogue_url": meta["catalogue_url"],
                "download_url": meta.get("download_url"),
                "publisher": meta["publisher"],
                "licence": meta["licence"],
                "reporting_period": meta["reporting_period"],
                "publication_date": meta["publication_date"],
                "extraction_timestamp_utc": extracted,
            }
        )
    out_path = DATA_PROCESSED / "source_metadata.json"
    out_path.write_text(json.dumps(records, indent=2))
    return out_path


def copy_raw_files() -> None:
    """Copy original workbooks into data/raw without overwriting existing copies."""
    import shutil

    ensure_output_dirs()
    for key in SOURCE_FILES:
        try:
            src = source_path(key)
        except FileNotFoundError:
            continue
        dest = DATA_RAW / src.name
        if dest.exists():
            continue
        shutil.copy2(src, dest)


def export_data_requests(db_path: Path | None = None) -> pd.DataFrame | None:
    """Copy existing data_requests so a rebuild does not discard the audit log."""
    path = db_path or SQLITE_PATH
    if not path.exists():
        return None
    with sqlite3.connect(path) as conn:
        names = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        if "data_requests" not in names:
            return None
        existing = pd.read_sql_query("SELECT * FROM data_requests", conn)
    return existing if not existing.empty else None


def restore_data_requests(conn: sqlite3.Connection, requests: pd.DataFrame | None) -> None:
    if requests is None or requests.empty:
        return
    requests.to_sql("data_requests", conn, index=False, if_exists="append")


def build_sqlite(tables: dict[str, pd.DataFrame]) -> Path:
    ensure_output_dirs()
    preserved_requests = export_data_requests()
    if SQLITE_PATH.exists():
        SQLITE_PATH.unlink()
    with sqlite3.connect(SQLITE_PATH) as conn:
        for name, df in tables.items():
            df.to_sql(name, conn, index=False, if_exists="replace")
        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_lga_totals_year ON lga_offence_totals (year);
            CREATE INDEX IF NOT EXISTS idx_lga_totals_lga ON lga_offence_totals (local_government_area);
            CREATE INDEX IF NOT EXISTS idx_lga_offences_year ON lga_offences (year);
            CREATE INDEX IF NOT EXISTS idx_lga_offences_lga ON lga_offences (local_government_area);
            CREATE INDEX IF NOT EXISTS idx_statewide_year ON statewide_offences (year);
            CREATE INDEX IF NOT EXISTS idx_statewide_div ON statewide_offences (offence_division);
            CREATE INDEX IF NOT EXISTS idx_incidents_year ON statewide_incidents (year);
            CREATE INDEX IF NOT EXISTS idx_lga_incidents_year ON lga_incident_totals (year);
            CREATE INDEX IF NOT EXISTS idx_offenders_year ON statewide_offenders (year);
            CREATE INDEX IF NOT EXISTS idx_age_sex_year ON statewide_offenders_age_sex (year);
            CREATE INDEX IF NOT EXISTS idx_lga_offenders_year ON lga_offender_totals (year);
            CREATE INDEX IF NOT EXISTS idx_lga_offenders_lga ON lga_offender_totals (local_government_area);
            CREATE INDEX IF NOT EXISTS idx_abs_offenders_year ON abs_offenders (year_end);
            CREATE INDEX IF NOT EXISTS idx_abs_offenders_jurisdiction ON abs_offenders (jurisdiction);
            CREATE INDEX IF NOT EXISTS idx_abs_trend_year ON abs_offenders_trend (year_end);
            CREATE INDEX IF NOT EXISTS idx_abs_youth_year ON abs_youth_offenders (year_end);
            CREATE TABLE IF NOT EXISTS data_requests (
                request_id TEXT PRIMARY KEY,
                requested_at TEXT NOT NULL,
                request_type TEXT NOT NULL,
                offence_category TEXT,
                lga TEXT,
                start_year INTEGER,
                end_year INTEGER,
                output_format TEXT,
                status TEXT,
                row_count INTEGER,
                summary TEXT
            );
            """
        )
        restore_data_requests(conn, preserved_requests)
    return SQLITE_PATH


def ingest_all() -> dict[str, pd.DataFrame]:
    """Read the official workbooks, write CSV + SQLite, return in-memory tables."""
    from src.ingestion.abs_offenders import load_abs_tables
    from src.ingestion.download import download_stage2_sources, download_stage3_sources
    from src.ingestion.stage2 import load_stage2_tables

    ensure_output_dirs()
    download_stage2_sources()
    download_stage3_sources()
    copy_raw_files()
    write_source_metadata()

    lga_wb = source_path("lga_recorded_offences")
    vis_wb = source_path("statewide_recorded_offences")

    tables = {
        "lga_offence_totals": prepare_lga_totals(load_excel_table(lga_wb, "Table 01")),
        "lga_offences": prepare_lga_offences(load_excel_table(lga_wb, "Table 02")),
        "lga_location_type": prepare_location_type(load_excel_table(lga_wb, "Table 04")),
        "lga_investigation_status": prepare_investigation_status(
            load_excel_table(lga_wb, "Table 05")
        ),
        "statewide_offences": prepare_statewide_offences(
            load_excel_table(vis_wb, "Table 01")
        ),
        "statewide_family_incidents": prepare_family_incidents(
            load_excel_table(vis_wb, "Table 03")
        ),
        "statewide_investigation_status": prepare_investigation_status(
            load_excel_table(vis_wb, "Table 04")
        ),
    }
    tables.update(
        load_stage2_tables(
            source_path("statewide_criminal_incidents"),
            source_path("lga_criminal_incidents"),
            source_path("statewide_alleged_offenders"),
            source_path("lga_alleged_offenders"),
        )
    )
    tables.update(load_abs_tables())

    for name, df in tables.items():
        csv_path = DATA_PROCESSED / f"{name}.csv"
        df.to_csv(csv_path, index=False)

    build_sqlite(tables)
    return tables


def ingest_abs_only() -> dict[str, pd.DataFrame]:
    """Write ABS tables into the existing SQLite database without rebuilding CSA tables."""
    from src.ingestion.abs_offenders import load_abs_tables
    from src.ingestion.download import download_stage3_sources

    ensure_output_dirs()
    download_stage3_sources()
    write_source_metadata()
    tables = load_abs_tables()
    for name, df in tables.items():
        df.to_csv(DATA_PROCESSED / f"{name}.csv", index=False)
    if not SQLITE_PATH.exists():
        build_sqlite(tables)
        return tables
    with sqlite3.connect(SQLITE_PATH) as conn:
        for name, df in tables.items():
            df.to_sql(name, conn, index=False, if_exists="replace")
        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_abs_offenders_year ON abs_offenders (year_end);
            CREATE INDEX IF NOT EXISTS idx_abs_offenders_jurisdiction ON abs_offenders (jurisdiction);
            CREATE INDEX IF NOT EXISTS idx_abs_trend_year ON abs_offenders_trend (year_end);
            CREATE INDEX IF NOT EXISTS idx_abs_youth_year ON abs_youth_offenders (year_end);
            """
        )
    return tables


if __name__ == "__main__":
    loaded = ingest_all()
    for name, df in loaded.items():
        print(f"{name}: {len(df):,} rows, {list(df.columns)}")
    print(f"SQLite: {SQLITE_PATH}")
