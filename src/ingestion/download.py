"""Download official CSA Excel releases into data/raw without overwriting."""

from __future__ import annotations

import ssl
import subprocess
import urllib.request
from pathlib import Path

from src.config import DATA_RAW, ensure_output_dirs

DOWNLOADS = {
    "Data_Tables_Criminal_Incidents_Visualisation_Year_Ending_March_2026.xlsx": "https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Criminal_Incidents_Visualisation_Year_Ending_March_2026.xlsx",
    "Data_Tables_LGA_Criminal_Incidents_Year_Ending_March_2026.xlsx": "https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Criminal_Incidents_Year_Ending_March_2026.xlsx",
    "Data_Tables_Alleged_Offender_Incidents_Visualisation_Year_Ending_March_2026.xlsx": "https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Alleged_Offender_Incidents_Visualisation_Year_Ending_March_2026.xlsx",
    "Data_Tables_LGA_Alleged_Offenders_Year_Ending_March_2026.xlsx": "https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Alleged_Offenders_Year_Ending_March_2026.xlsx",
}

ABS_DOWNLOADS = {
    "ABS_Offenders_Australia_2024-25.xlsx": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/1.%20Offenders%2C%20Australia.xlsx",
    "ABS_Offenders_States_2024-25.xlsx": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/2.%20Offenders%2C%20states%20and%20territories.xlsx",
    "ABS_Youth_Offenders_2024-25.xlsx": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/3.%20Youth%20offenders.xlsx",
}


def _download_with_curl(url: str, dest: Path) -> None:
    subprocess.run(
        ["curl", "-fsSL", "-A", "crime-justice-analytics/1.0", "-o", str(dest), url],
        check=True,
    )


def _download_with_urllib(url: str, dest: Path) -> None:
    try:
        import certifi

        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "crime-justice-analytics/1.0"})
    with urllib.request.urlopen(req, timeout=120, context=context) as response:
        dest.write_bytes(response.read())


def _download_set(files: dict[str, str], force: bool = False) -> list[Path]:
    ensure_output_dirs()
    saved: list[Path] = []
    for filename, url in files.items():
        dest = DATA_RAW / filename
        if dest.exists() and dest.stat().st_size > 1000 and not force:
            print(f"exists, skip: {dest.name}")
            saved.append(dest)
            continue
        print(f"downloading {filename}")
        try:
            _download_with_curl(url, dest)
        except (subprocess.CalledProcessError, FileNotFoundError):
            _download_with_urllib(url, dest)
        print(f"  saved {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
        saved.append(dest)
    return saved


def download_stage2_sources(force: bool = False) -> list[Path]:
    return _download_set(DOWNLOADS, force=force)


def download_stage3_sources(force: bool = False) -> list[Path]:
    return _download_set(ABS_DOWNLOADS, force=force)


if __name__ == "__main__":
    download_stage2_sources()
    download_stage3_sources()
