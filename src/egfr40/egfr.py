import numpy as np


def ckd_epi_2021(scr, age, male):
    """eGFR from serum creatinine, using the CKD-EPI 2021 (race-free) equation.

    Inker LA et al. N Engl J Med 2021;385:1737-1749.

    Parameters
    ----------
    scr : float or array-like
        Serum creatinine in mg/dL.
    age : float or array-like
        Age in years.
    male : int or array-like
        1 = male, 0 = female.

    Returns
    -------
    float or numpy.ndarray
        eGFR in mL/min/1.73 m^2. NaN where inputs are missing.

    Examples
    --------
    >>> round(ckd_epi_2021(scr=1.0, age=50, male=1), 1)
    91.7
    """

    scr = np.asarray(scr, dtype=float)
    age = np.asarray(age, dtype=float)
    male = np.asarray(male, dtype=float)

    kappa = np.where(male == 1, 0.9, 0.7)
    alpha = np.where(male == 1, -0.302, -0.241)
    female_factor = np.where(male == 1, 1.0, 1.012)

    ratio = scr / kappa
    egfr = (
        142
        * np.minimum(ratio, 1) ** alpha
        * np.maximum(ratio, 1) ** -1.200
        * 0.9938**age
        * female_factor
    )
    egfr = np.where(np.isnan(male), np.nan, egfr)
    return egfr.item() if egfr.ndim == 0 else egfr

__all__ = ["ckd_epi_2021"]
