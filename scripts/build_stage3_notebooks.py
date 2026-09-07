"""Add the Stage 3 national-comparison notebook."""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def md(source: str):
    return nbf.v4.new_markdown_cell(source.strip())


def code(source: str):
    return nbf.v4.new_code_cell(source.strip())


nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}
nb["cells"] = [
    md(
        """
# 11 ABS Recorded Crime – Offenders

## Objective
Compare Victoria with Australia and other jurisdictions using the official ABS unique-offender measure.

## Data source
https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-offenders/latest-release

## Business questions
How does Victoria’s offender *rate* compare with other states? How has the Victorian series moved since 2008–09? What share of Victorian offenders are aged 10–17?

## Critical caveat
ABS unique alleged offenders proceeded against (financial year) are **not** CSA alleged offender incidents (year ending March).
"""
    ),
    code(
        """
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd().parents[0] if Path.cwd().name == 'notebooks' else Path.cwd()))
from src.analytics.national import (
    abs_product_caveat,
    abs_state_totals_latest,
    abs_victoria_persons_trend,
    abs_victoria_vs_australia,
    abs_victoria_youth_trend,
    abs_youth_by_state_latest,
    csa_vs_abs_product_note,
)
from src.analytics.visualisation import (
    plot_abs_state_rates,
    plot_abs_victoria_australia_trend,
    plot_abs_victoria_offence_mix,
    plot_abs_youth_trend,
)
print(abs_product_caveat())
display(abs_victoria_vs_australia())
display(abs_state_totals_latest())
display(csa_vs_abs_product_note())
display(abs_victoria_persons_trend().tail())
display(abs_victoria_youth_trend().tail())
display(abs_youth_by_state_latest())
plot_abs_state_rates()
plot_abs_victoria_australia_trend()
plot_abs_victoria_offence_mix()
plot_abs_youth_trend()
"""
    ),
    md(
        """
## Limitations
ABS cells are randomly adjusted for confidentiality. Rates use persons aged 10 years and over. Do not calculate a clearance rate by dividing CSA incidents into ABS offenders.
"""
    ),
]
nbf.write(nb, NOTEBOOKS / "11_abs_national_comparison.ipynb")
print(NOTEBOOKS / "11_abs_national_comparison.ipynb")
