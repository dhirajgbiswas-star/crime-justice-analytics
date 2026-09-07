"""Write the interactive public HTML dashboard."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import DASHBOARD_DIR, ensure_output_dirs
from src.dashboard.mart import dashboard_payload

TEMPLATE = Path(__file__).with_name("templates") / "public_dashboard.html"


def write_public_html(output_path: Path | None = None) -> Path:
    ensure_output_dirs()
    path = output_path or (DASHBOARD_DIR / "Victorian_Crime_Justice_Dashboard.html")
    payload = dashboard_payload()
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__DASHBOARD_DATA__", json.dumps(payload, separators=(",", ":")))
    path.write_text(html, encoding="utf-8")
    return path
