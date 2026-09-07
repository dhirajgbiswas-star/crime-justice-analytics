-- Analytical schema for Victorian CSA statistics.
-- Optional MySQL target. SQLite remains the local default.

CREATE DATABASE IF NOT EXISTS victorian_crime
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'crime_analyst'@'%' IDENTIFIED BY 'change_me';
GRANT ALL PRIVILEGES ON victorian_crime.* TO 'crime_analyst'@'%';
FLUSH PRIVILEGES;
USE victorian_crime;

CREATE TABLE IF NOT EXISTS dim_date (
  date_key INT PRIMARY KEY,
  year SMALLINT NOT NULL,
  year_ending VARCHAR(16) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_lga (
  lga_key INT AUTO_INCREMENT PRIMARY KEY,
  local_government_area VARCHAR(128) NOT NULL UNIQUE,
  police_region VARCHAR(128),
  metro_regional VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS dim_offence (
  offence_key INT AUTO_INCREMENT PRIMARY KEY,
  offence_division VARCHAR(128) NOT NULL,
  offence_subdivision VARCHAR(128),
  offence_subgroup VARCHAR(255),
  UNIQUE KEY uq_offence (offence_division, offence_subdivision, offence_subgroup)
);

CREATE TABLE IF NOT EXISTS fact_recorded_offence (
  year SMALLINT NOT NULL,
  lga_key INT,
  offence_key INT,
  offence_count INT,
  rate_per_100000 DECIMAL(12,4),
  KEY idx_offence_year (year),
  KEY idx_offence_lga (lga_key)
);

CREATE TABLE IF NOT EXISTS fact_criminal_incident (
  year SMALLINT NOT NULL,
  lga_key INT,
  offence_key INT,
  incident_count INT,
  rate_per_100000 DECIMAL(12,4),
  KEY idx_incident_year (year),
  KEY idx_incident_lga (lga_key)
);

CREATE TABLE IF NOT EXISTS fact_alleged_offender (
  year SMALLINT NOT NULL,
  lga_key INT,
  offence_key INT,
  alleged_offender_incidents INT,
  rate_per_100000 DECIMAL(12,4),
  KEY idx_offender_year (year),
  KEY idx_offender_lga (lga_key)
);

-- ABS unique alleged offenders proceeded against. Do not union with CSA incidents.
CREATE TABLE IF NOT EXISTS fact_abs_offender (
  year_end SMALLINT NOT NULL,
  financial_year VARCHAR(16) NOT NULL,
  jurisdiction VARCHAR(64) NOT NULL,
  sex VARCHAR(16),
  age_group VARCHAR(32),
  principal_offence VARCHAR(255),
  offence_level VARCHAR(32),
  offender_count INT,
  rate_per_100000_age_10_plus DECIMAL(12,4),
  KEY idx_abs_year (year_end),
  KEY idx_abs_jurisdiction (jurisdiction)
);

CREATE OR REPLACE VIEW vw_crime_summary AS
SELECT year, SUM(offence_count) AS recorded_offences
FROM fact_recorded_offence
GROUP BY year;

CREATE OR REPLACE VIEW vw_incident_summary AS
SELECT year, SUM(incident_count) AS criminal_incidents
FROM fact_criminal_incident
GROUP BY year;

CREATE OR REPLACE VIEW vw_offender_summary AS
SELECT year, SUM(alleged_offender_incidents) AS alleged_offender_incidents
FROM fact_alleged_offender
GROUP BY year;

CREATE OR REPLACE VIEW vw_abs_offender_summary AS
SELECT year_end, jurisdiction, SUM(offender_count) AS offenders
FROM fact_abs_offender
WHERE offence_level = 'total'
  AND sex = 'Persons'
  AND age_group = 'All ages 10+'
GROUP BY year_end, jurisdiction;
