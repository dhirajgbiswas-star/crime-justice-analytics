# Data files are not stored in this repository

Download the official workbooks into `data/raw/` before running the pipeline. Do not commit those files.

Publisher licences are Creative Commons Attribution 4.0. Attribute the Crime Statistics Agency and the Australian Bureau of Statistics.

## Crime Statistics Agency (Victoria)

Publication date: 19 June 2026. Reporting period: year ending March 2017 to year ending March 2026.

### Recorded offences

Catalogue: https://discover.data.vic.gov.au/dataset/data-tables-recorded-offences

- https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Recorded_Offences_Visualisation_Year_Ending_March_2026.xlsx
- https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Recorded_Offences_Year_Ending_March_2026.xlsx

### Criminal incidents

Catalogue: https://discover.data.vic.gov.au/dataset/criminal-incident

- https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Criminal_Incidents_Visualisation_Year_Ending_March_2026.xlsx
- https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Criminal_Incidents_Year_Ending_March_2026.xlsx

### Alleged offender incidents

Catalogue: https://discover.data.vic.gov.au/dataset/data-tables-alleged-offender-incidents

- https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_Alleged_Offender_Incidents_Visualisation_Year_Ending_March_2026.xlsx
- https://files.crimestatistics.vic.gov.au/2026-06/Data_Tables_LGA_Alleged_Offenders_Year_Ending_March_2026.xlsx

CSA download hub: https://www.crimestatistics.vic.gov.au/crime-statistics/latest-victorian-crime-data/download-data

## Australian Bureau of Statistics

Recorded Crime – Offenders, 2024–25. Released 18 March 2026.

Catalogue: https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/latest-release

- https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/1.%20Offenders%2C%20Australia.xlsx
- https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/2.%20Offenders%2C%20states%20and%20territories.xlsx
- https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/2024-25/3.%20Youth%20offenders.xlsx

## After download

Save the CSA files under the filenames listed in `src/config.py`, or place them in `data/raw/` and run:

```bash
export PYTHONPATH=.
python -m src.pipeline
```

ABS files can use the local names `ABS_Offenders_Australia_2024-25.xlsx`, `ABS_Offenders_States_2024-25.xlsx` and `ABS_Youth_Offenders_2024-25.xlsx` in `data/raw/`.
