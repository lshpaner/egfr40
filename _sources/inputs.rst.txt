Input Requirements and Common Pitfalls
======================================

Inputs
------

.. list-table::
   :header-rows: 1
   :widths: 30 25 45

   * - Input
     - Argument (column default)
     - Units and accepted values
   * - Age
     - ``age``
     - years; the model was developed in adults
   * - Sex
     - ``male`` (``sex``)
     - 1 = male, 0 = female; columns also accept ``male``/``female``, ``m``/``f``
   * - eGFR
     - ``egfr`` (``eGFR``)
     - mL/min/1.73 m², CKD-EPI 2021 creatinine equation (see :doc:`egfr`)
   * - Urine albumin-to-creatinine ratio
     - ``uacr`` (``uACR``)
     - mg/g, must be greater than 0 (see :doc:`conversions` for mg/mmol, uPCR or dipstick)
   * - Systolic blood pressure
     - ``sbp``
     - mmHg
   * - Antihypertensive medication
     - ``bp_meds``
     - 1/0 (columns also accept yes/no)
   * - History of heart failure
     - ``hf``
     - 1/0
   * - History of coronary heart disease
     - ``chd``
     - 1/0
   * - History of atrial fibrillation
     - ``afib``
     - 1/0
   * - Smoking status
     - ``smoking``
     - ``never``, ``former`` or ``current``
   * - Body mass index
     - ``bmi``
     - kg/m²
   * - Diabetes
     - ``dm``
     - required; selects the diabetes or no-diabetes model
   * - HbA1c
     - ``hba1c``
     - percent (%), diabetes only
   * - Oral diabetes medication
     - ``oral_dm``
     - 1/0, diabetes only
   * - Insulin
     - ``insulin``
     - 1/0, diabetes only

Common pitfalls
---------------

**uACR in mg/mmol.** The model expects mg/g. Values reported in mg/mmol are
about 8.84 times smaller, which understates risk. Convert first with
``acr_mg_mmol_to_mg_g``.

**HbA1c in mmol/mol.** The model expects percent. The paper's tables label
HbA1c "mmol", but the centering at 7 in Supplemental Table S5 shows the unit is
percent. Convert IFCC values with ``% = mmol/mol / 10.929 + 2.15``.

**eGFR from an older equation.** The model was built on CKD-EPI 2021
(race-free) eGFR. eGFR from the 2009 equation or MDRD differs, especially near
the eGFR 60 boundary. Recompute with ``ckd_epi_2021`` when serum creatinine is
available.

**The eGFR 60 boundary.** The two eGFR strata are separate models and do not
meet at 60. Small changes in eGFR around 60 can move risk noticeably. At
exactly 60 the two models are averaged, as on the CKD-PC website.

**Inputs the model does not use.** Race and hypertension status do not appear
in the published equation, so neither is an input here.

**Missing values in cohorts.** ``add_egfr40_risk_col`` returns ``NaN`` for rows
with a missing required input. Count them before summarizing risk, since
complete-case results may not represent the full cohort.
