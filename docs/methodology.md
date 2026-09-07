# Methodology

## Statistical products

The platform keeps four official products separate.

1. **CSA recorded offences** — offences recorded by Victoria Police, year ending March.
2. **CSA criminal incidents** — incidents that can contain multiple offences, year ending March.
3. **CSA alleged offender incidents** — incidents linked to an alleged offender, year ending March. Not unique people and not proven offences.
4. **ABS Recorded Crime – Offenders** — unique alleged offenders proceeded against, financial year July–June. Rate per 100,000 persons aged 10 years and over.

Victoria’s ABS 2024–25 count (59,693) must not be compared with CSA 2026 alleged offender incidents (195,342) as if they were the same measure.

## Geography

Metropolitan / regional is derived for analysis:

- Police region name contains `Metro`, or
- LGA is one of Boroondara, Manningham, Monash, Whitehorse, Knox, Maroondah, Yarra Ranges.

Justice Institutions and Unincorporated Vic are retained in tables but omitted from the symbol map.

## Youth

- CSA youth uses official age groups 10–11, 12–14 and 15–17, plus single years 10–17 in Table 07.
- Sex filters are Males and Females only. CSA `Total` rows are excluded so youth is not double-counted.
- ABS youth is persons aged 10–17 proceeded against (Table 20).

## Rates

Use rates when comparing LGAs or jurisdictions with different populations. CSA LGA rates use the published CSA population denominator. ABS rates use persons aged 10 years and over.

## Change measures

Year-on-year change is `(latest − previous) / previous`. Long-term CSA change uses 2017 to 2026. ABS time series uses 2008–09 to 2024–25.

## ABS parsing

ABS Excel files have title rows, merged Number/Rate headers and footnote letters. The parser:

- reads published sheets Table 1, Table 6, Table 8 and Table 20
- takes the first 17 financial-year columns as counts and the repeated year block as rates
- strips footnote markers such as `(d)` before mapping jurisdictions
- stops Table 6 at the first `Total` row so the printed table is not read twice

ABS cells are randomly adjusted for confidentiality. Small cells can therefore fail to add exactly to printed totals.

## What is not done

- No individual-level linkage or profiling.
- No Indigenous-status ABS cubes in this stage.
- No causal claims from correlation.
- No blending of CSA incidents with ABS unique offenders.
