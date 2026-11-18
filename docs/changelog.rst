Changelog
=========

Version 0.0.1a2 (unreleased)
----------------------------

- ``egfr40_risk(..., explain=True)`` returns the stratum, linear predictor and
  each predictor's contribution to the log-odds.
- New conversions: ``pcr_to_acr`` and ``dipstick_to_acr`` (Sumida et al. 2020),
  and ``acr_mg_mmol_to_mg_g`` / ``acr_mg_g_to_mg_mmol``.
- Package moved to a ``src/`` layout; ``help(egfr40)`` prints a library
  overview.
- Supported Python versions widened to 3.8 and higher; tested on 3.8 to 3.13.
- Two more test cases verified against the online calculator (diabetes,
  eGFR ≥60).
- Logo, README and Zenodo archiving.

Version 0.0.1a1 (2026-11-18)
----------------------------

- First alpha release.
- ``egfr40_risk`` and ``add_egfr40_risk_col``: 3-year risk of ≥40% eGFR decline
  or kidney failure, from Supplemental Table S5 of Grams et al. (2022).
- ``ckd_epi_2021``: race-free CKD-EPI 2021 eGFR.
- ``dm`` made a required argument so the model is always chosen explicitly.
