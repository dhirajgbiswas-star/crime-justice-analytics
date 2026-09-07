"""Python visualisations for Victorian recorded-offence analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.analytics.descriptive import (
    add_yoy,
    family_incident_share,
    investigation_status_trends,
    latest_lga_snapshot,
    lga_yoy_change,
    metro_regional_trends,
    offence_composition_by_lga,
    offence_division_trends,
    offence_subdivision_change,
    statewide_annual_totals,
    top_subgroups,
)
from src.analytics.incidents import (
    charge_status_share,
    statewide_incident_totals,
    statistical_product_comparison,
)
from src.analytics.national import (
    abs_australia_trend,
    abs_principal_offence_latest,
    abs_state_totals_latest,
    abs_victoria_persons_trend,
    abs_victoria_youth_trend,
    abs_youth_by_state_latest,
)
from src.analytics.offender import (
    age_sex_distribution,
    sex_distribution,
    statewide_offender_totals,
    youth_single_year_of_age,
    youth_vs_adult,
)
from src.config import DIVISION_COLOURS, FIGURES_DIR, PALETTE, ensure_output_dirs

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": PALETTE["grey"],
        "axes.labelcolor": PALETTE["navy"],
        "xtick.color": PALETTE["slate"],
        "ytick.color": PALETTE["slate"],
        "text.color": PALETTE["navy"],
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "legend.frameon": False,
        "axes.grid": True,
        "grid.color": PALETTE["grey"],
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def _save(fig: plt.Figure, name: str) -> Path:
    ensure_output_dirs()
    path = FIGURES_DIR / name
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_statewide_trend() -> Path:
    df = add_yoy(statewide_annual_totals(), "offence_count")
    fig, ax1 = plt.subplots(figsize=(10, 5.2))
    ax1.plot(
        df["year"],
        df["offence_count"] / 1000,
        color=PALETTE["navy"],
        marker="o",
        linewidth=2.2,
        label="Recorded offences (thousands)",
    )
    ax1.set_xlabel("Year ending March")
    ax1.set_ylabel("Recorded offences (thousands)")
    ax2 = ax1.twinx()
    ax2.plot(
        df["year"],
        df["rate_per_100000"],
        color=PALETTE["rust"],
        marker="s",
        linewidth=1.8,
        linestyle="--",
        label="Rate per 100,000",
    )
    ax2.set_ylabel("Rate per 100,000 population")
    ax2.grid(False)
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], loc="upper left")
    ax1.set_title("Victorian recorded offences, year ending March 2017–2026")
    fig.text(
        0.01,
        -0.04,
        "Source: Crime Statistics Agency, Recorded offences, year ending March 2026. "
        "Counts and rates are official CSA aggregates, not modelled estimates.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "01_statewide_trend.png")


def plot_yoy_change() -> Path:
    df = add_yoy(statewide_annual_totals(), "offence_count")
    df = df.dropna(subset=["offence_count_yoy_pct"])
    colours = [PALETTE["green"] if v < 0 else PALETTE["rust"] for v in df["offence_count_yoy_pct"]]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df["year"].astype(int).astype(str), df["offence_count_yoy_pct"], color=colours)
    ax.axhline(0, color=PALETTE["navy"], linewidth=0.8)
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Year-on-year change (%)")
    ax.set_title("Year-on-year change in Victorian recorded offences")
    fig.text(
        0.01,
        -0.04,
        "Source: CSA recorded offences. Percentage change is calculated from official annual totals.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "02_yoy_change.png")


def plot_division_trends() -> Path:
    df = offence_division_trends()
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    for division, group in df.groupby("offence_division"):
        ax.plot(
            group["year"],
            group["offence_count"] / 1000,
            marker="o",
            linewidth=2,
            label=division.split(" ", 1)[-1] if " " in division else division,
            color=DIVISION_COLOURS.get(division, PALETTE["slate"]),
        )
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Recorded offences (thousands)")
    ax.set_title("Recorded offences by CSA offence division")
    ax.legend(title="Offence division", loc="upper left", fontsize=8)
    fig.text(
        0.01,
        -0.06,
        "Source: CSA recorded offences visualisation Table 01. Division totals are sums of official subgroups.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "03_division_trends.png")


def plot_division_composition(year: int | None = None) -> Path:
    df = offence_division_trends()
    year = int(year or df["year"].max())
    latest = df[df["year"] == year].sort_values("offence_count", ascending=True)
    colours = [DIVISION_COLOURS.get(d, PALETTE["slate"]) for d in latest["offence_division"]]
    labels = [d.split(" ", 1)[-1] for d in latest["offence_division"]]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(labels, latest["offence_count"] / 1000, color=colours)
    ax.set_xlabel("Recorded offences (thousands)")
    ax.set_title(f"Offence composition, year ending March {year}")
    fig.text(
        0.01,
        -0.04,
        "Source: CSA recorded offences. These are recorded offences, not unique incidents or proven offences.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "04_division_composition.png")


def plot_fastest_changing_subdivisions(start_year: int = 2017, end_year: int = 2026) -> Path:
    df = offence_subdivision_change(start_year, end_year).dropna(subset=["change_pct"])
    df = df[df["start_count"] >= 1000]
    top = pd.concat([df.head(8), df.tail(8)]).drop_duplicates("offence_subdivision")
    top = top.sort_values("change_pct")
    colours = [PALETTE["green"] if v < 0 else PALETTE["rust"] for v in top["change_pct"]]
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.barh(top["offence_subdivision"], top["change_pct"], color=colours)
    ax.axvline(0, color=PALETTE["navy"], linewidth=0.8)
    ax.set_xlabel(f"Change in recorded offences, {start_year} to {end_year} (%)")
    ax.set_title("Largest long-term changes by offence subdivision")
    fig.text(
        0.01,
        -0.04,
        "Restricted to subdivisions with at least 1,000 offences in the start year to avoid unstable percentages.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "05_subdivision_change.png")


def plot_top_lga_counts() -> Path:
    df = latest_lga_snapshot().nlargest(15, "offence_count")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=df.sort_values("offence_count"),
        y="local_government_area",
        x="offence_count",
        hue="metro_regional",
        palette={"Metropolitan": PALETTE["navy"], "Regional": PALETTE["teal"]},
        dodge=False,
        ax=ax,
    )
    ax.set_xlabel("Recorded offences")
    ax.set_ylabel("Local government area")
    ax.set_title(f"LGAs with the highest offence counts, year ending March {int(df['year'].iloc[0])}")
    ax.legend(title="Geography")
    fig.text(
        0.01,
        -0.04,
        "Raw counts favour larger populations. Compare with crime-rate rankings before interpreting local risk.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "06_top_lga_counts.png")


def plot_top_lga_rates() -> Path:
    df = latest_lga_snapshot().nlargest(15, "rate_per_100000")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=df.sort_values("rate_per_100000"),
        y="local_government_area",
        x="rate_per_100000",
        hue="metro_regional",
        palette={"Metropolitan": PALETTE["navy"], "Regional": PALETTE["teal"]},
        dodge=False,
        ax=ax,
    )
    ax.set_xlabel("Rate per 100,000 population")
    ax.set_ylabel("Local government area")
    ax.set_title(f"LGAs with the highest crime rates, year ending March {int(df['year'].iloc[0])}")
    ax.legend(title="Geography")
    fig.text(
        0.01,
        -0.04,
        "CSA rates use ABS population estimates, with Victoria in Future estimates for the latest year.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "07_top_lga_rates.png")


def plot_lga_count_vs_rate() -> Path:
    df = latest_lga_snapshot()
    fig, ax = plt.subplots(figsize=(9.5, 6))
    for geo, group in df.groupby("metro_regional"):
        ax.scatter(
            group["offence_count"],
            group["rate_per_100000"],
            s=48,
            alpha=0.85,
            label=geo,
            color=PALETTE["navy"] if geo == "Metropolitan" else PALETTE["teal"],
        )
    melbourne = df[df["local_government_area"] == "Melbourne"]
    if not melbourne.empty:
        row = melbourne.iloc[0]
        ax.annotate(
            "Melbourne",
            (row["offence_count"], row["rate_per_100000"]),
            xytext=(10, 8),
            textcoords="offset points",
            fontsize=9,
        )
    ax.set_xlabel("Recorded offences (count)")
    ax.set_ylabel("Rate per 100,000 population")
    ax.set_title("LGA offence counts versus crime rates")
    ax.legend(title="Geography")
    fig.text(
        0.01,
        -0.04,
        "A high count can reflect population size or a high rate. Both measures are required for LGA comparison.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "08_count_vs_rate.png")


def plot_metro_regional() -> Path:
    df = metro_regional_trends()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    for geo, group in df.groupby("metro_regional"):
        colour = PALETTE["navy"] if geo == "Metropolitan" else PALETTE["teal"]
        axes[0].plot(group["year"], group["offence_count"] / 1000, marker="o", color=colour, label=geo)
        axes[1].plot(group["year"], group["avg_lga_rate_per_100000"], marker="o", color=colour, label=geo)
    axes[0].set_title("Total recorded offences")
    axes[0].set_ylabel("Offences (thousands)")
    axes[1].set_title("Average LGA crime rate")
    axes[1].set_ylabel("Average LGA rate per 100,000")
    for ax in axes:
        ax.set_xlabel("Year ending March")
        ax.legend()
    fig.suptitle("Metropolitan and regional Victorian recorded-offence patterns", fontweight="bold")
    fig.tight_layout()
    fig.text(
        0.01,
        -0.06,
        "Metropolitan includes police regions containing 'Metro' plus Eastern Greater Melbourne LGAs. "
        "Average LGA rate is unweighted and is not a population-weighted Victorian rate.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "09_metro_regional.png")


def plot_largest_lga_increases() -> Path:
    df = lga_yoy_change()
    latest_year = int(df["year"].max())
    latest = df[df["year"] == latest_year].nlargest(12, "yoy_pct")
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.barh(
        latest.sort_values("yoy_pct")["local_government_area"],
        latest.sort_values("yoy_pct")["yoy_pct"],
        color=PALETTE["rust"],
    )
    ax.set_xlabel(f"Year-on-year change to year ending March {latest_year} (%)")
    ax.set_title("LGAs with the largest year-on-year increases")
    fig.text(
        0.01,
        -0.04,
        "Percentage changes in smaller LGAs can be volatile. Interpret alongside counts and rates.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "10_lga_yoy_increases.png")


def plot_top_subgroups() -> Path:
    df = top_subgroups(n=12).sort_values("offence_count")
    fig, ax = plt.subplots(figsize=(10.5, 6))
    colours = [DIVISION_COLOURS.get(d, PALETTE["slate"]) for d in df["offence_division"]]
    ax.barh(df["offence_subgroup"], df["offence_count"], color=colours)
    ax.set_xlabel("Recorded offences")
    ax.set_title(f"Most common offence subgroups, year ending March {int(df['year'].iloc[0])}")
    fig.text(
        0.01,
        -0.04,
        "Source: CSA statewide recorded offences. Subgroup labels are official CSA offence classifications.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "11_top_subgroups.png")


def plot_investigation_status() -> Path:
    df = investigation_status_trends()
    pivot = df.pivot(index="year", columns="investigation_status", values="offence_count").fillna(0)
    share = pivot.div(pivot.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    share.plot(kind="area", stacked=True, ax=ax, colormap="tab20", alpha=0.9)
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Share of recorded offences (%)")
    ax.set_title("Investigation status of recorded offences")
    ax.legend(title="Investigation status", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    fig.text(
        0.01,
        -0.06,
        "Investigation status is an administrative outcome at extraction, not a court finding of guilt.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "12_investigation_status.png")


def plot_family_incident_share() -> Path:
    df = family_incident_share()
    pivot = df.pivot(index="year", columns="family_incident_flag", values="offence_count").fillna(0)
    fig, ax = plt.subplots(figsize=(9.5, 5))
    for col in pivot.columns:
        colour = PALETTE["rust"] if "Family" in col else PALETTE["navy"]
        ax.plot(pivot.index, pivot[col] / 1000, marker="o", linewidth=2, label=col, color=colour)
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Recorded offences (thousands)")
    ax.set_title("Family-incident related recorded offences")
    ax.legend()
    fig.text(
        0.01,
        -0.04,
        "Family-incident flag is available from 2021. This is a recorded-offence measure, not a unique-family-incident count.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "13_family_incidents.png")


def plot_lga_offence_heatmap() -> Path:
    df = offence_composition_by_lga()
    latest = latest_lga_snapshot().nlargest(12, "rate_per_100000")
    focus = df[df["local_government_area"].isin(latest["local_government_area"])]
    pivot = focus.pivot_table(
        index="local_government_area",
        columns="offence_division",
        values="offence_count",
        aggfunc="sum",
    ).fillna(0)
    share = pivot.div(pivot.sum(axis=1), axis=0) * 100
    share.columns = [c.split(" ", 1)[-1] for c in share.columns]
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(
        share,
        annot=True,
        fmt=".0f",
        cmap="Blues",
        ax=ax,
        cbar_kws={"label": "Share of LGA offences (%)"},
    )
    ax.set_xlabel("Offence division")
    ax.set_ylabel("Local government area")
    ax.set_title("Offence composition in highest-rate LGAs (%)")
    fig.text(
        0.01,
        -0.08,
        "Each row sums to 100% of that LGA's recorded offences in the latest year.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "14_lga_composition_heatmap.png")


def plot_rolling_average() -> Path:
    df = add_yoy(statewide_annual_totals(), "offence_count")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["year"], df["offence_count"] / 1000, color=PALETTE["grey"], linewidth=1.5, label="Annual total")
    ax.plot(
        df["year"],
        df["offence_count_3yr_avg"] / 1000,
        color=PALETTE["navy"],
        linewidth=2.4,
        marker="o",
        label="3-year rolling average",
    )
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Recorded offences (thousands)")
    ax.set_title("Long-term Victorian recorded-offence trend")
    ax.legend()
    fig.text(
        0.01,
        -0.04,
        "The 3-year average smooths short-term volatility and does not imply a forecast.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "15_rolling_average.png")


def plot_statistical_products() -> Path:
    df = statistical_product_comparison()
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.plot(df["year"], df["recorded_offences"] / 1000, marker="o", color=PALETTE["navy"], label="Recorded offences")
    ax.plot(df["year"], df["criminal_incidents"] / 1000, marker="s", color=PALETTE["teal"], label="Criminal incidents")
    ax.plot(
        df["year"],
        df["alleged_offender_incidents"] / 1000,
        marker="^",
        color=PALETTE["rust"],
        label="Alleged offender incidents",
    )
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Count (thousands)")
    ax.set_title("Three CSA statistical products, Victoria")
    ax.legend()
    fig.text(
        0.01,
        -0.06,
        "These measures are not interchangeable. One incident can generate multiple recorded offences. "
        "An alleged offender incident is not a finding of guilt.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "16_statistical_products.png")


def plot_incident_trend() -> Path:
    df = add_yoy(statewide_incident_totals(), "incident_count")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["year"], df["incident_count"] / 1000, marker="o", color=PALETTE["teal"], linewidth=2.2)
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Criminal incidents (thousands)")
    ax.set_title("Victorian criminal incidents")
    fig.text(
        0.01,
        -0.04,
        "Source: CSA criminal incidents visualisation Table 01 · year ending March 2017–2026",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "17_incident_trend.png")


def plot_charge_status() -> Path:
    df = charge_status_share()
    latest = df[df["year"] == df["year"].max()].sort_values("incident_count")
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.barh(latest["charge_status"], latest["share_pct"], color=PALETTE["navy"])
    ax.set_xlabel("Share of criminal incidents (%)")
    ax.set_title(f"Charge status, year ending March {int(latest['year'].iloc[0])}")
    fig.text(
        0.01,
        -0.04,
        "Charge status is an administrative outcome at extraction, not a court result.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "18_charge_status.png")


def plot_offender_trend() -> Path:
    df = add_yoy(statewide_offender_totals(), "alleged_offender_incidents")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        df["year"],
        df["alleged_offender_incidents"] / 1000,
        marker="o",
        color=PALETTE["rust"],
        linewidth=2.2,
    )
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Alleged offender incidents (thousands)")
    ax.set_title("Victorian alleged offender incidents")
    fig.text(
        0.01,
        -0.04,
        "Source: CSA alleged offender incidents Table 01. These are alleged incidents, not unique people.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "19_offender_trend.png")


def plot_sex_distribution() -> Path:
    df = sex_distribution()
    pivot = df.pivot(index="year", columns="sex", values="alleged_offender_incidents").fillna(0)
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in pivot.columns:
        colour = PALETTE["navy"] if col.lower().startswith("male") else PALETTE["teal"]
        ax.plot(pivot.index, pivot[col] / 1000, marker="o", label=col, color=colour, linewidth=2)
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Alleged offender incidents (thousands)")
    ax.set_title("Alleged offender incidents by sex")
    ax.legend()
    fig.text(
        0.01,
        -0.04,
        "Excludes unknown sex, organisations and CSA total rows. Sex is as recorded by police.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "20_sex_distribution.png")


def plot_age_distribution() -> Path:
    df = age_sex_distribution()
    grouped = (
        df.groupby("age_group", as_index=False)["alleged_offender_incidents"].sum()
    )
    order = [
        "10-11 years",
        "12-14 years",
        "15-17 years",
        "18-19 years",
        "20-24 years",
        "25-29 years",
        "30-34 years",
        "35-39 years",
        "40-44 years",
        "45-49 years",
        "50-54 years",
        "55-59 years",
        "60-64 years",
        "65-69 years",
        "70-74 years",
        "75 years and over",
    ]
    grouped["age_group"] = pd.Categorical(grouped["age_group"], categories=order, ordered=True)
    grouped = grouped.dropna(subset=["age_group"]).sort_values("age_group")
    fig, ax = plt.subplots(figsize=(11, 5.2))
    colours = [PALETTE["rust"] if str(a).startswith(("10", "12", "15")) else PALETTE["navy"] for a in grouped["age_group"]]
    ax.bar(grouped["age_group"].astype(str), grouped["alleged_offender_incidents"], color=colours)
    ax.set_xlabel("Age group")
    ax.set_ylabel("Alleged offender incidents")
    ax.set_title(f"Age distribution of alleged offender incidents, year ending March {int(df['year'].iloc[0])}")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.text(
        0.01,
        -0.08,
        "Youth groups (10-17) are highlighted. Totals are incident counts, not unique alleged offenders.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "21_age_distribution.png")


def plot_youth_trend() -> Path:
    df = youth_vs_adult()
    pivot = df.pivot(index="year", columns="age_band", values="alleged_offender_incidents").fillna(0)
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in pivot.columns:
        colour = PALETTE["rust"] if "Youth" in col else PALETTE["navy"]
        ax.plot(pivot.index, pivot[col] / 1000, marker="o", label=col, color=colour, linewidth=2)
    ax.set_xlabel("Year ending March")
    ax.set_ylabel("Alleged offender incidents (thousands)")
    ax.set_title("Youth and adult alleged offender incidents")
    ax.legend()
    fig.text(
        0.01,
        -0.04,
        "Youth is CSA age groups 10-11, 12-14 and 15-17. This is not a unique-person count.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "22_youth_adult.png")


def plot_youth_single_year() -> Path:
    df = youth_single_year_of_age()
    pivot = df.pivot(index="age_group", columns="sex", values="alleged_offender_incidents").fillna(0)
    pivot.index = pivot.index.astype(int)
    pivot = pivot.sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    x = pivot.index.astype(str)
    width = 0.38
    males = pivot.get("Males", pd.Series(0, index=pivot.index))
    females = pivot.get("Females", pd.Series(0, index=pivot.index))
    ax.bar([i - width / 2 for i in range(len(x))], males, width=width, label="Males", color=PALETTE["navy"])
    ax.bar([i + width / 2 for i in range(len(x))], females, width=width, label="Females", color=PALETTE["teal"])
    ax.set_xticks(range(len(x)), x)
    ax.set_xlabel("Single year of age")
    ax.set_ylabel("Alleged offender incidents")
    ax.set_title(f"Youth alleged offender incidents by single year of age, {int(df['year'].iloc[0])}")
    ax.legend()
    fig.text(
        0.01,
        -0.04,
        "Source: CSA alleged offender incidents Table 07. Ages 10-17 only.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "23_youth_single_year.png")


def plot_abs_state_rates() -> Path:
    df = abs_state_totals_latest()
    df = df.loc[df["jurisdiction"].ne("Australia")].sort_values(
        "rate_per_100000_age_10_plus", ascending=True
    )
    colours = [
        PALETTE["gold"] if j == "Victoria" else PALETTE["navy"] for j in df["jurisdiction"]
    ]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.barh(df["jurisdiction"], df["rate_per_100000_age_10_plus"], color=colours)
    ax.set_xlabel("Offender rate per 100,000 persons aged 10+")
    ax.set_ylabel("State or territory")
    ax.set_title("ABS offender rates, 2024–25")
    fig.text(
        0.01,
        -0.06,
        "Source: ABS Recorded Crime – Offenders, Table 6. Unique alleged offenders proceeded against. "
        "Not comparable to CSA alleged offender incidents.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "24_abs_state_rates.png")


def plot_abs_victoria_australia_trend() -> Path:
    vic = abs_victoria_persons_trend()
    aus = abs_australia_trend()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(
        vic["financial_year"],
        vic["rate_per_100000_age_10_plus"],
        color=PALETTE["gold"],
        marker="o",
        linewidth=2.2,
        label="Victoria",
    )
    ax.plot(
        aus["financial_year"],
        aus["rate_per_100000_age_10_plus"],
        color=PALETTE["navy"],
        marker="o",
        linewidth=2.2,
        label="Australia",
    )
    ax.set_xlabel("Financial year")
    ax.set_ylabel("Offender rate per 100,000 aged 10+")
    ax.set_title("ABS offender rates: Victoria and Australia")
    ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.text(
        0.01,
        -0.08,
        "Source: ABS Recorded Crime – Offenders, Tables 1 and 8. Financial years 2008–09 to 2024–25.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "25_abs_vic_australia_rate.png")


def plot_abs_victoria_offence_mix() -> Path:
    df = abs_principal_offence_latest("Victoria")
    df = df.loc[df["offence_level"].eq("division")].sort_values("offender_count")
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.barh(df["principal_offence"], df["offender_count"], color=PALETTE["teal"])
    ax.set_xlabel("Unique alleged offenders proceeded against")
    ax.set_ylabel("ANZSOC division")
    ax.set_title("ABS Victoria principal offence, 2024–25")
    fig.text(
        0.01,
        -0.05,
        "Source: ABS Recorded Crime – Offenders, Table 6. Principal offence of unique offenders, not CSA incidents.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    return _save(fig, "26_abs_vic_principal_offence.png")


def plot_abs_youth_trend() -> Path:
    vic = abs_victoria_youth_trend()
    latest = abs_youth_by_state_latest()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.1))
    axes[0].plot(
        vic["financial_year"],
        vic["offender_count"] / 1000,
        color=PALETTE["rust"],
        marker="o",
        linewidth=2.2,
    )
    axes[0].set_xlabel("Financial year")
    axes[0].set_ylabel("Youth offenders (thousands)")
    axes[0].set_title("ABS Victoria youth offenders")
    plt.setp(axes[0].get_xticklabels(), rotation=45, ha="right")
    other = latest.loc[latest["jurisdiction"].ne("Australia")].sort_values("youth_offenders")
    colours = [
        PALETTE["gold"] if j == "Victoria" else PALETTE["navy"] for j in other["jurisdiction"]
    ]
    axes[1].barh(other["jurisdiction"], other["youth_offenders"], color=colours)
    axes[1].set_xlabel("Youth offenders, 2024–25")
    axes[1].set_title("ABS youth offenders by jurisdiction")
    fig.text(
        0.01,
        -0.06,
        "Source: ABS Recorded Crime – Offenders, Table 20. Youth is persons aged 10–17 proceeded against.",
        fontsize=8,
        color=PALETTE["slate"],
    )
    fig.tight_layout()
    return _save(fig, "27_abs_youth_offenders.png")


def generate_all_figures() -> list[Path]:
    """Create the full visualisation suite used by notebooks and reports."""
    return [
        plot_statewide_trend(),
        plot_yoy_change(),
        plot_division_trends(),
        plot_division_composition(),
        plot_fastest_changing_subdivisions(),
        plot_top_lga_counts(),
        plot_top_lga_rates(),
        plot_lga_count_vs_rate(),
        plot_metro_regional(),
        plot_largest_lga_increases(),
        plot_top_subgroups(),
        plot_investigation_status(),
        plot_family_incident_share(),
        plot_lga_offence_heatmap(),
        plot_rolling_average(),
        plot_statistical_products(),
        plot_incident_trend(),
        plot_charge_status(),
        plot_offender_trend(),
        plot_sex_distribution(),
        plot_age_distribution(),
        plot_youth_trend(),
        plot_youth_single_year(),
        plot_abs_state_rates(),
        plot_abs_victoria_australia_trend(),
        plot_abs_victoria_offence_mix(),
        plot_abs_youth_trend(),
    ]


if __name__ == "__main__":
    for path in generate_all_figures():
        print(path)
