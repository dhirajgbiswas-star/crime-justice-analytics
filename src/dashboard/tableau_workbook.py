"""Build a Tableau Desktop 2026.2 / Tableau Public workbook."""

from __future__ import annotations

from pathlib import Path

from src.config import DASHBOARD_DIR, DIVISION_COLOURS, PALETTE, ensure_output_dirs

NAVY = PALETTE["navy"]
TEAL = PALETTE["teal"]
GOLD = PALETTE["gold"]
RUST = PALETTE["rust"]
SLATE = PALETTE["slate"]
NAVY_DEEP = "#0E2140"
PAPER = "#F3EEE4"
CARD = "#FFFDF8"
LINE = "#E4D8C6"
MUTED = "#6D7784"

DASH_OVERVIEW = "Victorian Crime Overview"
DASH_GEO = "Geographic Intelligence"
DASH_OFFENDERS = "Offenders and Justice"
DASH_NATIONAL = "National Comparison"
DASH_QUALITY = "Data Quality"

CARD_STYLE = {
    "background-color": CARD,
    "border-color": LINE,
    "border-style": "solid",
    "border-width": "1",
}
KPI_STYLE = {
    "background-color": CARD,
    "border-color": GOLD,
    "border-style": "solid",
    "border-width": "2",
}

CSV_FIELDS = [
    {"name": "Dataset", "datatype": "string", "role": "dimension"},
    {"name": "Year", "datatype": "integer", "role": "dimension"},
    {"name": "Statistical Product", "datatype": "string", "role": "dimension"},
    {"name": "Country", "datatype": "string", "role": "dimension"},
    {"name": "State", "datatype": "string", "role": "dimension"},
    {"name": "Local Government Area", "datatype": "string", "role": "dimension"},
    {"name": "Police Region", "datatype": "string", "role": "dimension"},
    {"name": "Metro Regional", "datatype": "string", "role": "dimension"},
    {"name": "Offence Division", "datatype": "string", "role": "dimension"},
    {"name": "Offence Subdivision", "datatype": "string", "role": "dimension"},
    {"name": "Offence Subgroup", "datatype": "string", "role": "dimension"},
    {"name": "Sex", "datatype": "string", "role": "dimension"},
    {"name": "Age Group", "datatype": "string", "role": "dimension"},
    {"name": "Charge Status", "datatype": "string", "role": "dimension"},
    {"name": "Investigation Status", "datatype": "string", "role": "dimension"},
    {"name": "Family Incident Flag", "datatype": "string", "role": "dimension"},
    {"name": "Age Band", "datatype": "string", "role": "dimension"},
    {"name": "Table Name", "datatype": "string", "role": "dimension"},
    {"name": "Jurisdiction", "datatype": "string", "role": "dimension"},
    {"name": "Financial Year", "datatype": "string", "role": "dimension"},
    {"name": "Latitude", "datatype": "real", "role": "measure"},
    {"name": "Longitude", "datatype": "real", "role": "measure"},
    {"name": "Count", "datatype": "real", "role": "measure"},
    {"name": "Rate per 100000", "datatype": "real", "role": "measure"},
    {"name": "Share %", "datatype": "real", "role": "measure"},
    {"name": "YoY %", "datatype": "real", "role": "measure"},
    {"name": "YoY Count", "datatype": "real", "role": "measure"},
    {"name": "Quality Score", "datatype": "real", "role": "measure"},
]


def _text(runs: list[dict], height: int, background: str) -> dict:
    return {"type": "text", "fixed_size": height, "style": {"background-color": background}, "runs": runs}


def _header(active: str) -> list[dict]:
    tab_runs = []
    for label, target in (
        ("Overview", DASH_OVERVIEW),
        ("Geography", DASH_GEO),
        ("Offenders", DASH_OFFENDERS),
        ("National", DASH_NATIONAL),
        ("Quality", DASH_QUALITY),
    ):
        is_active = target == active
        tab_runs.append(
            {
                "text": f"   {label}   ",
                "bold": True,
                "font_size": "12",
                "font_color": GOLD if is_active else "#C9D3DE",
            }
        )
    return [
        _text(
            [
                {
                    "text": "  CRIME STATISTICS AGENCY  ·  VICTORIA  ·  OPEN DATA",
                    "bold": True,
                    "font_size": "10",
                    "font_color": GOLD,
                }
            ],
            22,
            NAVY_DEEP,
        ),
        _text(
            [
                    {"text": "  Crime & Justice Intelligence", "bold": True, "font_size": "22", "font_color": "#FFFFFF"},
                {
                    "text": "     CSA year ending March 2017–2026  ·  ABS offenders 2024–25",
                    "font_size": "12",
                    "font_color": "#C9D3DE",
                },
            ],
            46,
            NAVY,
        ),
        _text([{"text": " ", "font_size": "4", "font_color": GOLD}], 4, GOLD),
        {
            "type": "container",
            "direction": "horizontal",
            "fixed_size": 40,
            "style": {"background-color": NAVY},
            "children": [
                _text(tab_runs, 40, NAVY),
                {"type": "empty", "weight": 1, "style": {"background-color": NAVY}},
                {
                    "type": "paramctrl",
                    "parameter": "Year ending March",
                    "fixed_size": 220,
                    "style": {"background-color": NAVY},
                },
            ],
        },
    ]


def _footer() -> dict:
    return _text(
        [
            {
                "text": "  Source: CSA (Victoria) and ABS Recorded Crime – Offenders, CC BY 4.0.  CSA offences, incidents and alleged offender incidents are different products.  ABS unique offenders (financial year) must not be compared with CSA alleged offender incidents.",
                "font_size": "10",
                "font_color": MUTED,
            }
        ],
        30,
        PAPER,
    )


def _card(name: str, **kwargs) -> dict:
    node = {"type": "worksheet", "name": name, "show_title": True, "style": CARD_STYLE, "fit": "entire"}
    node.update(kwargs)
    return node


def _kpi_card(name: str) -> dict:
    return {"type": "worksheet", "name": name, "show_title": True, "style": KPI_STYLE, "fit": "entire"}


def _filter_dataset(*values: str) -> list[dict]:
    return [{"column": "Dataset", "values": list(values), "context": True}]


def write_tableau_workbook(csv_path: Path, output_dir: Path | None = None) -> dict[str, Path]:
    from cwtwb.twb_editor import TWBEditor

    ensure_output_dirs()
    folder = Path(output_dir) if output_dir else DASHBOARD_DIR
    folder.mkdir(parents=True, exist_ok=True)
    twb_path = folder / "Victorian_Crime_Justice.twb"
    twbx_path = folder / "Victorian_Crime_Justice.twbx"

    editor = TWBEditor("")
    editor.clear_worksheets()
    editor.set_csv_connection(str(csv_path.resolve()), fields=CSV_FIELDS)

    editor.add_parameter(
        "Year ending March",
        datatype="integer",
        default_value="2026",
        domain_type="list",
        allowed_values=[str(year) for year in range(2017, 2027)],
    )
    editor.add_calculated_field(
        "Selected Count",
        "IF [Year] = [Year ending March] THEN [Count] END",
        datatype="real",
        default_format="#,##0",
    )
    editor.add_calculated_field(
        "Selected Rate",
        "IF [Year] = [Year ending March] THEN [Rate per 100000] END",
        datatype="real",
        default_format="#,##0.0",
    )
    editor.add_calculated_field(
        "Selected YoY %",
        "IF [Year] = [Year ending March] THEN [YoY %] END",
        datatype="real",
        default_format="0.0",
    )

    editor.set_datasource_color_palette(
        "Statistical Product",
        {
            "Recorded offences": NAVY,
            "Criminal incidents": TEAL,
            "Alleged offender incidents": RUST,
            "ABS unique offenders": GOLD,
        },
    )
    editor.set_datasource_color_palette("Offence Division", DIVISION_COLOURS)
    editor.set_datasource_color_palette("Metro Regional", {"Metropolitan": NAVY, "Regional": GOLD})
    editor.set_datasource_color_palette("Sex", {"Males": NAVY, "Females": TEAL})
    editor.set_datasource_color_palette(
        "Charge Status",
        {"Unsolved": GOLD, "Charges laid": TEAL, "No charges laid": NAVY},
    )
    editor.set_datasource_color_palette("Age Band", {"Adult (18+)": NAVY, "Youth (10-17)": GOLD})
    editor.set_datasource_color_palette(
        "Family Incident Flag",
        {"Family incident related": RUST, "Not family incident related": NAVY},
    )
    editor.set_datasource_color_palette(
        "Jurisdiction",
        {
            "Victoria": GOLD,
            "Australia": NAVY,
            "New South Wales": TEAL,
            "Queensland": SLATE,
            "South Australia": RUST,
            "Western Australia": "#3E6B4F",
            "Tasmania": MUTED,
            "Northern Territory": "#8B3A3A",
            "Australian Capital Territory": "#7A8B99",
        },
    )

    def style_chart(name: str, *, pie: bool = False) -> None:
        editor.configure_worksheet_style(
            name,
            background_color=CARD,
            hide_band_color=True,
            hide_gridlines=False,
            hide_zeroline=True,
            hide_borders=True,
            hide_col_field_labels=True,
            hide_row_field_labels=True,
            hide_axes=pie,
            header_formats=[{"color": MUTED, "font-size": "10"}],
        )

    def rich_title(name: str, title: str, note: str = "") -> None:
        runs = [{"text": title, "bold": True, "fontsize": "13", "fontcolor": NAVY}]
        if note:
            runs.append({"text": f"    {note}", "fontsize": "10", "fontcolor": MUTED})
        editor.set_worksheet_rich_title(name, runs)

    def sheet(name: str, title: str, note: str = "", pie: bool = False, **chart) -> None:
        editor.add_worksheet(name)
        editor.configure_chart(name, **chart)
        style_chart(name, pie=pie)
        rich_title(name, title, note)

    def kpi(name: str, title: str, measure: str, dataset: str, product: str | None = None, number_format: str = "#,##0") -> None:
        filters = _filter_dataset(dataset)
        if product:
            filters.append({"column": "Statistical Product", "values": [product]})
        field = measure.replace("SUM(", "").replace("AVG(", "").replace(")", "")
        editor.add_worksheet(name)
        editor.configure_chart(
            name,
            mark_type="Text",
            label=measure,
            filters=filters,
            text_format={field: number_format},
        )
        editor.configure_worksheet_style(
            name,
            background_color=CARD,
            hide_axes=True,
            hide_gridlines=True,
            hide_borders=True,
            hide_band_color=True,
            hide_col_field_labels=True,
            hide_row_field_labels=True,
            pane_datalabel_style={
                "font-size": "28",
                "color": NAVY,
                "font-weight": "bold",
                "text-align": "center",
            },
        )
        rich_title(name, title, "Year ending March <[Year ending March]>")

    def kpi_abs(
        name: str,
        title: str,
        measure: str,
        dataset: str,
        jurisdiction: str,
        number_format: str = "#,##0",
    ) -> None:
        field = measure.replace("SUM(", "").replace("AVG(", "").replace(")", "")
        editor.add_worksheet(name)
        editor.configure_chart(
            name,
            mark_type="Text",
            label=measure,
            filters=_filter_dataset(dataset)
            + [{"column": "Jurisdiction", "values": [jurisdiction]}],
            text_format={field: number_format},
        )
        editor.configure_worksheet_style(
            name,
            background_color=CARD,
            hide_axes=True,
            hide_gridlines=True,
            hide_borders=True,
            hide_band_color=True,
            hide_col_field_labels=True,
            hide_row_field_labels=True,
            pane_datalabel_style={
                "font-size": "28",
                "color": NAVY,
                "font-weight": "bold",
                "text-align": "center",
            },
        )
        rich_title(name, title, "ABS financial year 2024–25")

    kpi("KPI Recorded Offences", "Recorded offences", "SUM(Selected Count)", "Statewide products", "Recorded offences")
    kpi("KPI Criminal Incidents", "Criminal incidents", "SUM(Selected Count)", "Statewide products", "Criminal incidents")
    kpi("KPI Alleged Offenders", "Alleged offenders", "SUM(Selected Count)", "Statewide products", "Alleged offender incidents")
    kpi("KPI Offence Rate", "Rate per 100,000", "AVG(Selected Rate)", "Statewide products", "Recorded offences", "#,##0.0")
    kpi("KPI Data Quality", "Loaded-table score", "AVG(Quality Score)", "Data quality", None, "0.0")

    editor.add_worksheet("Statewide Trend")
    editor.configure_dual_axis(
        "Statewide Trend",
        mark_type_1="Line",
        mark_type_2="Line",
        columns=["Year"],
        rows=["SUM(Count)", "AVG(Rate per 100000)"],
        synchronized=False,
        filters=_filter_dataset("Statewide products")
        + [{"column": "Statistical Product", "values": ["Recorded offences"]}],
        mark_color_1=NAVY,
        mark_color_2=TEAL,
        show_labels=False,
    )
    style_chart("Statewide Trend")
    rich_title("Statewide Trend", "Statewide recorded offences", "Count and rate per 100,000")

    sheet(
        "Three Products",
        "Three official products",
        "Do not add these series together",
        mark_type="Line",
        columns=["Year"],
        rows=["SUM(Count)"],
        color="Statistical Product",
        filters=_filter_dataset("Statewide products"),
        tooltip=["Statistical Product", "SUM(Count)", "AVG(Rate per 100000)"],
    )
    sheet(
        "YoY Change",
        "Year-on-year change",
        "Recorded offences",
        mark_type="Bar",
        columns=["Year"],
        rows=["AVG(YoY %)"],
        filters=_filter_dataset("Statewide products")
        + [{"column": "Statistical Product", "values": ["Recorded offences"]}],
        tooltip=["Year", "AVG(YoY %)", "SUM(Count)"],
    )
    sheet(
        "Offence Mix",
        "Offence composition",
        "Selected year",
        mark_type="Bar",
        rows=["Offence Division"],
        columns=["SUM(Selected Count)"],
        color="Offence Division",
        sort_descending="SUM(Selected Count)",
        filters=_filter_dataset("Recorded offence divisions"),
        tooltip=["Offence Division", "SUM(Selected Count)"],
    )
    sheet(
        "Investigation Status",
        "Investigation status",
        "Selected year",
        mark_type="Bar",
        rows=["Investigation Status"],
        columns=["SUM(Selected Count)"],
        sort_descending="SUM(Selected Count)",
        filters=_filter_dataset("Investigation status"),
        tooltip=["Investigation Status", "SUM(Selected Count)"],
    )
    sheet(
        "Family Incident Flag",
        "Family-incident related offences",
        "Flag available from 2021",
        mark_type="Bar",
        columns=["Year"],
        rows=["SUM(Count)"],
        color="Family Incident Flag",
        filters=_filter_dataset("Family incident offences"),
    )
    sheet(
        "Highest LGA Rates",
        "Highest LGA rates",
        "Use rates to compare places",
        mark_type="Bar",
        rows=["Local Government Area"],
        columns=["AVG(Selected Rate)"],
        color="Metro Regional",
        sort_descending="AVG(Selected Rate)",
        filters=_filter_dataset("LGA recorded offences")
        + [{"column": "Local Government Area", "top": 12, "by": "AVG(Selected Rate)"}],
        tooltip=["Local Government Area", "AVG(Selected Rate)", "SUM(Selected Count)", "Metro Regional"],
    )
    sheet(
        "Highest LGA Counts",
        "Highest LGA counts",
        "Melbourne is an activity centre",
        mark_type="Bar",
        rows=["Local Government Area"],
        columns=["SUM(Selected Count)"],
        color="Metro Regional",
        sort_descending="SUM(Selected Count)",
        filters=_filter_dataset("LGA recorded offences")
        + [{"column": "Local Government Area", "top": 12, "by": "SUM(Selected Count)"}],
        tooltip=["Local Government Area", "SUM(Selected Count)", "AVG(Selected Rate)"],
    )
    sheet(
        "Count versus Rate",
        "Count versus rate",
        "Navy metropolitan  ·  gold regional",
        mark_type="Circle",
        columns=["SUM(Selected Count)"],
        rows=["AVG(Selected Rate)"],
        color="Metro Regional",
        detail="Local Government Area",
        size="SUM(Selected Count)",
        filters=_filter_dataset("LGA recorded offences"),
        tooltip=["Local Government Area", "SUM(Selected Count)", "AVG(Selected Rate)", "Metro Regional"],
    )
    sheet(
        "Metro and Regional",
        "Metropolitan and regional",
        "Analytical grouping, not official CSA geography",
        mark_type="Line",
        columns=["Year"],
        rows=["SUM(Count)"],
        color="Metro Regional",
        filters=_filter_dataset("Metro regional recorded offences"),
    )
    sheet(
        "LGA Symbol Map",
        "Victorian LGA map",
        "Symbol size = offences  ·  colour = rate",
        mark_type="Circle",
        columns=["AVG(Longitude)"],
        rows=["AVG(Latitude)"],
        color="AVG(Selected Rate)",
        size="SUM(Selected Count)",
        detail="Local Government Area",
        filters=_filter_dataset("LGA recorded offences"),
        tooltip=["Local Government Area", "SUM(Selected Count)", "AVG(Selected Rate)", "Metro Regional"],
    )
    sheet(
        "Largest LGA Increases",
        "Largest year-on-year LGA changes",
        "Selected year versus previous year",
        mark_type="Bar",
        rows=["Local Government Area"],
        columns=["AVG(Selected YoY %)"],
        sort_descending="AVG(Selected YoY %)",
        filters=_filter_dataset("LGA YoY recorded offences")
        + [{"column": "Local Government Area", "top": 12, "by": "AVG(Selected YoY %)"}],
        tooltip=["Local Government Area", "AVG(Selected YoY %)", "SUM(Selected Count)"],
    )
    sheet(
        "Alleged Offender Trend",
        "Alleged offender incidents",
        "Not unique people and not findings of guilt",
        mark_type="Line",
        columns=["Year"],
        rows=["SUM(Count)"],
        filters=_filter_dataset("Statewide products")
        + [{"column": "Statistical Product", "values": ["Alleged offender incidents"]}],
    )
    sheet(
        "Youth versus Adult",
        "Youth versus adult",
        "Youth is CSA ages 10–17",
        mark_type="Line",
        columns=["Year"],
        rows=["SUM(Count)"],
        color="Age Band",
        filters=_filter_dataset("Youth vs adult"),
    )
    sheet(
        "Known Sex",
        "Known sex",
        "Males and females only",
        pie=True,
        mark_type="Pie",
        color="Sex",
        wedge_size="SUM(Selected Count)",
        filters=_filter_dataset("Alleged offender age-sex"),
        tooltip=["Sex", "SUM(Selected Count)"],
    )
    sheet(
        "Age Groups",
        "Age group",
        "Selected year",
        mark_type="Bar",
        rows=["Age Group"],
        columns=["SUM(Selected Count)"],
        color="Sex",
        filters=_filter_dataset("Alleged offender age-sex"),
    )
    sheet(
        "Youth Single Year",
        "Youth single year of age",
        "Ages 10–17",
        mark_type="Bar",
        columns=["Age Group"],
        rows=["SUM(Selected Count)"],
        color="Sex",
        filters=_filter_dataset("Youth single year of age"),
    )
    sheet(
        "Principal Offence",
        "Principal alleged-offender offence",
        "Top 10 in selected year",
        mark_type="Bar",
        rows=["Offence Subdivision"],
        columns=["SUM(Selected Count)"],
        sort_descending="SUM(Selected Count)",
        filters=_filter_dataset("Principal alleged offender offence")
        + [{"column": "Offence Subdivision", "top": 10, "by": "SUM(Selected Count)"}],
    )
    sheet(
        "Charge Status",
        "Criminal incident charge status",
        "Incidents, not offences",
        pie=True,
        mark_type="Pie",
        color="Charge Status",
        wedge_size="SUM(Selected Count)",
        filters=_filter_dataset("Charge status"),
        tooltip=["Charge Status", "SUM(Selected Count)", "AVG(Share %)"],
    )
    sheet(
        "Highest Offender Rates",
        "Highest alleged-offender rates",
        "Latrobe leads rate, not Melbourne",
        mark_type="Bar",
        rows=["Local Government Area"],
        columns=["AVG(Selected Rate)"],
        sort_descending="AVG(Selected Rate)",
        filters=_filter_dataset("LGA alleged offender incidents")
        + [{"column": "Local Government Area", "top": 12, "by": "AVG(Selected Rate)"}],
        tooltip=["Local Government Area", "AVG(Selected Rate)", "SUM(Selected Count)"],
    )
    sheet(
        "Quality Tables",
        "Loaded CSA and ABS tables",
        "Missing values, negatives and duplicate keys",
        mark_type="Bar",
        rows=["Table Name"],
        columns=["SUM(Count)"],
        label="AVG(Quality Score)",
        filters=_filter_dataset("Data quality"),
    )
    kpi_abs(
        "KPI ABS Vic Offenders",
        "ABS Victoria offenders",
        "SUM(Count)",
        "ABS state totals",
        "Victoria",
    )
    kpi_abs(
        "KPI ABS Vic Rate",
        "ABS Victoria rate",
        "AVG(Rate per 100000)",
        "ABS state totals",
        "Victoria",
        "#,##0.0",
    )
    kpi_abs(
        "KPI ABS Aus Rate",
        "ABS Australia rate",
        "AVG(Rate per 100000)",
        "ABS state totals",
        "Australia",
        "#,##0.0",
    )
    kpi_abs(
        "KPI ABS Vic Youth",
        "ABS Victoria youth 10–17",
        "SUM(Count)",
        "ABS youth by state",
        "Victoria",
    )
    sheet(
        "ABS State Rates",
        "ABS offender rates by jurisdiction",
        "Unique offenders proceeded against  ·  not CSA incidents",
        mark_type="Bar",
        rows=["Jurisdiction"],
        columns=["AVG(Rate per 100000)"],
        color="Jurisdiction",
        sort_descending="AVG(Rate per 100000)",
        filters=_filter_dataset("ABS state totals"),
        tooltip=["Jurisdiction", "SUM(Count)", "AVG(Rate per 100000)", "Financial Year"],
    )
    sheet(
        "ABS Vic Australia Rate",
        "ABS offender rates: Victoria and Australia",
        "Financial years 2008–09 to 2024–25",
        mark_type="Line",
        columns=["Year"],
        rows=["AVG(Rate per 100000)"],
        color="Jurisdiction",
        filters=_filter_dataset("ABS Victoria Australia trend"),
        tooltip=["Jurisdiction", "Financial Year", "SUM(Count)", "AVG(Rate per 100000)"],
    )
    sheet(
        "ABS Vic Principal Offence",
        "ABS Victoria principal offence",
        "ANZSOC divisions, 2024–25",
        mark_type="Bar",
        rows=["Offence Division"],
        columns=["SUM(Count)"],
        sort_descending="SUM(Count)",
        filters=_filter_dataset("ABS Victoria principal offence"),
        tooltip=["Offence Division", "SUM(Count)", "AVG(Rate per 100000)"],
    )
    sheet(
        "ABS Youth by State",
        "ABS youth offenders by jurisdiction",
        "Persons aged 10–17, 2024–25",
        mark_type="Bar",
        rows=["Jurisdiction"],
        columns=["SUM(Count)"],
        sort_descending="SUM(Count)",
        filters=_filter_dataset("ABS youth by state"),
        tooltip=["Jurisdiction", "SUM(Count)", "AVG(Rate per 100000)"],
    )
    sheet(
        "ABS Vic Youth Trend",
        "ABS Victoria youth offenders",
        "Persons aged 10–17 proceeded against",
        mark_type="Line",
        columns=["Year"],
        rows=["SUM(Count)"],
        filters=_filter_dataset("ABS Victoria youth trend"),
        tooltip=["Financial Year", "SUM(Count)", "AVG(Rate per 100000)"],
    )
    sheet(
        "ABS versus CSA",
        "Do not compare these two numbers",
        "Different products, periods and units",
        mark_type="Bar",
        rows=["Table Name"],
        columns=["SUM(Count)"],
        color="Statistical Product",
        filters=_filter_dataset("ABS vs CSA note"),
        tooltip=["Table Name", "Statistical Product", "Financial Year", "SUM(Count)"],
    )

    overview = {
        "type": "container",
        "direction": "vertical",
        "style": {"background-color": PAPER},
        "children": [
            *_header(DASH_OVERVIEW),
            {
                "type": "container",
                "direction": "horizontal",
                "fixed_size": 108,
                "children": [
                    _kpi_card("KPI Recorded Offences"),
                    _kpi_card("KPI Offence Rate"),
                    _kpi_card("KPI Criminal Incidents"),
                    _kpi_card("KPI Alleged Offenders"),
                ],
            },
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1.35,
                "children": [
                    _card("Statewide Trend", weight=1.35),
                    _card("Three Products", weight=1),
                ],
            },
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1,
                "children": [
                    _card("YoY Change"),
                    _card("Offence Mix"),
                    _card("Investigation Status"),
                ],
            },
            _footer(),
        ],
    }
    geography = {
        "type": "container",
        "direction": "vertical",
        "style": {"background-color": PAPER},
        "children": [
            *_header(DASH_GEO),
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1.45,
                "children": [
                    _card("LGA Symbol Map", weight=1.25),
                    _card("Highest LGA Rates", weight=1),
                ],
            },
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1,
                "children": [
                    _card("Highest LGA Counts"),
                    _card("Count versus Rate"),
                    _card("Metro and Regional"),
                ],
            },
            _card("Largest LGA Increases", fixed_size=188),
            _footer(),
        ],
    }
    offenders = {
        "type": "container",
        "direction": "vertical",
        "style": {"background-color": PAPER},
        "children": [
            *_header(DASH_OFFENDERS),
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1.2,
                "children": [
                    _card("Alleged Offender Trend"),
                    _card("Youth versus Adult"),
                ],
            },
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1,
                "children": [
                    _card("Known Sex"),
                    _card("Age Groups"),
                    _card("Youth Single Year"),
                ],
            },
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1,
                "children": [
                    _card("Principal Offence"),
                    _card("Charge Status"),
                    _card("Highest Offender Rates"),
                ],
            },
            _footer(),
        ],
    }
    national = {
        "type": "container",
        "direction": "vertical",
        "style": {"background-color": PAPER},
        "children": [
            *_header(DASH_NATIONAL),
            {
                "type": "container",
                "direction": "horizontal",
                "fixed_size": 108,
                "children": [
                    _kpi_card("KPI ABS Vic Offenders"),
                    _kpi_card("KPI ABS Vic Rate"),
                    _kpi_card("KPI ABS Aus Rate"),
                    _kpi_card("KPI ABS Vic Youth"),
                ],
            },
            _text(
                [
                    {
                        "text": "  ABS unique alleged offenders proceeded against (financial year July–June) are not CSA alleged offender incidents (year ending March). Victoria 59,693 (2024–25) must not be ratioed with CSA 195,342 (2026).",
                        "font_size": "12",
                        "font_color": NAVY,
                    }
                ],
                36,
                "#F7F1E2",
            ),
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1.25,
                "children": [
                    _card("ABS State Rates", weight=1),
                    _card("ABS Vic Australia Rate", weight=1.15),
                ],
            },
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1,
                "children": [
                    _card("ABS Vic Principal Offence"),
                    _card("ABS Vic Youth Trend"),
                    _card("ABS Youth by State"),
                ],
            },
            _card("ABS versus CSA", fixed_size=150),
            _footer(),
        ],
    }
    quality = {
        "type": "container",
        "direction": "vertical",
        "style": {"background-color": PAPER},
        "children": [
            *_header(DASH_QUALITY),
            {
                "type": "container",
                "direction": "horizontal",
                "fixed_size": 140,
                "children": [
                    _kpi_card("KPI Data Quality") | {"fixed_size": 280},
                    _text(
                        [
                            {
                                "text": "  Scores describe loaded CSA and ABS tables: missing counts, negatives, duplicate business keys and year coverage. They do not describe police recording practice.",
                                "font_size": "13",
                                "font_color": NAVY,
                            },
                            {
                                "text": "  CSA published 19 June 2026.  ABS Recorded Crime – Offenders published 18 March 2026.  Licence CC BY 4.0.",
                                "font_size": "12",
                                "font_color": MUTED,
                            },
                        ],
                        140,
                        CARD,
                    ),
                ],
            },
            _card("Quality Tables", weight=1),
            _footer(),
        ],
    }

    editor.add_dashboard(DASH_OVERVIEW, worksheet_names=[], width=1600, height=980, layout=overview)
    editor.add_dashboard(DASH_GEO, worksheet_names=[], width=1600, height=980, layout=geography)
    editor.add_dashboard(DASH_OFFENDERS, worksheet_names=[], width=1600, height=980, layout=offenders)
    editor.add_dashboard(DASH_NATIONAL, worksheet_names=[], width=1600, height=980, layout=national)
    editor.add_dashboard(DASH_QUALITY, worksheet_names=[], width=1600, height=980, layout=quality)

    for source, target in (
        ("LGA Symbol Map", "Highest LGA Rates"),
        ("LGA Symbol Map", "Highest LGA Counts"),
        ("LGA Symbol Map", "Count versus Rate"),
        ("Highest LGA Rates", "Count versus Rate"),
    ):
        editor.add_dashboard_action(
            DASH_GEO,
            "highlight",
            source_sheet=source,
            target_sheet=target,
            fields=["Local Government Area"],
            event_type="on-select",
            caption=f"Highlight {target}",
        )

    for name in editor.list_worksheets():
        editor.set_worksheet_hidden(name, hidden=True)
    _polish_workbook(editor)

    editor.save(twb_path, validate=True)
    editor.save(twbx_path, validate=False)
    return {"twb": twb_path, "twbx": twbx_path}


def _polish_workbook(editor) -> None:
    """Apply Australian locale, dashboard paper, and title typography."""
    worksheets = editor.root.find("worksheets")
    if worksheets is not None:
        for worksheet in list(worksheets):
            if worksheet.get("name") == "Sheet 1":
                worksheets.remove(worksheet)
    windows = editor.root.find("windows")
    if windows is not None:
        for window in list(windows):
            if window.get("name") == "Sheet 1":
                windows.remove(window)
    for attribute in editor.root.xpath(".//attribute"):
        name = attribute.get("name")
        if name == "locale":
            attribute.text = '"en_AU"'
        elif name == "currency":
            attribute.text = '"$"'
        elif name == "collation":
            attribute.text = '"en_AU"'
    for columns in editor.root.xpath(".//columns[@locale]"):
        columns.set("locale", "en_AU")

    for dashboard in editor.root.xpath("./dashboards/dashboard"):
        style = dashboard.find("style")
        if style is None:
            style = editor.root.makeelement("style")
            dashboard.insert(0, style)
        rule = style.makeelement("style-rule")
        rule.set("element", "dashboard")
        fmt = rule.makeelement("format")
        fmt.set("attr", "background-color")
        fmt.set("value", PAPER)
        rule.append(fmt)
        style.append(rule)

    for run in editor.root.xpath(".//run"):
        if run.get("fontname"):
            continue
        if run.get("bold") == "true":
            run.set("fontname", "Tableau Bold")
        else:
            run.set("fontname", "Tableau Book")
