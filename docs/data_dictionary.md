# Data dictionary

Column names follow the official workbooks after snake-case standardisation. No business fields are invented.

## CSA recorded offences

| Table | Grain | Key columns |
|---|---|---|
| `statewide_offences` | Year × offence subgroup | `year`, `offence_division`, `offence_count`, `rate_per_100_000_population` |
| `lga_offence_totals` | Year × LGA | `offence_count`, `rate_per_100_000_population`, `metro_regional` |
| `lga_offences` | Year × LGA × offence type | `offence_count`, LGA and PSA rates |
| `statewide_investigation_status` | Year × status | `offence_count` |
| `statewide_family_incidents` | Year × family-incident flag | `offence_count` |

`metro_regional` is an analytical grouping: police region contains “Metro”, or the LGA is in the Eastern metropolitan set. It is not official CSA geography.

## CSA criminal incidents

| Table | Grain | Key columns |
|---|---|---|
| `statewide_incidents` | Year × offence subgroup | `incidents_recorded` |
| `lga_incident_totals` | Year × LGA | `incidents_recorded` |
| `statewide_incident_charge_status` | Year × charge status | `incidents_recorded` |

A criminal incident can contain more than one recorded offence.

## CSA alleged offender incidents

| Table | Grain | Key columns |
|---|---|---|
| `statewide_offenders` | Year × principal offence | `alleged_offender_incidents` |
| `statewide_offenders_age_sex` | Year × sex × age group | `is_youth`, `is_total_row` |
| `lga_offender_totals` | Year × LGA | `alleged_offender_incidents` |

These rows are **incidents**, not unique people and not findings of guilt. CSA `Total` sex rows must not be summed with Males and Females.

## ABS Recorded Crime – Offenders

| Table | Grain | Key columns |
|---|---|---|
| `abs_offenders` | Combined tidy extract | `financial_year`, `year_end`, `jurisdiction`, `sex`, `age_group`, `principal_offence`, `offender_count`, `rate_per_100000_age_10_plus` |
| `abs_offenders_trend` | Year × Victoria sex or Australia persons | totals only |
| `abs_offenders_states_latest` | 2024–25 × jurisdiction × offence | divisions and subdivisions |
| `abs_youth_offenders` | Year × jurisdiction | youth 10–17 totals |

ABS counts unique alleged offenders proceeded against in a **financial year (July–June)**. Rates are per 100,000 persons aged 10 years and over. Do not join these counts to CSA alleged offender incidents.

## Operational

`data_requests` stores Streamlit audit rows: `request_id`, `requested_at`, filters, `row_count`, `summary`.
