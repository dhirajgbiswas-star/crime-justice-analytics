"""Build Tableau Public extracts, workbook and interactive HTML dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config import DASHBOARD_DIR, ensure_output_dirs
from src.dashboard.mart import write_tableau_extracts
from src.dashboard.public_html import write_public_html


def build_dashboards(include_tableau: bool = True) -> dict[str, Path]:
    ensure_output_dirs()
    outputs: dict[str, Path] = {}
    extracts = write_tableau_extracts()
    outputs.update(extracts)
    html_path = write_public_html()
    outputs["html"] = html_path
    print(f"wrote interactive dashboard {html_path}")

    if include_tableau:
        try:
            from src.dashboard.tableau_workbook import write_tableau_workbook

            workbook = write_tableau_workbook(extracts["tableau_mart.csv"])
            outputs.update(workbook)
            print(f"wrote Tableau workbook {workbook['twbx']}")
        except Exception as exc:  # pragma: no cover - Tableau toolkit is optional
            print(f"Tableau workbook not generated: {exc}")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Victorian crime public dashboards.")
    parser.add_argument("--skip-tableau", action="store_true", help="Write HTML and extracts only.")
    args = parser.parse_args()
    build_dashboards(include_tableau=not args.skip_tableau)
    print(f"Dashboard folder: {DASHBOARD_DIR}")


if __name__ == "__main__":
    main()
