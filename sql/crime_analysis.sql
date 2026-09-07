-- Victorian Crime & Justice Intelligence Analytics Platform
-- Analysis-only SQL against the SQLite database built from official CSA tables.
-- Source: Crime Statistics Agency, Recorded offences, year ending March 2026.
-- These queries use aggregate recorded-offence statistics only.
-- They do not identify individuals and do not imply causation.

-- =============================================================================
-- Q1. Overall Victorian crime trend (statewide recorded offences)
-- =============================================================================
SELECT
    year,
    year_ending,
    SUM(offence_count) AS offence_count,
    SUM(rate_per_100_000_population) AS rate_per_100000
FROM statewide_offences
GROUP BY year, year_ending
ORDER BY year;


-- =============================================================================
-- Q2–Q5. Offence categories increasing / declining, YoY and long-term change
-- =============================================================================
WITH annual AS (
    SELECT
        year,
        offence_division,
        SUM(offence_count) AS offence_count
    FROM statewide_offences
    GROUP BY year, offence_division
),
yoy AS (
    SELECT
        year,
        offence_division,
        offence_count,
        LAG(offence_count) OVER (PARTITION BY offence_division ORDER BY year) AS prev_count
    FROM annual
)
SELECT
    year,
    offence_division,
    offence_count,
    offence_count - prev_count AS yoy_count,
    ROUND(100.0 * (offence_count - prev_count) / prev_count, 1) AS yoy_pct
FROM yoy
WHERE prev_count IS NOT NULL
ORDER BY year, yoy_pct DESC;


WITH bounds AS (
    SELECT MIN(year) AS start_year, MAX(year) AS end_year
    FROM statewide_offences
),
base AS (
    SELECT
        year,
        offence_division,
        offence_subdivision,
        SUM(offence_count) AS offence_count
    FROM statewide_offences
    GROUP BY year, offence_division, offence_subdivision
)
SELECT
    a.offence_division,
    a.offence_subdivision,
    a.offence_count AS start_count,
    b.offence_count AS end_count,
    b.offence_count - a.offence_count AS change_count,
    ROUND(100.0 * (b.offence_count - a.offence_count) / a.offence_count, 1) AS change_pct
FROM base a
JOIN base b
  ON a.offence_subdivision = b.offence_subdivision
 AND a.offence_division = b.offence_division
JOIN bounds x
  ON a.year = x.start_year
 AND b.year = x.end_year
WHERE a.offence_count >= 1000
ORDER BY change_pct DESC;


-- =============================================================================
-- Q6. LGAs with the highest number of offences (latest year)
-- =============================================================================
SELECT
    year,
    police_region,
    local_government_area,
    metro_regional,
    offence_count,
    rate_per_100_000_population AS rate_per_100000
FROM lga_offence_totals
WHERE is_region_total = 0
  AND year = (SELECT MAX(year) FROM lga_offence_totals)
ORDER BY offence_count DESC
LIMIT 20;


-- =============================================================================
-- Q7. LGAs with the highest crime rates (latest year)
-- =============================================================================
SELECT
    year,
    police_region,
    local_government_area,
    metro_regional,
    offence_count,
    rate_per_100_000_population AS rate_per_100000
FROM lga_offence_totals
WHERE is_region_total = 0
  AND year = (SELECT MAX(year) FROM lga_offence_totals)
ORDER BY rate_per_100_000_population DESC
LIMIT 20;


-- =============================================================================
-- Q8. LGAs with the largest year-on-year increases (latest year)
-- =============================================================================
WITH ranked AS (
    SELECT
        year,
        police_region,
        local_government_area,
        metro_regional,
        offence_count,
        rate_per_100_000_population AS rate_per_100000,
        LAG(offence_count) OVER (
            PARTITION BY local_government_area ORDER BY year
        ) AS prev_count
    FROM lga_offence_totals
    WHERE is_region_total = 0
)
SELECT
    year,
    police_region,
    local_government_area,
    metro_regional,
    prev_count,
    offence_count,
    offence_count - prev_count AS yoy_count,
    ROUND(100.0 * (offence_count - prev_count) / prev_count, 1) AS yoy_pct
FROM ranked
WHERE year = (SELECT MAX(year) FROM ranked)
  AND prev_count IS NOT NULL
ORDER BY yoy_pct DESC
LIMIT 20;


-- =============================================================================
-- Q9. Offence categories that dominate different LGAs (latest year)
-- =============================================================================
WITH lga_div AS (
    SELECT
        year,
        local_government_area,
        offence_division,
        SUM(offence_count) AS offence_count
    FROM lga_offences
    WHERE year = (SELECT MAX(year) FROM lga_offences)
    GROUP BY year, local_government_area, offence_division
),
ranked AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY local_government_area
            ORDER BY offence_count DESC
        ) AS division_rank,
        100.0 * offence_count / SUM(offence_count) OVER (
            PARTITION BY local_government_area
        ) AS share_pct
    FROM lga_div
)
SELECT
    local_government_area,
    offence_division,
    offence_count,
    ROUND(share_pct, 1) AS share_pct
FROM ranked
WHERE division_rank = 1
ORDER BY share_pct DESC, offence_count DESC;


-- =============================================================================
-- Q10. Metropolitan versus regional differences
-- =============================================================================
SELECT
    year,
    metro_regional,
    COUNT(DISTINCT local_government_area) AS lga_count,
    SUM(offence_count) AS offence_count,
    ROUND(AVG(rate_per_100_000_population), 1) AS avg_lga_rate_per_100000,
    ROUND(MIN(rate_per_100_000_population), 1) AS min_lga_rate,
    ROUND(MAX(rate_per_100_000_population), 1) AS max_lga_rate
FROM lga_offence_totals
WHERE is_region_total = 0
  AND metro_regional IS NOT NULL
GROUP BY year, metro_regional
ORDER BY year, metro_regional;


-- =============================================================================
-- Q11–Q14. Most common offences, fastest growing, highest rates, composition
-- =============================================================================
SELECT
    year,
    offence_division,
    offence_subdivision,
    offence_subgroup,
    offence_count,
    rate_per_100_000_population AS rate_per_100000
FROM statewide_offences
WHERE year = (SELECT MAX(year) FROM statewide_offences)
ORDER BY offence_count DESC
LIMIT 20;


WITH annual AS (
    SELECT
        year,
        offence_division,
        offence_subdivision,
        offence_subgroup,
        offence_count,
        LAG(offence_count) OVER (
            PARTITION BY offence_subgroup ORDER BY year
        ) AS prev_count
    FROM statewide_offences
)
SELECT
    year,
    offence_division,
    offence_subgroup,
    prev_count,
    offence_count,
    ROUND(100.0 * (offence_count - prev_count) / prev_count, 1) AS yoy_pct
FROM annual
WHERE year = (SELECT MAX(year) FROM annual)
  AND prev_count >= 500
ORDER BY yoy_pct DESC
LIMIT 20;


SELECT
    year,
    offence_division,
    SUM(offence_count) AS offence_count,
    ROUND(
        100.0 * SUM(offence_count)
        / SUM(SUM(offence_count)) OVER (PARTITION BY year),
        1
    ) AS share_pct
FROM statewide_offences
GROUP BY year, offence_division
ORDER BY year, share_pct DESC;


-- =============================================================================
-- Investigation status and family-incident analysis (available in this release)
-- Offender age/sex are not in the recorded-offences workbooks.
-- =============================================================================
SELECT
    year,
    investigation_status,
    SUM(offence_count) AS offence_count,
    ROUND(
        100.0 * SUM(offence_count)
        / SUM(SUM(offence_count)) OVER (PARTITION BY year),
        1
    ) AS share_pct
FROM statewide_investigation_status
GROUP BY year, investigation_status
ORDER BY year, share_pct DESC;


SELECT
    year,
    family_incident_flag,
    SUM(offence_count) AS offence_count,
    SUM(rate_per_100_000_population) AS rate_per_100000,
    ROUND(
        100.0 * SUM(offence_count)
        / SUM(SUM(offence_count)) OVER (PARTITION BY year),
        1
    ) AS share_pct
FROM statewide_family_incidents
GROUP BY year, family_incident_flag
ORDER BY year, family_incident_flag;


-- =============================================================================
-- Q20–Q24. Data-quality checks on loaded CSA tables
-- =============================================================================
SELECT
    'lga_offence_totals' AS table_name,
    COUNT(*) AS row_count,
    SUM(CASE WHEN local_government_area IS NULL OR local_government_area = '' THEN 1 ELSE 0 END) AS missing_lga,
    SUM(CASE WHEN offence_count IS NULL THEN 1 ELSE 0 END) AS missing_count,
    SUM(CASE WHEN offence_count < 0 THEN 1 ELSE 0 END) AS negative_count,
    SUM(CASE WHEN rate_per_100_000_population < 0 THEN 1 ELSE 0 END) AS negative_rate,
    COUNT(*)
      - COUNT(DISTINCT year || '|' || police_region || '|' || local_government_area) AS duplicate_keys,
    MIN(year) AS min_year,
    MAX(year) AS max_year
FROM lga_offence_totals

UNION ALL

SELECT
    'lga_offences',
    COUNT(*),
    SUM(CASE WHEN local_government_area IS NULL OR local_government_area = '' THEN 1 ELSE 0 END),
    SUM(CASE WHEN offence_count IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN offence_count < 0 THEN 1 ELSE 0 END),
    SUM(CASE WHEN lga_rate_per_100_000_population < 0 THEN 1 ELSE 0 END),
    COUNT(*)
      - COUNT(DISTINCT year || '|' || local_government_area || '|' || offence_subgroup),
    MIN(year),
    MAX(year)
FROM lga_offences

UNION ALL

SELECT
    'statewide_offences',
    COUNT(*),
    0,
    SUM(CASE WHEN offence_count IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN offence_count < 0 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rate_per_100_000_population < 0 THEN 1 ELSE 0 END),
    COUNT(*) - COUNT(DISTINCT year || '|' || offence_subgroup),
    MIN(year),
    MAX(year)
FROM statewide_offences;


SELECT year, COUNT(DISTINCT offence_subgroup) AS subgroup_count
FROM statewide_offences
GROUP BY year
ORDER BY year;


SELECT
    year,
    COUNT(DISTINCT local_government_area) AS lga_count
FROM lga_offence_totals
WHERE is_region_total = 0
GROUP BY year
ORDER BY year;
