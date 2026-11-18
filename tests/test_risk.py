import math

import numpy as np
import pandas as pd
import pytest

from egfr40 import add_egfr40_risk_col, egfr40_risk
from egfr40.risk import _COEFS

# Model 2 odds ratios from Tables 2 and 3 of Grams et al. 2022 (rounded to 2 dp)
KEYS = ["age", "male", "egfr", "lnacr", "sbp", "bpmed", "sbp_bpmed", "hf", "chd",
        "afib", "current_smoker", "former_smoker", "bmi"]
PAPER_OR = {
    (True, False): [1.45, 0.87, 1.03, 1.52, 1.36, 1.30, 0.89, 2.87, 1.51, 1.12, 1.46, 1.20, 1.04],
    (True, True): [1.16, 0.78, 0.95, 1.51, 1.16, 1.33, 0.97, 2.52, 1.24, 1.36, 1.13, 1.08, 1.03],
    (False, False): [0.92, 1.06, 0.85, 1.48, 1.27, 1.08, 0.98, 1.63, 1.26, 1.08, 1.34, 1.19, 0.98],
    (False, True): [0.84, 0.86, 0.93, 1.59, 1.23, 1.18, 0.95, 1.52, 1.24, 1.05, 0.97, 1.15, 1.03],
}

SITE_CASE = dict(age=70, male=1, egfr=40, uacr=150, sbp=140, bp_meds=1, hf=0, chd=1,
                 afib=1, smoking="former", bmi=28, dm=True, hba1c=7, oral_dm=0, insulin=0)


@pytest.mark.parametrize("stratum", list(PAPER_OR))
def test_coefficients_match_paper_odds_ratios(stratum):
    for key, odds in zip(KEYS, PAPER_OR[stratum]):
        assert round(math.exp(_COEFS[stratum][key]), 2) == pytest.approx(odds, abs=0.011), key


def test_matches_ckdpcrisk_site():
    # Verified against ckdpcrisk.org/gfrdecline40 on 2026-11-17: 16.6%
    assert round(egfr40_risk(**SITE_CASE), 3) == 0.166


@pytest.mark.parametrize("case,expected", [
    # Diabetes, eGFR >= 60, oral meds (verified on the site 2026-11-18: 3.2%)
    (dict(age=60, male=1, egfr=80, uacr=30, sbp=140, bp_meds=1, hf=0, chd=0, afib=0,
          smoking="current", bmi=30, dm=True, hba1c=8, oral_dm=1, insulin=0), 0.032),
    # Diabetes, eGFR >= 60, insulin (verified on the site 2026-11-18: 12.1%)
    (dict(age=45, male=0, egfr=100, uacr=300, sbp=150, bp_meds=1, hf=0, chd=0, afib=1,
          smoking="never", bmi=35, dm=True, hba1c=9, oral_dm=0, insulin=1), 0.121),
])
def test_matches_ckdpcrisk_site_dm_high_egfr(case, expected):
    assert round(egfr40_risk(**case), 3) == expected


def test_dm_is_required():
    kw = {k: v for k, v in SITE_CASE.items() if k not in ("dm", "hba1c", "oral_dm", "insulin")}
    with pytest.raises(TypeError):
        egfr40_risk(**kw)


def test_dm_requires_hba1c():
    with pytest.raises(ValueError):
        egfr40_risk(**{**SITE_CASE, "hba1c": None})


def test_egfr_60_averages_strata():
    kw = {**SITE_CASE, "dm": False, "hba1c": None}
    at_60 = egfr40_risk(**{**kw, "egfr": 60})
    above = egfr40_risk(**{**kw, "egfr": 60.0000001})
    below = egfr40_risk(**{**kw, "egfr": 59.9999999})
    assert at_60 == pytest.approx((above + below) / 2, abs=1e-6)


def _synthetic_cohort(n=500, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "age": rng.integers(20, 81, n),
        "sex": rng.choice(["male", "female"], n),
        "eGFR": rng.integers(15, 120, n).astype(float),
        "uACR": np.round(np.exp(rng.normal(3, 1.5, n)), 1) + 0.1,
        "sbp": rng.integers(100, 180, n),
        "bp_meds": rng.integers(0, 2, n),
        "hf": rng.integers(0, 2, n),
        "chd": rng.integers(0, 2, n),
        "afib": rng.integers(0, 2, n),
        "smoking": rng.choice(["never", "former", "current"], n),
        "bmi": rng.uniform(18, 45, n),
        "dm": rng.integers(0, 2, n),
    })
    df["hba1c"] = np.where(df.dm == 1, rng.uniform(5.5, 11, n), np.nan)
    df["oral_dm"] = np.where(df.dm == 1, rng.integers(0, 2, n), 0)
    df["insulin"] = np.where(df.dm == 1, rng.integers(0, 2, n), 0)
    df.loc[:4, "eGFR"] = 60
    return df


def test_dataframe_matches_scalar():
    df = _synthetic_cohort()
    scored = add_egfr40_risk_col(df)
    scalar = [
        egfr40_risk(age=r.age, male=int(r.sex == "male"), egfr=r.eGFR, uacr=r.uACR,
                    sbp=r.sbp, bp_meds=r.bp_meds, hf=r.hf, chd=r.chd, afib=r.afib,
                    smoking=r.smoking, bmi=r.bmi, dm=bool(r.dm),
                    hba1c=r.hba1c if r.dm else None, oral_dm=r.oral_dm, insulin=r.insulin)
        for r in df.itertuples()
    ]
    np.testing.assert_allclose(scored["egfr40_3year"], scalar, atol=1e-12)


def test_dataframe_missing_inputs_give_nan():
    df = _synthetic_cohort(n=3)
    df.loc[0, "sbp"] = np.nan
    df.loc[1, ["dm", "hba1c"]] = [1, np.nan]
    scored = add_egfr40_risk_col(df)
    assert scored["egfr40_3year"].iloc[:2].isna().all()


def test_dataframe_rejects_bad_smoking():
    df = _synthetic_cohort(n=3)
    df.loc[0, "smoking"] = "sometimes"
    with pytest.raises(ValueError):
        add_egfr40_risk_col(df)


def test_dataframe_does_not_modify_input_by_default():
    df = _synthetic_cohort(n=5)
    add_egfr40_risk_col(df)
    assert "egfr40_3year" not in df.columns
