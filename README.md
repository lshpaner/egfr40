# egfr40

Python implementation of the CKD Prognosis Consortium (CKD-PC) risk equation for the
**3-year probability of a ≥40% decline in eGFR or kidney failure**, from Grams et al.,
*Diabetes Care* 2022. This is the equation behind the
[ckdpcrisk.org/gfrdecline40](https://ckdpcrisk.org/gfrdecline40/) calculator.

> **Not affiliated with the CKD Prognosis Consortium.** This is an independent
> implementation of a published equation, intended for research use. It is not a
> medical device and should not be used to make clinical decisions.

## Installation

```bash
pip install egfr40
```

Development install:

```bash
git clone https://github.com/lshpaner/egfr40.git
cd egfr40
pip install -e ".[dev]"
```

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

## The model

Four logistic models, stratified by diabetes status and eGFR (≥60 or <60):

$$
p = \frac{1}{1 + e^{-(\beta_0 + \sum_i \beta_i x_i)}}
$$

Coefficients, intercepts, and the centering and scaling of each predictor are taken from
**Supplemental Table S5** of the paper. All 52 coefficients match the model 2 odds
ratios reported in Tables 2 and 3, and the package reproduces the online calculator.

**eGFR = 60 boundary.** The stratified models do not meet at eGFR 60. Following the
CKD-PC website, risk at exactly eGFR 60 is the average of the two strata.

**Notes on the source**

- The calculator also asks for race and hypertension status. Neither appears in the
  published Table S5 model, so neither is an input here.
- The hypertension-based alternative models (Supplemental Tables S6 and S7) are published
  without intercepts and cannot be implemented.
- HbA1c is labeled "mmol" in the paper's tables. Its centering at 7 in Table S5 shows the
  unit is percent.

## Testing

```bash
make test
```

The tests check the coefficients against the paper's odds ratios, a case verified
against the online calculator, the eGFR 60 averaging, and agreement between the
single-patient and DataFrame functions.

## NHANES example

`data_gen.py` downloads the raw NHANES 2017–March 2020 pre-pandemic files needed to apply
the equation to a nationally representative sample:

```bash
pip install -e ".[nhanes]"
make data_gen
```

Files are saved to `data/raw/` (gitignored). NHANES does not record atrial fibrillation.

## Citation

If you use this package, please cite the original paper:

> Grams ME, Brunskill NJ, Ballew SH, et al. Development and Validation of Prediction
> Models of Adverse Kidney Outcomes in the Population With and Without Diabetes.
> *Diabetes Care*. 2022;45(9):2055-2063. doi:10.2337/dc22-0698

## License

MIT
