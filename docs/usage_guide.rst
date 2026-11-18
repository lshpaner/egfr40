Usage Guide
===========

Single patient: ``egfr40_risk``
-------------------------------

``egfr40_risk`` returns the 3-year probability (0 to 1) for one patient.

.. code-block:: python

   from egfr40 import egfr40_risk

   risk = egfr40_risk(
       age=58, male=1, egfr=82, uacr=40, sbp=138, bp_meds=1,
       hf=0, chd=0, afib=0, smoking="current", bmi=31,
       dm=True, hba1c=8.0, oral_dm=1, insulin=0,
   )

``dm`` is required and has no default. It selects the diabetes or
no-diabetes model, and leaving it implicit made it too easy to score a
diabetic patient with the wrong model. When ``dm=True``, ``hba1c`` is required.

Explaining a patient's risk
---------------------------

Pass ``explain=True`` to get a breakdown instead of a single number:

.. code-block:: python

   out = egfr40_risk(
       age=70, male=1, egfr=40, uacr=150, sbp=140, bp_meds=1,
       hf=0, chd=1, afib=1, smoking="former", bmi=28,
       dm=True, hba1c=7, explain=True,
   )

   out["risk"]              # 0.166
   out["stratum"]           # 'DM, eGFR <60'
   out["linear_predictor"]  # log-odds
   out["contributions"]     # {'uacr': 1.261, 'chd': 0.185, 'age': -0.172, ...}

Each value in ``contributions`` is that predictor's effect on the log-odds,
listed largest first. Positive values raise risk and negative values lower it,
relative to the model's reference patient: age 60, uACR 10 mg/g, systolic BP
130 mmHg, BMI 30 kg/m², and eGFR at the center of its stratum (85 or 45).

Heart failure and coronary heart disease are centered at 0.05 and 0.15 in the
published model, so a patient without either still gets a small negative
contribution for each.

At exactly eGFR 60 the risk is an average of two models (see :doc:`model`), so
``explain=True`` returns both breakdowns under ``"strata"``.

Cohorts: ``add_egfr40_risk_col``
--------------------------------

``add_egfr40_risk_col`` adds a risk column to a DataFrame, scoring each row
with its own stratum.

.. code-block:: python

   from egfr40 import add_egfr40_risk_col

   df = add_egfr40_risk_col(
       df,
       age_col="age", sex_col="sex", egfr_col="eGFR", uacr_col="uACR",
       sbp_col="sbp", bp_meds_col="bp_meds",
       hf_col="hf", chd_col="chd", afib_col="afib",
       smoking_col="smoking", bmi_col="bmi",
       dm_col="dm", hba1c_col="hba1c",
       oral_dm_col="oral_dm", insulin_col="insulin",
       risk_col="egfr40_3year",
   )

The arguments shown are the defaults, so a DataFrame that already uses these
column names needs only ``add_egfr40_risk_col(df)``.

The function:

- accepts text or numeric codes (``"male"``/``"female"`` or 1/0;
  ``"yes"``/``"no"`` or 1/0)
- returns ``NaN`` for any row with a missing required input, rather than
  guessing
- requires HbA1c and the diabetes medication columns only for rows with
  diabetes
- raises an error for unrecognized smoking or yes/no values
- returns a copy by default (``copy=True``) and leaves the input unchanged
