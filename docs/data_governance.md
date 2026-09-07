# Data governance

This project uses publicly released Crime Statistics Agency and Australian Bureau of Statistics aggregates.

The full ethics, stakeholder, north-star and recommendation brief is in [`ethics_governance_and_decisions.md`](ethics_governance_and_decisions.md).

## Operating rules

- Analyse recorded offences, criminal incidents, alleged offender incidents and ABS unique offenders as separate statistical products.
- Do not attempt to identify victims, alleged offenders or private individuals.
- Do not build individual-level profiles.
- CSA confidentialises some homicide and sexual-offence counts of 3 or fewer.
- ABS randomly adjusts cells to protect confidentiality.
- Alleged offender incidents include unknown sex/age in some tables; those rows are documented in CSA footnotes.
- Correlation is not causation. Changes can reflect recording practice, legislation, policing and reporting behaviour.
- Attribute the Crime Statistics Agency and the Australian Bureau of Statistics under CC BY 4.0.
- Indigenous-status cubes were not ingested.
- Official workbooks and processed extracts are not stored in git. Use the download links in `data/README.md`.
