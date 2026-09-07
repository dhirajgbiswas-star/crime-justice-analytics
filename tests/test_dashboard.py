"""Tests for Tableau / public dashboard extracts."""

from src.dashboard.mart import build_tableau_mart, dashboard_payload


def test_tableau_mart_keeps_products_separate():
    mart = build_tableau_mart()
    products = set(
        mart.loc[mart["Dataset"] == "Statewide products", "Statistical Product"].unique()
    )
    assert products == {
        "Recorded offences",
        "Criminal incidents",
        "Alleged offender incidents",
    }
    latest = mart[
        (mart["Dataset"] == "Statewide products")
        & (mart["Statistical Product"] == "Recorded offences")
        & (mart["Year"] == 2026)
    ]
    assert abs(latest["Count"].sum() - 625426) < 1


def test_dashboard_payload_has_tabs():
    payload = dashboard_payload()
    assert payload["meta"]["latestYear"] == 2026
    assert payload["qualityScores"]["overall"] == 100.0
    assert payload["offences"][-1]["offence_count"] == 625426
    assert payload["absCompare"]["victoria_offenders"] == 59693
    assert payload["absCompare"]["australia_offenders"] == 344620
    assert payload["absProductNote"]["comparable"] == 0
    assert "ABS Recorded Crime" in payload["meta"]["catalogue"][-1]["name"]


def test_tableau_mart_keeps_abs_separate():
    mart = build_tableau_mart()
    statewide = set(
        mart.loc[mart["Dataset"] == "Statewide products", "Statistical Product"].unique()
    )
    assert "ABS unique offenders" not in statewide
    abs_states = mart[mart["Dataset"] == "ABS state totals"]
    victoria = abs_states[abs_states["Jurisdiction"] == "Victoria"]
    assert abs(victoria["Count"].sum() - 59693) < 1
    assert abs(victoria["Rate per 100000"].mean() - 961.6) < 0.05
