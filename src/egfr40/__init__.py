import sys
import builtins
from .logo import *

from .egfr import *
from .convert import *
from .risk import *

detailed_doc = """
CKD-PC 40% eGFR Decline Risk Equation Python Library
========================================================================================

`egfr40` is a Python library that estimates the 3-year probability of a >=40% decline
in eGFR or kidney failure, using the CKD Prognosis Consortium (CKD-PC) risk equation
developed by Grams et al. (Diabetes Care, 2022). The model is stratified by diabetes
status and eGFR (>=60 or <60 mL/min/1.73 m^2) and applies to the general population,
with or without chronic kidney disease. The library scores single individuals or whole
cohorts, explains each individual's risk term by term, and includes helpers for CKD-EPI
2021 eGFR and for converting urine protein-to-creatinine ratio or dipstick protein to
albumin-to-creatinine ratio.

Not affiliated with the CKD Prognosis Consortium. For research use only.

PyPI: https://pypi.org/project/egfr40/
GitHub: https://github.com/lshpaner/egfr40

Version: 0.0.1a3

"""

__author__ = "Leonid Shpaner"
__email__ = "lshpaner@ucla.edu"
__version__ = "0.0.1a3"


# Define the custom help function
def custom_help(obj=None):
    """
    Custom help function to dynamically include ASCII art in help() output.
    """
    if (
        obj is None or obj is sys.modules[__name__]
    ):  # When `help()` is called for this module
        print(egfr40_logo)  # Print ASCII art first
        print(detailed_doc)  # Print the detailed documentation
    else:
        original_help(obj)  # Use the original help for other objects


# Backup the original help function
original_help = builtins.help

# Override the global help function in builtins
builtins.help = custom_help
