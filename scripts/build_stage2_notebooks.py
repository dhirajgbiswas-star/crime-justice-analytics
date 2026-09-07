"""Add Stage 2 notebooks."""

from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def md(source: str):
    return nbf.v4.new_markdown_cell(source.strip())


def code(source: str):
    return nbf.v4.new_code_cell(source.strip())


def write(name: str, cells: list) -> None:
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    nb["cells"] = cells
    nbf.write(nb, NOTEBOOKS / name)
    print(NOTEBOOKS / name)


write(
    "09_criminal_incidents.ipynb",
    [
        md("""
# 09 Criminal incidents

## Objective
Analyse CSA criminal incidents as a separate statistical product from recorded offences.

## Data source
https://discover.data.vic.gov.au/dataset/criminal-incident

## Business questions
How do criminal incidents compare with recorded offences? Which charge statuses dominate? Which LGAs have the highest incident rates?
"""),
        code("""
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd().parents[0] if Path.cwd().name == 'notebooks' else Path.cwd()))
from src.analytics.incidents import (
    charge_status_share, latest_lga_incidents, statewide_incident_totals, statistical_product_comparison
)
from src.analytics.visualisation import plot_charge_status, plot_incident_trend, plot_statistical_products
display(statewide_incident_totals())
display(statistical_product_comparison())
display(charge_status_share().query('year == year.max()'))
display(latest_lga_incidents().head(10))
plot_statistical_products()
plot_incident_trend()
plot_charge_status()
"""),
        md("""
## Limitations
A criminal incident can contain more than one recorded offence. Charge status is administrative, not a court outcome.
"""),
    ],
)

write(
    "10_offender_analysis.ipynb",
    [
        md("""
# 10 Alleged offender analysis

## Objective
Describe alleged offender incidents by principal offence, age, sex and youth status.

## Data source
https://discover.data.vic.gov.au/dataset/data-tables-alleged-offender-incidents

## Business questions
15-18. Principal offence, age, sex and youth trends. These are alleged incidents, not unique people and not proven offences.
"""),
        code("""
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd().parents[0] if Path.cwd().name == 'notebooks' else Path.cwd()))
from src.analytics.offender import (
    age_sex_distribution, principal_offence_latest, sex_distribution,
    statewide_offender_totals, youth_single_year_of_age, youth_vs_adult
)
from src.analytics.visualisation import (
    plot_age_distribution, plot_offender_trend, plot_sex_distribution,
    plot_youth_single_year, plot_youth_trend
)
display(statewide_offender_totals())
display(principal_offence_latest().head(12))
display(sex_distribution())
display(youth_vs_adult())
display(age_sex_distribution().head(20))
display(youth_single_year_of_age())
plot_offender_trend()
plot_sex_distribution()
plot_age_distribution()
plot_youth_trend()
plot_youth_single_year()
"""),
        md("""
## Limitations
ABS national offender comparison is not loaded in this stage. Youth is CSA ages 10-17. Unknown sex/age and organisations are excluded from sex/age charts as documented in CSA footnotes.
"""),
    ],
)
