"""Project paths, source metadata and analysis constants."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_EXPORTS = PROJECT_ROOT / "data" / "exports"
FIGURES_DIR = PROJECT_ROOT / "reports" / "generated" / "figures"
REPORTS_DIR = PROJECT_ROOT / "reports" / "generated"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard" / "tableau-public"
LOGS_DIR = PROJECT_ROOT / "logs"
SQLITE_PATH = DATA_PROCESSED / "victorian_crime.db"

# Official source files already downloaded into the workspace folder.
SOURCE_FILES = {
    "lga_recorded_offences": {
        "filename": "Data_Tables_LGA_Recorded_Offences_Year_Ending_March_2026 (1).xlsx",
        "dataset_name": "Recorded offences by LGA - Year Ending Mar 2026",
        "catalogue_url": "https://discover.data.vic.gov.au/dataset/data-tables-recorded-offences",
        "publisher": "Crime Statistics Agency (Victoria)",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Year ending March 2017 to year ending March 2026",
        "publication_date": "2026-06-19",
    },
    "statewide_recorded_offences": {
        "filename": "Data_Tables_Recorded_Offences_Visualisation_Year_Ending_March_2026 (1).xlsx",
        "dataset_name": "Recorded offences - Year ending Mar 2026",
        "catalogue_url": "https://discover.data.vic.gov.au/dataset/data-tables-recorded-offences",
        "publisher": "Crime Statistics Agency (Victoria)",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Year ending March 2017 to year ending March 2026",
        "publication_date": "2026-06-19",
    },
    "geographic_classification": {
        "filename": "Geographic classification.xlsx",
        "dataset_name": "CSA Geographical Area Hierarchy",
        "catalogue_url": "https://www.crimestatistics.vic.gov.au/about-the-data/classifications",
        "publisher": "Crime Statistics Agency (Victoria)",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Current CSA geography hierarchy",
        "publication_date": None,
    },
    "statewide_criminal_incidents": {
        "filename": "Data_Tables_Criminal_Incidents_Visualisation_Year_Ending_March_2026.xlsx",
        "dataset_name": "Criminal incidents - Year ending Mar 2026",
        "catalogue_url": "https://discover.data.vic.gov.au/dataset/criminal-incident",
        "publisher": "Crime Statistics Agency (Victoria)",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Year ending March 2017 to year ending March 2026",
        "publication_date": "2026-06-19",
        "download_url": "https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Criminal_Incidents_Visualisation_Year_Ending_March_2026.xlsx",
    },
    "lga_criminal_incidents": {
        "filename": "Data_Tables_LGA_Criminal_Incidents_Year_Ending_March_2026.xlsx",
        "dataset_name": "Criminal incident by LGA - Year Ending Mar 2026",
        "catalogue_url": "https://discover.data.vic.gov.au/dataset/criminal-incident",
        "publisher": "Crime Statistics Agency (Victoria)",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Year ending March 2017 to year ending March 2026",
        "publication_date": "2026-06-19",
        "download_url": "https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Criminal_Incidents_Year_Ending_March_2026.xlsx",
    },
    "statewide_alleged_offenders": {
        "filename": "Data_Tables_Alleged_Offender_Incidents_Visualisation_Year_Ending_March_2026.xlsx",
        "dataset_name": "Alleged offender incidents - Year ending Mar 2026",
        "catalogue_url": "https://discover.data.vic.gov.au/dataset/data-tables-alleged-offender-incidents",
        "publisher": "Crime Statistics Agency (Victoria)",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Year ending March 2017 to year ending March 2026",
        "publication_date": "2026-06-19",
        "download_url": "https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Alleged_Offender_Incidents_Visualisation_Year_Ending_March_2026.xlsx",
    },
    "lga_alleged_offenders": {
        "filename": "Data_Tables_LGA_Alleged_Offenders_Year_Ending_March_2026.xlsx",
        "dataset_name": "Alleged offender incidents by LGA - Year Ending Mar 2026",
        "catalogue_url": "https://discover.data.vic.gov.au/dataset/data-tables-alleged-offender-incidents",
        "publisher": "Crime Statistics Agency (Victoria)",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Year ending March 2017 to year ending March 2026",
        "publication_date": "2026-06-19",
        "download_url": "https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Alleged_Offenders_Year_Ending_March_2026.xlsx",
    },
    "abs_offenders_australia": {
        "filename": "ABS_Offenders_Australia_2024-25.xlsx",
        "dataset_name": "Recorded Crime – Offenders, 2024–25, Offenders, Australia",
        "catalogue_url": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/latest-release",
        "publisher": "Australian Bureau of Statistics",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Financial years 2008–09 to 2024–25",
        "publication_date": "2026-03-18",
        "download_url": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/1.%20Offenders%2C%20Australia.xlsx",
    },
    "abs_offenders_states": {
        "filename": "ABS_Offenders_States_2024-25.xlsx",
        "dataset_name": "Recorded Crime – Offenders, 2024–25, Offenders, states and territories",
        "catalogue_url": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/latest-release",
        "publisher": "Australian Bureau of Statistics",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Financial years 2008–09 to 2024–25",
        "publication_date": "2026-03-18",
        "download_url": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/2.%20Offenders%2C%20states%20and%20territories.xlsx",
    },
    "abs_youth_offenders": {
        "filename": "ABS_Youth_Offenders_2024-25.xlsx",
        "dataset_name": "Recorded Crime – Offenders, 2024–25, Youth offenders",
        "catalogue_url": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/latest-release",
        "publisher": "Australian Bureau of Statistics",
        "licence": "Creative Commons Attribution 4.0 International",
        "reporting_period": "Financial years 2008–09 to 2024–25",
        "publication_date": "2026-03-18",
        "download_url": "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/3.%20Youth%20offenders.xlsx",
    },
}

ABS_STATISTICAL_PRODUCT = (
    "ABS Recorded Crime – Offenders counts unique alleged offenders proceeded "
    "against during a financial year (July–June). Rates are per 100,000 persons "
    "aged 10 years and over. This is not comparable to CSA alleged offender "
    "incidents (year ending March), which count incidents rather than unique people."
)

YOUTH_AGE_GROUPS = {
    "10-11 years",
    "12-14 years",
    "15-17 years",
    "10 - 17 years",
    "10-17 years",
}

# Greater Melbourne LGAs that sit inside the Eastern police region.
EASTERN_METRO_LGAS = {
    "Boroondara",
    "Manningham",
    "Monash",
    "Whitehorse",
    "Knox",
    "Maroondah",
    "Yarra Ranges",
}

# Colour palette for government-style charts.
PALETTE = {
    "navy": "#1B365D",
    "teal": "#2A6F7F",
    "slate": "#5B6B7A",
    "gold": "#C4A35A",
    "rust": "#A15C38",
    "green": "#3E6B4F",
    "grey": "#D6D9DE",
    "light": "#F4F6F8",
}

DIVISION_COLOURS = {
    "A Crimes against the person": "#A15C38",
    "B Property and deception offences": "#1B365D",
    "C Drug offences": "#2A6F7F",
    "D Public order and security offences": "#3E6B4F",
    "E Justice procedures offences": "#C4A35A",
    "F Other offences": "#5B6B7A",
}


def source_path(key: str) -> Path:
    """Return the absolute path of a downloaded source workbook."""
    filename = SOURCE_FILES[key]["filename"]
    candidate = WORKSPACE_ROOT / filename
    if candidate.exists():
        return candidate
    raw_copy = DATA_RAW / filename
    if raw_copy.exists():
        return raw_copy
    raise FileNotFoundError(f"Source file not found for {key}: {filename}")


def ensure_output_dirs() -> None:
    """Create processed, export and figure directories if missing."""
    for path in (
        DATA_RAW,
        DATA_PROCESSED,
        DATA_EXPORTS,
        FIGURES_DIR,
        REPORTS_DIR,
        DASHBOARD_DIR,
        DASHBOARD_DIR / "data",
        LOGS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
