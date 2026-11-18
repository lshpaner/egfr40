The Model
=========

Outcome
-------

The model predicts a composite of a ≥40% decline in eGFR or kidney failure
(receipt of kidney replacement therapy) over 2 to 3 years. A 40% eGFR decline
is accepted as a surrogate kidney endpoint by the U.S. Food and Drug
Administration and the European Medicines Agency.

Development
-----------

Grams et al. (2022) developed the model in an individual participant data
meta-analysis of 1,621,817 participants from 43 cohorts in the CKD Prognosis
Consortium. A logistic regression was fit in each development cohort and the
estimates were pooled by random-effects meta-analysis. Separate models were fit
within four strata: diabetes or not, and eGFR ≥60 or <60 mL/min/1.73 m².

``egfr40`` implements model 2 from the paper, the version used by the online
calculator. Model 3 adds the prior 2-year eGFR slope and improved
discrimination only slightly, so it is not included.

The equation
------------

For each stratum,

.. math::

   p = \frac{1}{1 + e^{-\left(\beta_0 + \sum_i \beta_i x_i\right)}}

where :math:`\beta_0` is the stratum's intercept and each :math:`x_i` is a
predictor after the centering and scaling shown below.

.. include:: _coef_table.rst.inc

.. [#E] E = 85 in the eGFR ≥60 strata and 45 in the eGFR <60 strata.

Every coefficient matches the odds ratios reported in the paper's Tables 2 and
3 (``exp(β)`` agrees to two decimals), and the package reproduces the online
calculator in all four strata.

The eGFR 60 boundary
--------------------

Because the strata are separate models, predicted risk jumps at eGFR 60. For a
60-year-old man with uACR 10 mg/g, SBP 130 and no other risk factors, the risk
is 0.64% at eGFR 61 and 1.89% at eGFR 59. Following the CKD-PC website, risk at
exactly eGFR 60 is the average of the two models.

What is not implemented
-----------------------

- **Hypertension-based models** (Supplemental Tables S6 and S7) are published
  without intercepts, so absolute risk cannot be computed.
- **30% and 50% decline models** (Supplemental Tables S8 to S11) are also
  published without intercepts.
- **Race and hypertension status** do not appear in the published equation.
- **Risk thresholds** such as "high risk" are not defined in the paper, so the
  package reports probabilities only.

Discrimination
--------------

Median C statistics of model 2 in the validation cohorts were 0.740 (eGFR ≥60,
no diabetes), 0.774 (eGFR ≥60, diabetes), 0.750 (eGFR <60, no diabetes) and
0.769 (eGFR <60, diabetes).
