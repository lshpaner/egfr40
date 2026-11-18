<img src="https://raw.githubusercontent.com/lshpaner/egfr40/main/assets/egfr40_logo.svg" width="300" style="border: none; outline: none; box-shadow: none;" oncontextmenu="return false;">

<br>

[![PyPI](https://img.shields.io/pypi/v/egfr40.svg)](https://pypi.org/project/egfr40/)
[![Downloads](https://static.pepy.tech/badge/egfr40)](https://pepy.tech/project/egfr40)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/lshpaner/egfr40/tree/main?tab=MIT-1-ov-file)

`egfr40` is a Python library designed to estimate the 3-year risk of a ≥40% decline in estimated glomerular filtration rate (eGFR) or kidney failure, using the risk equation developed by Grams et al. for the CKD Prognosis Consortium (CKD-PC). Unlike risk equations restricted to patients with established chronic kidney disease (CKD), this model applies to the general population, with or without CKD. It is stratified by diabetes status and eGFR (≥60 or <60 mL/min/1.73 m²), and reproduces the [ckdpcrisk.org/gfrdecline40](https://ckdpcrisk.org/gfrdecline40/) calculator. The library is tailored for healthcare professionals and researchers, supporting risk predictions for individual patients or entire cohorts.

> **Not affiliated with the CKD Prognosis Consortium.** This is an independent implementation of a published equation, intended for research use. It is not a medical device and should not be used to make clinical decisions.

## Prerequisites
Before you install `egfr40`, ensure you have the following:

- **Python**: Python 3.8 or higher is required to run `egfr40`.

Additionally, `egfr40` has the following package dependencies:

- **numpy**: version 1.20 or higher
- **pandas**: version 1.3 or higher

## Installation

You can install `egfr40` directly from PyPI:

```bash
pip install egfr40
```

## Features

- 3-year risk of ≥40% eGFR decline or kidney failure for one patient or a whole cohort
- Risk explanations: each predictor's contribution to an individual patient's risk
- CKD-EPI 2021 (race-free) eGFR from serum creatinine
- uPCR-to-uACR and urine dipstick-to-uACR estimation, plus uACR unit conversion (see caveat below)
- Verified against the online CKD-PC calculator in all four strata

**Note on uACR estimation:** the uPCR- and dipstick-to-uACR conversions are approximations that carry measurement error; a directly measured uACR is preferred when available.

## Usage

### One patient

```python
from egfr40 import egfr40_risk

egfr40_risk(
    age=70, male=1, egfr=40, uacr=150, sbp=140, bp_meds=1,
    hf=0, chd=1, afib=1, smoking="former", bmi=28,
    dm=True, hba1c=7, oral_dm=0, insulin=0,
)
# 0.166
```

Pass `explain=True` to also get the stratum, the linear predictor, and each predictor's contribution to the log-odds, largest first.

### A whole cohort

```python
from egfr40 import add_egfr40_risk_col

df = add_egfr40_risk_col(
    df,
    age_col="age", sex_col="sex", egfr_col="eGFR", uacr_col="uACR",
    sbp_col="sbp", bp_meds_col="bp_meds",
    hf_col="hf", chd_col="chd", afib_col="afib",
    smoking_col="smoking", bmi_col="bmi",
    dm_col="dm", hba1c_col="hba1c", oral_dm_col="oral_dm", insulin_col="insulin",
)
df["egfr40_3year"]
```

Each row is scored with its own stratum. Rows missing any required input get `NaN`.

### eGFR and uACR helpers

```python
from egfr40 import ckd_epi_2021, pcr_to_acr, dipstick_to_acr, acr_mg_mmol_to_mg_g

ckd_epi_2021(scr=1.2, age=70, male=1)   # mL/min/1.73 m²
pcr_to_acr(150)                         # uPCR (mg/g) -> uACR (mg/g)
dipstick_to_acr("++")                   # dipstick category -> uACR (mg/g)
acr_mg_mmol_to_mg_g(3.0)                # 26.5 mg/g
```

## Inputs

| Input | Units / values |
|---|---|
| Age | years |
| Sex | `male`/`female`, `m`/`f`, or 1 = male / 0 = female |
| eGFR | mL/min/1.73 m², CKD-EPI 2021 creatinine equation |
| uACR | mg/g |
| Systolic BP | mmHg |
| Antihypertensive medication | 1/0 or yes/no |
| History of heart failure, CHD, atrial fibrillation | 1/0 or yes/no |
| Smoking | `never`, `former`, `current` |
| BMI | kg/m² |
| Diabetes | 1/0 or yes/no (**required**: selects the model) |
| HbA1c | % (diabetes only) |
| Oral diabetes medication, insulin | 1/0 or yes/no (diabetes only) |

## Model Notes

- Coefficients, intercepts, and the centering and scaling of each predictor are taken from Supplemental Table S5 of Grams et al. (2022). All coefficients match the odds ratios reported in the paper's Tables 2 and 3.
- The stratified models do not meet at eGFR 60. Following the CKD-PC website, risk at exactly eGFR 60 is the average of the two strata.
- The online calculator also asks for race and hypertension status; neither appears in the published model, so neither is an input here.
- The hypertension-based alternative models (Supplemental Tables S6 and S7) are published without intercepts and cannot be implemented.

## NHANES Example

The repository includes a pipeline that applies the equation to NHANES 2017–March 2020:

```bash
make data_gen     # fetch raw NHANES files into data/raw/
make preprocess   # merge, compute eGFR, recode inputs -> data/processed/
```

See `notebooks/01_score_nhanes.ipynb` for cohort scoring and survey-weighted summaries.

## 🌐 Author Website

https://www.leonshpaner.com

## ⚖️ License

`egfr40` is distributed under the MIT License. See [LICENSE](https://github.com/lshpaner/egfr40/blob/main/LICENSE) for more information.

## 📚 Citing `egfr40`

If you use `egfr40` in your research or projects, please consider citing it, along with the original paper by Grams et al. (2022).

```bibtex
    @software{shpaner_2026_egfr40,
      author       = {Shpaner, Leonid},
      title        = {{egfr40: A Python Library for the CKD Prognosis
                       Consortium 40\% eGFR Decline Risk Equation}},
      month        = nov,
      year         = 2026,
      version      = {0.0.1a2},
      url          = {https://github.com/lshpaner/egfr40}
    }
```

## Support
If you have any questions or issues with `egfr40`, please open an issue on this GitHub repository.

## Acknowledgements
The risk equation developed by Grams et al. for the CKD Prognosis Consortium has made significant contributions to kidney disease research, offering a validated way to predict kidney function decline before it becomes advanced.

The `egfr40` library is based on the risk prediction models developed in the studies referenced below. Please refer to these studies for an in-depth understanding of the models used within this library.

References
===========

1. Grams, M. E., Brunskill, N. J., Ballew, S. H., Sang, Y., Coresh, J., Matsushita, K., Surapaneni, A., Bell, S., Carrero, J. J., Chodick, G., Evans, M., Heerspink, H. J. L., Inker, L. A., Iseki, K., Kalra, P. A., Kirchner, H. L., Lee, B. J., Levin, A., Major, R. W., Medcalf, J., Nadkarni, G. N., Naimark, D. M. J., Ricardo, A. C., Sawhney, S., Sood, M. M., Staplin, N., Stempniewicz, N., Stengel, B., Sumida, K., Traynor, J. P., van den Brand, J., Wen, C.-P., Woodward, M., Yang, J. W., Wang, A. Y.-M., Tangri, N., & for the CKD Prognosis Consortium. (2022). Development and validation of prediction models of adverse kidney outcomes in the population with and without diabetes. *Diabetes Care, 45*(9), 2055–2063. https://doi.org/10.2337/dc22-0698

2. Inker, L. A., Eneanya, N. D., Coresh, J., Tighiouart, H., Wang, D., Sang, Y., Crews, D. C., Doria, A., Estrella, M. M., Froissart, M., Grams, M. E., Greene, T., Grubb, A., Gudnason, V., Gutiérrez, O. M., Kalil, R., Karger, A. B., Mauer, M., Navis, G., Nelson, R. G., et al. (2021). New creatinine- and cystatin C–based equations to estimate GFR without race. *New England Journal of Medicine, 385*(19), 1737–1749. https://doi.org/10.1056/NEJMoa2102953

3. Sumida, K., Nadkarni, G. N., Grams, M. E., Sang, Y., Ballew, S. H., Coresh, J., Matsushita, K., Surapaneni, A., Brunskill, N., Chadban, S. J., Chang, A. R., Cirillo, M., Daratha, K. B., Gansevoort, R. T., Garg, A. X., Iacoviello, L., Kayama, T., Konta, T., Kovesdy, C. P., Lash, J., Lee, B. J., Major, R. W., Metzger, M., Miura, K., Naimark, D. M. J., Nelson, R. G., Sawhney, S., Stempniewicz, N., Tang, M., Townsend, R. R., Traynor, J. P., Valdivielso, J. M., Wetzels, J., Polkinghorne, K. R., & Heerspink, H. J. L. (2020). Conversion of urine protein-creatinine ratio or urine dipstick protein to urine albumin-creatinine ratio for use in chronic kidney disease screening and prognosis. *Annals of Internal Medicine, 173*(6), 426–435. https://doi.org/10.7326/M20-0529
