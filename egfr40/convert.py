"""Convert other urine measures to the albumin-to-creatinine ratio (ACR, mg/g).

PCR and dipstick conversions use the crude (unadjusted) equations from
Sumida K, Nadkarni GN, et al. Ann Intern Med 2020;173:426-435, Table 2
(doi:10.7326/M20-0529), as used by Grams et al. 2022 to build the egfr40 model.
"""

import numpy as np
import pandas as pd

MG_G_PER_MG_MMOL = 8.84  # 1 mg/mmol creatinine = 8.84 mg/g creatinine

# Dipstick category -> indicator coefficient (crude model)
_DIPSTICK = {
    "negative": 0.0,
    "trace": 0.7539,
    "+": 1.7243,
    "++": 3.3475,
    ">++": 4.6399,
}
_DIPSTICK_ALIASES = {
    "neg": "negative", "-": "negative", "0": "negative", "none": "negative",
    "tr": "trace", "+/-": "trace",
    "1+": "+", "2+": "++",
    "+++": ">++", "++++": ">++", "3+": ">++", "4+": ">++",
}


def acr_mg_mmol_to_mg_g(acr):
    """ACR in mg/mmol -> mg/g."""
    return np.asarray(acr, dtype=float) * MG_G_PER_MG_MMOL


def acr_mg_g_to_mg_mmol(acr):
    """ACR in mg/g -> mg/mmol."""
    return np.asarray(acr, dtype=float) / MG_G_PER_MG_MMOL


def pcr_to_acr(pcr):
    """Predicted ACR (mg/g) from urine protein-to-creatinine ratio (PCR, mg/g).

    pACR = exp(5.3920 + 0.3072 log(min(PCR/50, 1))
                      + 1.5793 log(max(min(PCR/500, 1), 0.1))
                      + 1.1266 log(max(PCR/500, 1)))
    """
    pcr = np.asarray(pcr, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.exp(
            5.3920
            + 0.3072 * np.log(np.minimum(pcr / 50, 1))
            + 1.5793 * np.log(np.maximum(np.minimum(pcr / 500, 1), 0.1))
            + 1.1266 * np.log(np.maximum(pcr / 500, 1))
        )
    out = np.where(pcr > 0, out, np.nan)
    return out.item() if out.ndim == 0 else out


def _dipstick_key(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    key = str(value).strip().lower().replace(" ", "")
    key = _DIPSTICK_ALIASES.get(key, key)
    if key not in _DIPSTICK:
        raise ValueError(
            f"Unrecognized dipstick category {value!r}; use one of "
            f"{list(_DIPSTICK)} (or 1+, 2+, 3+, 4+)"
        )
    return key


def dipstick_to_acr(category):
    """Predicted ACR (mg/g) from a urine dipstick protein category.

    Categories: 'negative', 'trace', '+', '++', '>++'
    (also accepts 'neg', '1+', '2+', '3+', '4+', '+++').
    """
    def one(v):
        k = _dipstick_key(v)
        return np.nan if k is None else float(np.exp(2.4738 + _DIPSTICK[k]))

    if isinstance(category, (list, tuple, np.ndarray, pd.Series)):
        return np.array([one(v) for v in category])
    return one(category)
