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
    """3-year probability of a >=40% eGFR decline or kidney failure.

    Parameters
    ----------
    age : float
        Age in years.
    male : int
        1 = male, 0 = female.
    egfr : float
        eGFR in mL/min/1.73 m^2, from the CKD-EPI 2021 creatinine equation.
    uacr : float
        Urine albumin-to-creatinine ratio in mg/g. Must be greater than 0.
    sbp : float
        Systolic blood pressure in mmHg.
    bp_meds : int
        Antihypertensive medication use (1/0).
    hf : int
        History of heart failure (1/0).
    chd : int
        History of coronary heart disease (1/0).
    afib : int
        History of atrial fibrillation (1/0).
    smoking : {'never', 'former', 'current'}
        Smoking status.
    bmi : float
        Body mass index in kg/m^2.
    dm : bool
        Diabetes. Required: selects the diabetes or no-diabetes model.
    hba1c : float, optional
        HbA1c in percent. Required when ``dm`` is True.
    oral_dm : int, default 0
        Oral diabetes medication (1/0). Used only when ``dm`` is True.
    insulin : int, default 0
        Insulin use (1/0). Used only when ``dm`` is True.
    explain : bool, default False
        Return a breakdown instead of just the risk.

    Returns
    -------
    float or dict
        The 3-year probability, between 0 and 1. At eGFR == 60 the two eGFR
        strata are averaged, as on ckdpcrisk.org.

        With ``explain=True``, a dict with ``risk``, ``stratum``,
        ``intercept``, ``linear_predictor`` (log-odds) and ``contributions``
        (each predictor's log-odds contribution, largest first). Positive
        contributions raise risk relative to the reference individual: age 60,
        eGFR at the stratum center (85 or 45), uACR 10 mg/g, SBP 130, BMI 30,
        HbA1c 7%, never smoker, no BP or diabetes medication, and HF and CHD at
        their centering values of 0.05 and 0.15 (so an individual without HF or CHD
        gets a small negative contribution for each). At eGFR == 60, a dict with
        the averaged ``risk`` and both breakdowns under ``strata``.

    Raises
    ------
    ValueError
        If ``hba1c`` is missing for an individual with diabetes, ``uacr`` is not
        positive, or ``smoking`` is not a recognized value.

    Examples
    --------
    >>> egfr40_risk(age=70, male=1, egfr=40, uacr=150, sbp=140, bp_meds=1,
    ...             hf=0, chd=1, afib=1, smoking="former", bmi=28,
    ...             dm=True, hba1c=7)  # doctest: +ELLIPSIS
    0.166...
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
    """Add the 3-year >=40% eGFR decline risk to every row of a DataFrame.

    Each row is scored with its own stratum (eGFR >=60 or <60, with or without
    diabetes). Rows at exactly eGFR 60 get the average of the two eGFR strata,
    as on ckdpcrisk.org.

    Parameters
    ----------
    df : pandas.DataFrame
        One row per individual.
    age_col, sex_col, egfr_col, uacr_col, sbp_col, bp_meds_col : str
        Column names for age (years), sex, eGFR (CKD-EPI 2021), uACR (mg/g),
        systolic BP (mmHg) and antihypertensive medication use.
    hf_col, chd_col, afib_col : str
        Column names for history of heart failure, coronary heart disease and
        atrial fibrillation.
    smoking_col, bmi_col : str
        Column names for smoking status and BMI (kg/m^2).
    dm_col, hba1c_col, oral_dm_col, insulin_col : str
        Column names for diabetes, HbA1c (%), oral diabetes medication and
        insulin. The last three are used only for rows with diabetes and may
        be absent from ``df`` if no row has diabetes.
    risk_col : str, default "egfr40_3year"
        Name of the new risk column.
    copy : bool, default True
        Work on a copy and leave ``df`` unchanged.

    Returns
    -------
    pandas.DataFrame
        ``df`` (or a copy) with ``risk_col`` added, holding probabilities
        between 0 and 1.

    Notes
    -----
    Sex accepts ``"male"``/``"female"``, ``"m"``/``"f"`` or 1/0. Yes/no
    columns (BP medication, HF, CHD, AFib, diabetes, oral diabetes medication,
    insulin) accept 1/0 or ``"yes"``/``"no"``. Smoking accepts ``"never"``,
    ``"former"`` or ``"current"``.

    A row with any required input missing gets ``NaN``. HbA1c, oral diabetes
    medication and insulin are required only for rows with diabetes; missing
    values there give ``NaN`` rather than being treated as 0.

    Raises
    ------
    ValueError
        If a smoking or yes/no column contains an unrecognized value.
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

__all__ = ["egfr40_risk", "add_egfr40_risk_col"]
