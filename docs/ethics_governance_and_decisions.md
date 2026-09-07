# Data ethics, governance and decision framework

Victorian Crime & Justice Intelligence Analytics Platform  
Official Crime Statistics Agency (CSA) aggregates, year ending March 2017–2026, and ABS Recorded Crime – Offenders, 2008–09 to 2024–25.  
Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute CSA and ABS.

This document is a decision brief for a public-sector analytics portfolio. It does not identify individuals and does not replace operational police or court advice.

---

## 1. Executive summary

Victoria’s recorded-offence volume remains high after a long rise, but the latest year is not another surge. In the year ending March 2026 the CSA recorded **625,426** offences (rate **8,690.8** per 100,000), **+15.4%** since 2017 and **−0.2%** on 2025. Those offences sat inside **468,711** criminal incidents (**−1.0%** on 2025). About **1.3** recorded offences were attached to each incident.

Justice outcomes and alleged-offender pressure tell a different story from the offence total. **55.6%** of criminal incidents were unsolved and **45.4%** of recorded offences had an unsolved investigation status. Alleged offender incidents rose to **195,342** (**+8.6%** on 2025; **+20.4%** since 2017). Youth aged 10–17 accounted for **22,654** of those incidents (**11.7%**), with the peak single year of age at **16**. Among known sex, **78.4%** of alleged offender incidents were male.

Place matters, and counts and rates answer different questions. Melbourne leads recorded-offence *counts* as an activity centre. The highest alleged-offender *rate* LGA in 2026 is **Latrobe**, not Melbourne. Family-incident related offences were **20.1%** of 2026 recorded offences (flag available from 2021). Justice procedures offences had the largest long-term division rise (**+43.8%**). Property and deception remained the largest mix (**57.9%**).

Nationally, Victoria looks different on the ABS unique-offender measure. In 2024–25 Victoria had **59,693** unique alleged offenders proceeded against, rate **961.6** per 100,000 aged 10+ (**−3.0%** on 2023–24). Australia’s rate was **1,419.8**. Victoria’s rate is the lowest of the six states. ABS **7,644** Victorian youth offenders (10–17) must not be treated as the same number as CSA’s **22,654** youth *incidents*.

**North-star reading:** use *rates* and *product-specific* series to decide where to look next. Do not add offences, incidents and alleged offender incidents into one crime total, and do not calculate a clearance rate by dividing CSA incidents into ABS offenders.

---

## 2. What problem we are solving

Public debate often treats “crime is up” as a single number. Victorian open data actually publishes several official products with different units, periods and meanings. Mixing them produces false rankings, false clearance rates and poor targeting of local government areas.

The problem this platform solves is **decision-quality use of official crime statistics**:

- keep recorded offences, criminal incidents, alleged offender incidents and ABS unique offenders separate
- show volume and rate side by side so activity centres are not confused with high-rate communities
- document youth, sex, charge/investigation status and family-incident flags without profiling people
- give analysts a repeatable pipeline, quality score and Tableau views that a briefing can defend

The platform does **not** solve operational dispatch, court listing, or individual risk assessment. Those need systems this project does not hold.

---

## 3. Business questions

| ID | Question | Product used | Decision it supports |
|---|---|---|---|
| BQ1 | Is statewide recorded crime still rising? | CSA recorded offences | Whether the latest year is a new surge or a pause after a long rise |
| BQ2 | How many events sit behind the offence count? | CSA criminal incidents | Resource conversations about incidents versus charges laid |
| BQ3 | Where is alleged-offender *pressure* highest? | CSA alleged offender incidents, LGA rates | Which LGAs need rate-based attention, not just CBD volume |
| BQ4 | What share of incidents remain unsolved? | Charge and investigation status | Whether volume growth is matched by resolved process |
| BQ5 | How large is the youth share, and at which age? | CSA age/sex and Table 07 | Prevention targeting around ages 10–17, especially 16 |
| BQ6 | How does Victoria compare with Australia? | ABS unique offenders | Whether Victoria is a high-rate or low-rate jurisdiction on a national measure |
| BQ7 | Can the tables be trusted for a briefing? | Loaded-table quality score | Whether missing, negative or duplicate keys block publication |

---

## 4. Analytical framework for business judgement

Judgement here means choosing the right measure for the decision, not forcing a single ranking.

1. **Name the product first.** Recorded offences count offences. Incidents count events that can hold several offences. Alleged offender incidents count incidents linked to an alleged offender, not unique people and not findings of guilt. ABS counts unique alleged offenders proceeded against in a financial year.
2. **Prefer rates for comparison.** Counts favour large, busy places. Rates (CSA per 100,000 population; ABS per 100,000 aged 10+) are the comparison measure across LGAs and jurisdictions.
3. **Separate time bases.** CSA is year ending March. ABS is July–June. A 2026 CSA figure and a 2024–25 ABS figure are not the same year.
4. **Treat process series as process, not guilt.** Unsolved, charges laid, no charges laid, and investigation status are administrative outcomes.
5. **Do not infer cause from a trend.** Recording practice, legislation, policing, reporting behaviour and genuine change can all move a series.
6. **Confidentiality beats completeness.** CSA suppresses some small homicide and sexual-offence cells. ABS randomly adjusts cells. Small add-ups may not match printed totals.
7. **Stop at aggregates.** No victim, offender or household identification. No individual-level scoring.

---

## 5. Data ethics and governance

### Principles

| Principle | Practice in this project |
|---|---|
| Purpose limitation | Aggregate public-sector analysis and briefing only |
| No identification | No names, addresses, or record-level linkage |
| No profiling | Streamlit returns LGA/year aggregates, not person lists |
| Product integrity | Four statistical products stay in separate tables and dashboard tabs |
| Confidentiality | Official suppression and random adjustment are left intact |
| Attribution | CSA and ABS cited under CC BY 4.0 |
| Transparency | Source URLs, reporting periods and caveats sit with every major output |
| Least sensitive data | Indigenous-status ABS cubes were not ingested |

### Data best practice

- Store official workbooks in `data/raw/` and never overwrite them.
- Rebuild analysis from those files; do not hand-type crime totals into code.
- Keep a source metadata record (publisher, licence, period, extraction time).
- Preserve the Streamlit `data_requests` audit log across SQLite rebuilds.
- Score loaded tables for missing counts, negatives, duplicate keys, year span and timeliness.
- Exclude CSA `Total` sex rows when summing Males and Females so youth is not doubled.
- Publish rates and counts together on geographic views.
- Exclude generated extracts from git; the repository carries code and official download links only (`data/README.md`).

### What must not be done with these outputs

- Do not identify or re-identify a person.
- Do not build a watchlist or offender profile.
- Do not present ABS 59,693 and CSA 195,342 as a clearance rate.
- Do not add the three CSA products into one “total crime” KPI.
- Do not treat alleged incidents as proven offences.

See also `docs/methodology.md` and `docs/data_quality.md`.

---

## 6. Stakeholder management

| Stakeholder | What they need | What this platform gives them | What it does not give them |
|---|---|---|---|
| Policy / department analysts | Defensible statewide trend and national context | Executive KPIs, product comparison, ABS rate index | Operational tasking lists |
| Local government community safety | Fair LGA comparison | Rate and count views, metro/regional split, YoY LGA change | Official CSA geography (metro/regional is analytical) |
| Police performance / intelligence (aggregate) | Process and alleged-offender series | Charge status, investigation status, principal offence, youth age | Individual case files |
| Youth / family-violence program leads | Scale of youth and family-incident flags | Youth 10–17 share, age 16 peak, family-incident 20.1% | Client-level need |
| Communications / ministers’ offices | Accurate wording | Caveats on every product; Tableau notes | A single crime number |
| Public and researchers | Open, attributed data | Catalogue links and CC BY 4.0 citation | Raw extracts in git |

Engagement rule: lead with the **question and the product**, then the number. If a stakeholder asks “is crime worse than NSW?”, answer with the ABS *rate*, not a CSA incident count.

---

## 7. Decision-driven portfolio

Work is organised around decisions, not charts for their own sake.

| Portfolio layer | Decision | Primary artefact |
|---|---|---|
| Statewide watch | Has the long rise continued into 2026? | Tableau Overview; `statewide_annual_totals` |
| Place | Which LGAs are high-rate versus high-count? | Tableau Geographic Intelligence |
| Justice process | How much volume is unresolved? | Investigation status; charge status |
| Alleged offenders | Where is incident pressure rising, including youth? | Tableau Offenders and Justice |
| National context | Is Victoria high-rate on a comparable national measure? | Tableau National Comparison |
| Trust | Can the briefing be published? | Tableau Data Quality; quality score 100.0% on loaded tables |

---

## 8. North star metrics

The north star is **decision-safe comparison**, not a maximised crime count.

| Metric | Definition | Latest official value | Why it is a north star |
|---|---|---|---|
| Recorded offence rate | CSA offences per 100,000, year ending March | **8,690.8** (2026) | Statewide harm/volume context |
| Offences per incident | Recorded offences ÷ criminal incidents | **~1.3** (2026) | Stops “offences” being read as “events” |
| Unsolved incident share | CSA charge status = Unsolved | **55.6%** (2026) | Process pressure |
| Alleged offender incident rate (LGA) | CSA alleged offender incidents per 100,000 | Highest LGA: **Latrobe** | Place targeting |
| Youth alleged-offender share | CSA incidents, ages 10–17, known sex | **11.7%** (22,654) | Prevention focus |
| ABS Victoria offender rate | Unique offenders per 100,000 aged 10+ | **961.6** (2024–25) | National comparison |
| Product integrity flag | ABS unique offenders treated as not comparable to CSA incidents | Comparable = **0** | Ethics control |
| Loaded-table quality | Completeness, validity, uniqueness, consistency, timeliness | **100.0%** | Publish/no-publish gate |

Guardrail metrics (do not “optimise” these as success): raw CBD offence counts alone; any ratio of CSA incidents to ABS unique offenders.

---

## 9. Key insights with evidence (Tableau)

Rebuild the workbook with `python -m src.dashboard.build`. Tabs below match `docs/tableau_guide.md`.

### Overview — Victorian Crime Overview

| Insight | Evidence | Tableau view |
|---|---|---|
| The long rise paused in 2026 | 625,426 offences; −0.2% on 2025; +15.4% since 2017 | KPI cards; statewide trend; YoY change |
| Offences and incidents are not 1:1 | 468,711 incidents; about 1.3 offences per incident | Three official products |
| Property still dominates mix; justice procedures rose most over the decade | Property and deception 57.9%; justice procedures +43.8% from 2017 | Offence composition |
| A large share of offences remain unsolved | 45.4% unsolved investigation status in 2026 | Investigation status |
| Family-incident related offences are a fifth of the latest year | 20.1% of 2026 recorded offences (flag from 2021) | Family-incident related card / family series |

### Geographic Intelligence

| Insight | Evidence | Tableau view |
|---|---|---|
| Melbourne is the volume centre, not automatically the highest-rate story for alleged offenders | Melbourne 45,561 recorded offences; rate 23,304 per 100,000. Highest alleged-offender *rate* LGA is Latrobe | LGA map; highest counts; highest alleged-offender rates |
| Compare places with rates | Count-versus-rate scatter separates busy LGAs from high-rate LGAs | Count versus rate |
| Metro/regional is an analysis grouping | Police region contains “Metro”, plus seven Eastern LGAs | Metro and regional trend |

### Offenders and Justice

| Insight | Evidence | Tableau view |
|---|---|---|
| Alleged offender incidents rose while offences were flat | 195,342 incidents; +8.6% on 2025; +20.4% since 2017 | Alleged offender trend |
| Most incidents with known sex are male | 78.4% male; 21.6% female | Known sex |
| Youth is a minority of incidents but concentrated late in the 10–17 band | 22,654 youth incidents (11.7%); peak age 16 (5,991) | Youth versus adult; single year of age |
| More than half of incidents are unsolved | 55.6% unsolved; 30.1% charges laid; 14.3% no charges laid | Charge status |

### National Comparison (ABS)

| Insight | Evidence | Tableau view |
|---|---|---|
| Victoria is low-rate on the ABS unique-offender measure | Rate 961.6 versus Australia 1,419.8 (67.7% of the national rate) | State rates; Victoria versus Australia trend |
| Victoria’s unique-offender count fell in 2024–25 | 59,693; −3.0% on 2023–24 | ABS Victoria KPI |
| Youth unique offenders are 12.8% of Victorian ABS offenders | 7,644 aged 10–17 | ABS youth charts |
| CSA incidents and ABS offenders are different products | 195,342 vs 59,693; comparable = 0 | “Do not compare” bar |

### Data Quality

| Insight | Evidence | Tableau view |
|---|---|---|
| Loaded tables were complete enough to brief | Overall score 100.0%; no missing counts, negatives or duplicate business keys in the scored tables | Loaded-table score |

---

## 10. Recommendations and evidence

Recommendations are **analytical next steps** for stakeholders who already own operations. They are not instructions to Victoria Police or a finding of guilt.

| Recommendation | Evidence that justifies it |
|---|---|
| Brief 2026 as a pause after a long rise, not a new statewide surge | Offences −0.2% YoY; still +15.4% since 2017 |
| Use LGA *rates* for community comparison; keep Melbourne counts for activity-centre planning | Melbourne leads counts; Latrobe leads alleged-offender rate |
| Treat unresolved process as a parallel risk to volume | 55.6% incidents unsolved; 45.4% offences unsolved investigation status |
| Keep youth prevention focused on the late-teen years inside 10–17 | Peak single year of age 16; youth 11.7% of alleged offender incidents |
| Use ABS *rates* for state-to-state claims; never CSA incidents versus ABS unique offenders | Vic ABS rate 961.6 vs Aus 1,419.8; products not comparable |
| Repeat the quality gate before each public refresh | Loaded-table score 100.0% on current extracts |

---

## 11. Recommendation matrix

Suggested owners are functional roles, not named officers. Expectation is the change a briefing should produce. The metric is what this platform can actually track from official tables.

| Priority | Action | Owner (suggested) | Expectation | Metric to track |
|---|---|---|---|---|
| P1 | Publish the 2026 statewide brief with all four products named separately | Department analyst / BI lead | Stakeholders stop quoting one blended “crime total” | Offence count and rate; incident count; alleged offender incidents; ABS rate — four lines, never summed |
| P1 | Rank LGAs by alleged-offender *rate* and recorded-offence *rate*, not count alone | LGA community safety + police performance (aggregate) | Latrobe-type high-rate places appear in the conversation alongside Melbourne volume | Top-12 LGA rate tables on Geographic and Offenders tabs |
| P1 | Report unsolved share beside volume in every quarterly pack | Justice / performance reporting | Process pressure is visible when volume is flat | Unsolved incident share (55.6% in 2026); unsolved investigation share (45.4%) |
| P2 | Brief youth using CSA incidents *and* ABS unique youth separately | Youth justice / prevention program lead | Age-16 peak is used for CSA incident design; ABS 7,644 is used only for unique-offender context | CSA youth share 11.7%; CSA age-16 count; ABS Vic youth 7,644 |
| P2 | Use family-incident share as a monitoring series from 2021 onward, not a 2017 baseline | Family-violence policy (aggregate) | No false long-term % from years without the flag | Family-incident related share of recorded offences (20.1% in 2026) |
| P2 | For national media or inter-jurisdictional questions, quote ABS rates only | Communications / policy | Victoria described as below the national ABS rate, not “fewer incidents than NSW” from mixed products | ABS Vic rate / ABS Aus rate (961.6 / 1,419.8) |
| P3 | Re-run the pipeline and quality score before each data release | Data custodian | No briefing from stale or broken loads | Overall quality score; request-log row count in `data_requests` |
| P3 | Keep git free of raw and processed files; point users to official URLs | Data custodian | No unofficial copies circulating as “the dataset” | Presence of `data/README.md` links; absence of workbooks in the remote repository |

---

## 12. Business decision this brief supports

**Decision:** How should a 2026 Victorian crime briefing be framed for place, process and national comparison?

**Judgement supported by the evidence:**

1. Statewide recorded offences are high versus 2017 but not rising in the latest year.
2. Place decisions should split *volume* (Melbourne) from *rate* (including Latrobe for alleged offenders).
3. Process is strained: a majority of incidents are unsolved.
4. Youth work should focus on the official 10–17 definition, with attention to age 16, and must not confuse CSA incidents with ABS unique youth offenders.
5. National statements should use the ABS unique-offender *rate*, where Victoria is below Australia and lowest among the six states.
6. Publish only after the loaded-table quality gate passes.

If those six statements are the ones a stakeholder can repeat after the Tableau walkthrough, the briefing has done its job.
