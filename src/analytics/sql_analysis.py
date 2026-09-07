"""Execute the analysis-only SQL file against the CSA SQLite database."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analytics.descriptive import get_connection
from src.config import DATA_EXPORTS, PROJECT_ROOT, ensure_output_dirs

SQL_FILES = [
    PROJECT_ROOT / "sql" / "crime_analysis.sql",
    PROJECT_ROOT / "sql" / "stage2_analysis.sql",
    PROJECT_ROOT / "sql" / "stage3_analysis.sql",
]


def split_sql_statements(sql_text: str) -> list[tuple[str, str]]:
    """Split the analysis SQL file into (title, statement) pairs."""
    blocks = []
    current_title = "untitled"
    buffer: list[str] = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-- ==="):
            continue
        if stripped.startswith("-- Q"):
            current_title = stripped.lstrip("- ").strip()
            continue
        if stripped.startswith("--"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(buffer).strip()
            if statement:
                blocks.append((current_title, statement))
            buffer = []
    return blocks


def run_sql_analysis() -> list[tuple[str, pd.DataFrame]]:
    ensure_output_dirs()
    results: list[tuple[str, pd.DataFrame]] = []
    n = 0
    with get_connection() as conn:
        for sql_file in SQL_FILES:
            if not sql_file.exists():
                continue
            for title, statement in split_sql_statements(sql_file.read_text()):
                n += 1
                df = pd.read_sql_query(statement, conn)
                safe_title = "".join(ch.lower() if ch.isalnum() else "_" for ch in title)
                safe_title = "_".join(part for part in safe_title.split("_") if part)[:50]
                out = DATA_EXPORTS / f"sql_{n:02d}_{safe_title}.csv"
                df.to_csv(out, index=False)
                results.append((title, df))
                print(f"{n:02d}. {title}: {len(df):,} rows -> {out.name}")
    return results


if __name__ == "__main__":
    run_sql_analysis()
