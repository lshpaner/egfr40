NHANES Example
==============

The repository includes a pipeline that applies the equation to the National
Health and Nutrition Examination Survey (NHANES) 2017–March 2020 pre-pandemic
cycle. It lives in the repository, not the installed package.

.. code-block:: bash

   git clone https://github.com/lshpaner/egfr40.git
   cd egfr40
   pip install -e ".[nhanes]"
   make data_gen     # fetch the raw NHANES files into data/raw/
   make preprocess   # merge, compute eGFR, recode -> data/processed/

``notebooks/01_score_nhanes.ipynb`` then scores the cohort and produces
survey-weighted risk summaries by stratum.

How NHANES variables are coded
------------------------------

.. list-table::
   :header-rows: 1

   * - Input
     - NHANES source and coding
   * - eGFR
     - CKD-EPI 2021 from serum creatinine (``LBXSCR``)
   * - uACR
     - ``URDACT``, mg/g
   * - Systolic BP
     - mean of up to three oscillometric readings (``BPXOSY1``-``3``)
   * - Antihypertensive medication
     - ``BPQ050A`` (now taking), falling back to ``BPQ040A``; people never told
       they have hypertension are coded 0
   * - Heart failure
     - self-reported (``MCQ160B``)
   * - CHD
     - self-reported coronary heart disease (``MCQ160C``) or heart attack
       (``MCQ160E``)
   * - Atrial fibrillation
     - not collected in NHANES; set to 0
   * - Smoking
     - fewer than 100 lifetime cigarettes = never; smoking now (every day or
       some days) = current; quit = former
   * - Diabetes
     - self-reported diagnosis, insulin or diabetes pills, or HbA1c ≥6.5%

The analysis includes adults aged 20 to 80 who are not pregnant, have eGFR ≥15
and have complete model inputs.

Prior work
----------

The 3-year risk distribution in U.S. adults has already been described with
NHANES 1999–2020 in *Individualized Risk of CKD Progression among US Adults*
(*Journal of the American Society of Nephrology*,
`doi:10.1681/ASN.0000000000000377 <https://doi.org/10.1681/ASN.0000000000000377>`_). The ``egfr40`` pipeline reproduces that kind of analysis and is
intended as a worked, reproducible example.
