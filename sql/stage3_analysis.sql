-- Stage 3 SQL analysis: ABS Recorded Crime – Offenders.
-- ABS unique offenders proceeded against (financial year) are not CSA alleged
-- offender incidents (year ending March). Do not union the two products.

-- Q: Latest ABS offender counts and rates by jurisdiction
SELECT
    financial_year,
    jurisdiction,
    offender_count,
    rate_per_100000_age_10_plus
FROM abs_offenders_states_totals
WHERE offence_level = 'total'
  AND sex = 'Persons'
  AND age_group = 'All ages 10+'
ORDER BY rate_per_100000_age_10_plus DESC;

-- Q: Victoria ABS offender time series
SELECT
    financial_year,
    year_end,
    sex,
    offender_count,
    rate_per_100000_age_10_plus
FROM abs_offenders_trend
WHERE jurisdiction = 'Victoria'
ORDER BY year_end, sex;

-- Q: Australia ABS offender time series
SELECT
    financial_year,
    year_end,
    offender_count,
    rate_per_100000_age_10_plus
FROM abs_offenders_trend
WHERE jurisdiction = 'Australia'
  AND sex = 'Persons'
ORDER BY year_end;

-- Q: Victoria versus Australia on the ABS measure, latest year
SELECT
    v.financial_year,
    v.offender_count AS victoria_offenders,
    v.rate_per_100000_age_10_plus AS victoria_rate,
    a.offender_count AS australia_offenders,
    a.rate_per_100000_age_10_plus AS australia_rate,
    ROUND(100.0 * v.offender_count / a.offender_count, 1) AS victoria_share_pct,
    ROUND(100.0 * v.rate_per_100000_age_10_plus / a.rate_per_100000_age_10_plus, 1) AS victoria_rate_index
FROM abs_offenders_states_totals v
JOIN abs_offenders_states_totals a
  ON v.financial_year = a.financial_year
WHERE v.jurisdiction = 'Victoria'
  AND a.jurisdiction = 'Australia'
  AND v.offence_level = 'total'
  AND a.offence_level = 'total';

-- Q: ABS Victoria principal offence divisions, 2024-25
SELECT
    principal_offence,
    offender_count,
    rate_per_100000_age_10_plus
FROM abs_offenders
WHERE source_table = 'Table 6'
  AND jurisdiction = 'Victoria'
  AND offence_level = 'division'
  AND financial_year = '2024–25'
ORDER BY offender_count DESC;

-- Q: ABS youth offenders by state, latest year
SELECT
    financial_year,
    jurisdiction,
    offender_count AS youth_offenders,
    rate_per_100000_age_10_plus AS youth_rate
FROM abs_youth_offenders
WHERE year_end = (SELECT MAX(year_end) FROM abs_youth_offenders)
ORDER BY youth_offenders DESC;

-- Q: ABS Victoria youth trend
SELECT
    financial_year,
    year_end,
    offender_count,
    rate_per_100000_age_10_plus
FROM abs_youth_offenders
WHERE jurisdiction = 'Victoria'
ORDER BY year_end;
