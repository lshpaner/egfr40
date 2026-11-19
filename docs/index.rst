Welcome to the egfr40 Python Library Documentation!
===================================================

.. note::

   This documentation is for ``egfr40`` version |version_str|.

``egfr40`` is a Python library that estimates the 3-year probability of a
≥40% decline in estimated glomerular filtration rate (eGFR) or kidney failure,
using the risk equation developed by Grams et al. (2022) for the CKD Prognosis
Consortium (CKD-PC). The model applies to the general population, with or
without chronic kidney disease (CKD). Every coefficient matches the odds ratios
published in the paper, and the risks match the
`ckdpcrisk.org/gfrdecline40 <https://ckdpcrisk.org/gfrdecline40/>`_ calculator
in the diabetes models.

The library scores single patients or entire cohorts, explains each patient's
risk term by term, and includes helpers for CKD-EPI 2021 eGFR and for
converting urine protein-to-creatinine ratio (uPCR) or dipstick protein to
urine albumin-to-creatinine ratio (uACR).

For one patient at a time without writing code, there is also a
`web calculator <https://flask.leonshpaner.com/egfr40_calc/>`_ built on the
library.

.. important::

   ``egfr40`` is not affiliated with the CKD Prognosis Consortium. It is an
   independent implementation of a published equation, intended for research
   use. It is not a medical device and should not be used to make clinical
   decisions.

Prerequisites
-------------

- **Python**: 3.8 or higher
- **numpy**: 1.20 or higher
- **pandas**: 1.3 or higher

Installation
------------

.. code-block:: bash

   pip install egfr40

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started
   _notebooks/00_quickstart

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   usage_guide
   inputs
   egfr
   conversions
   nhanes
   api

.. toctree::
   :maxdepth: 2
   :caption: About egfr40

   model
   contributors
   acknowledgements
   citing
   changelog
   references
