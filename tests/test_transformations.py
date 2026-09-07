"""Unit tests for Stage 1-2 analytics helpers."""

from src.analytics.descriptive import add_yoy
from src.ingestion.load_csa import classify_metro_regional
from src.ingestion.stage2 import add_youth_flag, _to_numeric_counts
from src.validation.quality_checks import _score
import pandas as pd


def test_crime_rate_non_negative():
    rates = pd.Series([0.0, 12.5, 23303.67])
    assert (rates >= 0).all()


def test_classify_metro():
    assert classify_metro_regional("1 North West Metro", "Brimbank") == "Metropolitan"
    assert classify_metro_regional("2 Eastern", "Boroondara") == "Metropolitan"
    assert classify_metro_regional("4 Western", "Ballarat") == "Regional"


def test_youth_flag():
    df = pd.DataFrame({"age_group": ["10-11 years", "30-34 years", "15"]})
    out = add_youth_flag(df)
    assert out.loc[0, "is_youth"] == 1
    assert out.loc[1, "is_youth"] == 0
    assert out.loc[2, "is_youth"] == 1


def test_yoy_and_quality_score():
    df = pd.DataFrame({"year": [2024, 2025, 2026], "offence_count": [100.0, 110.0, 99.0]})
    out = add_yoy(df, "offence_count")
    assert round(out.loc[1, "offence_count_yoy_pct"], 1) == 10.0
    assert _score(120) == 100.0
    assert _score(-5) == 0.0


def test_numeric_prep_required_columns():
    raw = pd.DataFrame({"Year": [2026], "Incidents Recorded": ["10"]})
    raw.columns = ["year", "incidents_recorded"]
    out = _to_numeric_counts(raw)
    assert "year" in out.columns
    assert "incidents_recorded" in out.columns
    assert out["incidents_recorded"].iloc[0] == 10
