-- Stage 2 SQL analysis: criminal incidents and alleged offender incidents.
-- Source: Crime Statistics Agency, year ending March 2026.
-- Alleged offender incidents are not findings of guilt.

-- Q: Statewide criminal incident trend
SELECT
    year,
    SUM(incidents_recorded) AS incident_count,
    SUM(rate_per_100_000_population) AS rate_per_100000
FROM statewide_incidents
GROUP BY year
ORDER BY year;

-- Q: Compare recorded offences, criminal incidents and alleged offender incidents
WITH offences AS (
    SELECT year, SUM(offence_count) AS recorded_offences FROM statewide_offences GROUP BY year
),
incidents AS (
    SELECT year, SUM(incidents_recorded) AS criminal_incidents FROM statewide_incidents GROUP BY year
),
offenders AS (
    SELECT year, SUM(alleged_offender_incidents) AS alleged_offender_incidents FROM statewide_offenders GROUP BY year
)
SELECT
    o.year,
    o.recorded_offences,
    i.criminal_incidents,
    f.alleged_offender_incidents,
    ROUND(1.0 * o.recorded_offences / i.criminal_incidents, 2) AS offences_per_incident
FROM offences o
JOIN incidents i ON o.year = i.year
JOIN offenders f ON o.year = f.year
ORDER BY o.year;

-- Q: Charge status of criminal incidents, latest year
SELECT
    year,
    charge_status,
    SUM(incidents_recorded) AS incident_count,
    ROUND(100.0 * SUM(incidents_recorded) / SUM(SUM(incidents_recorded)) OVER (PARTITION BY year), 1) AS share_pct
FROM statewide_incident_charge_status
WHERE year = (SELECT MAX(year) FROM statewide_incident_charge_status)
GROUP BY year, charge_status
ORDER BY incident_count DESC;

-- Q15. Major principal offence categories among alleged offenders
SELECT
    year,
    offence_division,
    offence_subdivision,
    SUM(alleged_offender_incidents) AS alleged_offender_incidents
FROM statewide_offenders
WHERE year = (SELECT MAX(year) FROM statewide_offenders)
GROUP BY year, offence_division, offence_subdivision
ORDER BY alleged_offender_incidents DESC;

-- Q16. Age distribution of alleged offender incidents
SELECT
    year,
    age_group,
    SUM(alleged_offender_incidents) AS alleged_offender_incidents
FROM statewide_offenders_age_sex
WHERE is_total_row = 0
  AND LOWER(sex) IN ('males', 'females')
  AND year = (SELECT MAX(year) FROM statewide_offenders_age_sex)
GROUP BY year, age_group
ORDER BY alleged_offender_incidents DESC;

-- Q17. Sex distribution
SELECT
    year,
    sex,
    SUM(alleged_offender_incidents) AS alleged_offender_incidents,
    ROUND(
        100.0 * SUM(alleged_offender_incidents)
        / SUM(SUM(alleged_offender_incidents)) OVER (PARTITION BY year),
        1
    ) AS share_pct
FROM statewide_offenders_age_sex
WHERE is_total_row = 0
  AND LOWER(sex) IN ('males', 'females')
GROUP BY year, sex
ORDER BY year, sex;

-- Q18. Youth versus adult alleged offender incidents
SELECT
    year,
    CASE WHEN is_youth = 1 THEN 'Youth (10-17)' ELSE 'Adult (18+)' END AS age_band,
    SUM(alleged_offender_incidents) AS alleged_offender_incidents
FROM statewide_offenders_age_sex
WHERE is_total_row = 0
  AND LOWER(sex) IN ('males', 'females')
GROUP BY year, CASE WHEN is_youth = 1 THEN 'Youth (10-17)' ELSE 'Adult (18+)' END
ORDER BY year, age_band;

-- Q: Youth single year of age, latest year
SELECT
    year,
    sex,
    age_group,
    metric_value AS alleged_offender_incidents
FROM statewide_youth_metrics
WHERE category = 'Alleged Offender Incidents'
  AND LOWER(sex) IN ('males', 'females')
  AND CAST(age_group AS INTEGER) BETWEEN 10 AND 17
  AND year = (SELECT MAX(year) FROM statewide_youth_metrics)
ORDER BY sex, CAST(age_group AS INTEGER);

-- Q: Highest alleged-offender-rate LGAs
SELECT
    year,
    local_government_area,
    metro_regional,
    alleged_offender_incidents,
    rate_per_100_000_population AS rate_per_100000
FROM lga_offender_totals
WHERE is_region_total = 0
  AND year = (SELECT MAX(year) FROM lga_offender_totals)
ORDER BY rate_per_100_000_population DESC
LIMIT 20;
