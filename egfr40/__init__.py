"""egfr40: CKD-PC risk equation for a >=40% eGFR decline or kidney failure.

Implements Grams ME et al., Diabetes Care 2022;45(9):2055-2063
(doi:10.2337/dc22-0698), Supplemental Table S5.
"""

from .egfr import ckd_epi_2021
from .risk import add_egfr40_risk_col, egfr40_risk

__version__ = "0.0.1a1"

__all__ = ["egfr40_risk", "add_egfr40_risk_col", "ckd_epi_2021", "__version__"]
