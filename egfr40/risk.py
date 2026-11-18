import math

import numpy as np
import pandas as pd

# CKD-PC 40% eGFR decline risk equation (3-year probability)
# Grams ME et al. Diabetes Care 2022;45(9):2055-2063, Supplemental Table S5
# Strata keyed by (eGFR >= 60, diabetes)
_COEFS = {
    (True, False): {
        "const": -4.7045, "age": 0.3690, "male": -0.1433, "egfr": 0.0325,
        "lnacr": 0.4190, "sbp": 0.3048, "bpmed": 0.2656, "sbp_bpmed": -0.1140,
        "hf": 1.0534, "chd": 0.4102, "afib": 0.1140, "current_smoker": 0.3803,
        "former_smoker": 0.1862, "bmi": 0.0425,
    },
    (True, True): {
        "const": -4.2125, "age": 0.1465, "male": -0.2481, "egfr": -0.0562,
        "lnacr": 0.4098, "sbp": 0.1518, "bpmed": 0.2846, "sbp_bpmed": -0.0321,
        "hf": 0.9234, "chd": 0.2168, "afib": 0.3087, "current_smoker": 0.1186,
        "former_smoker": 0.0777, "bmi": 0.0308,
        "hba1c": 0.0987, "oral_dm": -0.0638, "insulin": 0.2359,
    },
    (False, False): {
        "const": -3.4540, "age": -0.0796, "male": 0.0626, "egfr": -0.1672,
        "lnacr": 0.3915, "sbp": 0.2373, "bpmed": 0.0790, "sbp_bpmed": -0.0214,
        "hf": 0.4898, "chd": 0.2343, "afib": 0.0739, "current_smoker": 0.2903,
        "former_smoker": 0.1725, "bmi": -0.0231,
    },
    (False, True): {
        "const": -3.2874, "age": -0.1725, "male": -0.1452, "egfr": -0.0769,
        "lnacr": 0.4658, "sbp": 0.2068, "bpmed": 0.1665, "sbp_bpmed": -0.0549,
        "hf": 0.4216, "chd": 0.2173, "afib": 0.0456, "current_smoker": -0.0338,
        "former_smoker": 0.1386, "bmi": 0.0253,
        "hba1c": -0.0031, "oral_dm": -0.1232, "insulin": 0.0980,
    },
}


def _contributions(high_egfr, dm, x):
    """Each term's contribution to the linear predictor (log-odds) for one stratum."""
    b = _COEFS[(high_egfr, dm)]
    egfr_center = 85 if high_egfr else 45
    sbp_c = (x["sbp"] - 130) / 20
    terms = {
        "age": b["age"] * (x["age"] - 60) / 10,
        "sex": b["male"] * (x["male"] - 0.5),
        "egfr": b["egfr"] * (x["egfr"] - egfr_center) / 5,
        "uacr": b["lnacr"] * math.log(x["uacr"] / 10),
        "sbp": b["sbp"] * sbp_c,
        "bp_meds": b["bpmed"] * x["bp_meds"],
        "sbp_x_bp_meds": b["sbp_bpmed"] * sbp_c * x["bp_meds"],
        "hf": b["hf"] * (x["hf"] - 0.05),
        "chd": b["chd"] * (x["chd"] - 0.15),
        "afib": b["afib"] * x["afib"],
        "smoking": (b["current_smoker"] * (x["smoking"] == "current")
                    + b["former_smoker"] * (x["smoking"] == "former")),
        "bmi": b["bmi"] * (x["bmi"] - 30) / 5,
    }
    if dm:
        terms["hba1c"] = b["hba1c"] * (x["hba1c"] - 7)
        terms["oral_dm"] = b["oral_dm"] * x["oral_dm"]
        terms["insulin"] = b["insulin"] * x["insulin"]
    return b["const"], terms


def _stratum_explain(high_egfr, dm, x):
    const, terms = _contributions(high_egfr, dm, x)
    lp = const + sum(terms.values())
    return {
        "risk": 1 / (1 + math.exp(-lp)),
        "stratum": f"{'DM' if dm else 'No DM'}, eGFR {'>=60' if high_egfr else '<60'}",
        "intercept": const,
        "linear_predictor": lp,
        "contributions": dict(sorted(terms.items(), key=lambda kv: -abs(kv[1]))),
    }


def _stratum_risk(high_egfr, dm, x):
    return _stratum_explain(high_egfr, dm, x)["risk"]


def egfr40_risk(
    age,
    male,
    egfr,
    uacr,
    sbp,
    bp_meds,
    hf,
    chd,
    afib,
    smoking,
    bmi,
    dm,
    hba1c=None,
    oral_dm=0,
    insulin=0,
    explain=False,
):
    """3-year probability of >=40% eGFR decline or kidney failure.

    Parameters
    ----------
    age : float          years
    male : int           1 = male, 0 = female
    egfr : float         CKD-EPI 2021, mL/min/1.73 m^2
    uacr : float         urine albumin-to-creatinine ratio, mg/g
    sbp : float          systolic blood pressure, mmHg
    bp_meds : int        antihypertensive medication use (1/0)
    hf, chd, afib : int  history of heart failure, CHD, atrial fibrillation (1/0)
    smoking : str        'never', 'former', or 'current'
    bmi : float          kg/m^2
    dm : bool            diabetes (required: selects the diabetes or no-diabetes model)
    hba1c : float        %, required when dm is True
    oral_dm : int        oral diabetes medication (1/0)
    insulin : int        insulin use (1/0)
    explain : bool       return a breakdown instead of just the risk

    Returns
    -------
    float in [0, 1]. At eGFR == 60 the two strata are averaged, as on
    ckdpcrisk.org.

    With explain=True, a dict: risk, stratum, intercept, linear_predictor
    (log-odds) and contributions (each term's log-odds contribution, largest
    first; positive raises risk relative to the reference patient: age 60,
    eGFR at the stratum center (85 or 45), uACR 10 mg/g, SBP 130, BMI 30,
    HbA1c 7%, never smoker, no BP or diabetes meds, and HF and CHD at their
    centering values of 0.05 and 0.15, so a patient without HF or CHD gets a
    small negative contribution for each). At eGFR == 60, a dict with the averaged risk and both strata.
    """
    if dm and hba1c is None:
        raise ValueError("hba1c is required when dm=True")
    if uacr <= 0:
        raise ValueError("uacr must be > 0")
    if smoking not in ("never", "former", "current"):
        raise ValueError("smoking must be 'never', 'former', or 'current'")

    x = dict(
        age=age, male=male, egfr=egfr, uacr=uacr, sbp=sbp, bp_meds=bp_meds,
        hf=hf, chd=chd, afib=afib, smoking=smoking, bmi=bmi,
        hba1c=hba1c, oral_dm=oral_dm, insulin=insulin,
    )

    if egfr == 60:
        hi, lo = _stratum_explain(True, dm, x), _stratum_explain(False, dm, x)
        risk = (hi["risk"] + lo["risk"]) / 2
        if explain:
            return {"risk": risk, "stratum": "averaged at eGFR 60", "strata": [hi, lo]}
        return risk
    out = _stratum_explain(egfr > 60, dm, x)
    return out if explain else out["risk"]


def _to_binary(s, name):
    """Coerce a yes/no column to 1.0/0.0 (NaN stays NaN)."""
    if s.dtype == object or pd.api.types.is_string_dtype(s):
        m = s.astype(str).str.strip().str.lower()
        out = pd.Series(np.nan, index=s.index)
        out[m.isin(["1", "yes", "y", "true", "t"])] = 1.0
        out[m.isin(["0", "no", "n", "false", "f"])] = 0.0
        bad = s.notna() & out.isna()
        if bad.any():
            raise ValueError(f"Unrecognized values in '{name}': {s[bad].unique()[:5]}")
        return out
    return s.astype(float)


def _to_male(s):
    """Coerce a sex column (text or 1/0) to 1.0 = male, 0.0 = female."""
    if s.dtype == object or pd.api.types.is_string_dtype(s):
        m = s.astype(str).str.strip().str.lower()
        out = pd.Series(np.nan, index=s.index)
        out[m.isin(["male", "m", "1"])] = 1.0
        out[m.isin(["female", "f", "0"])] = 0.0
        return out
    return s.astype(float)


def _lp_vectorized(high_egfr, dm, d):
    """Linear predictor for one stratum, applied to every row of d."""
    b = _COEFS[(high_egfr, dm)]
    egfr_center = 85 if high_egfr else 45
    sbp_c = (d["sbp"] - 130) / 20

    lp = (
        b["const"]
        + b["age"] * (d["age"] - 60) / 10
        + b["male"] * (d["male"] - 0.5)
        + b["egfr"] * (d["egfr"] - egfr_center) / 5
        + b["lnacr"] * np.log(d["uacr"] / 10)
        + b["sbp"] * sbp_c
        + b["bpmed"] * d["bp_meds"]
        + b["sbp_bpmed"] * sbp_c * d["bp_meds"]
        + b["hf"] * (d["hf"] - 0.05)
        + b["chd"] * (d["chd"] - 0.15)
        + b["afib"] * d["afib"]
        + b["current_smoker"] * d["current"]
        + b["former_smoker"] * d["former"]
        + b["bmi"] * (d["bmi"] - 30) / 5
    )
    if dm:
        lp = (
            lp
            + b["hba1c"] * (d["hba1c"] - 7)
            + b["oral_dm"] * d["oral_dm"]
            + b["insulin"] * d["insulin"]
        )
    return lp


def add_egfr40_risk_col(
    df,
    age_col="age",
    sex_col="sex",
    egfr_col="eGFR",
    uacr_col="uACR",
    sbp_col="sbp",
    bp_meds_col="bp_meds",
    hf_col="hf",
    chd_col="chd",
    afib_col="afib",
    smoking_col="smoking",
    bmi_col="bmi",
    dm_col="dm",
    hba1c_col="hba1c",
    oral_dm_col="oral_dm",
    insulin_col="insulin",
    risk_col="egfr40_3year",
    copy=True,
):
    """Add the CKD-PC 3-year >=40% eGFR decline risk to every row of a DataFrame.

    Each row is scored with its own stratum (eGFR >= 60 or < 60, with or
    without diabetes). Rows at exactly eGFR 60 get the average of the two
    eGFR strata, as on ckdpcrisk.org.

    Column expectations
    -------------------
    sex      : 'male'/'female' (or 'm'/'f'), or 1 = male / 0 = female
    yes/no   : bp_meds, hf, chd, afib, dm, oral_dm, insulin as 1/0 or yes/no
    smoking  : 'never', 'former', or 'current'
    uACR     : mg/g; eGFR: CKD-EPI 2021; HbA1c: %

    Missing values: a row with any required input missing gets NaN.
    HbA1c, oral_dm and insulin are only required for rows with dm == 1.
    Missing oral_dm / insulin in diabetic rows are treated as NaN (not 0).

    Returns
    -------
    DataFrame with a new column `risk_col` (probability in [0, 1]).
    """
    out = df.copy() if copy else df

    smk = out[smoking_col].astype(str).str.strip().str.lower()
    smk = smk.where(out[smoking_col].notna())
    bad_smk = smk.notna() & ~smk.isin(["never", "former", "current"])
    if bad_smk.any():
        raise ValueError(
            f"Unrecognized values in '{smoking_col}': {out.loc[bad_smk, smoking_col].unique()[:5]}"
        )

    d = pd.DataFrame(
        {
            "age": out[age_col].astype(float),
            "male": _to_male(out[sex_col]),
            "egfr": out[egfr_col].astype(float),
            "uacr": out[uacr_col].astype(float),
            "sbp": out[sbp_col].astype(float),
            "bp_meds": _to_binary(out[bp_meds_col], bp_meds_col),
            "hf": _to_binary(out[hf_col], hf_col),
            "chd": _to_binary(out[chd_col], chd_col),
            "afib": _to_binary(out[afib_col], afib_col),
            "current": (smk == "current").astype(float).where(smk.notna()),
            "former": (smk == "former").astype(float).where(smk.notna()),
            "bmi": out[bmi_col].astype(float),
            "dm": _to_binary(out[dm_col], dm_col),
        },
        index=out.index,
    )
    for col, src in (("hba1c", hba1c_col), ("oral_dm", oral_dm_col), ("insulin", insulin_col)):
        if src in out.columns:
            d[col] = out[src].astype(float) if col == "hba1c" else _to_binary(out[src], src)
        else:
            d[col] = np.nan

    # uACR must be positive for the log
    d.loc[d["uacr"] <= 0, "uacr"] = np.nan

    def prob(lp):
        return 1 / (1 + np.exp(-lp))

    risk = pd.Series(np.nan, index=out.index)
    for dm in (False, True):
        mask = d["dm"] == (1.0 if dm else 0.0)
        if not mask.any():
            continue
        sub = d[mask]
        p_hi = prob(_lp_vectorized(True, dm, sub))
        p_lo = prob(_lp_vectorized(False, dm, sub))
        r = np.where(sub["egfr"] > 60, p_hi, p_lo)
        r = np.where(sub["egfr"] == 60, (p_hi + p_lo) / 2, r)
        r = np.where(sub["egfr"].isna(), np.nan, r)
        risk[mask] = r

    out[risk_col] = risk
    return out
