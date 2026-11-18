import math

import numpy as np
import pytest

from egfr40 import ckd_epi_2021


def reference(scr, age, male):
    k, a = (0.9, -0.302) if male else (0.7, -0.241)
    f = 1.0 if male else 1.012
    return 142 * min(scr / k, 1) ** a * max(scr / k, 1) ** -1.2 * 0.9938**age * f


@pytest.mark.parametrize("scr,age,male", [
    (0.7, 60, 0), (1.0, 50, 1), (0.5, 30, 0), (2.5, 75, 1), (0.9, 45, 1), (1.4, 80, 0),
])
def test_scalar_matches_reference(scr, age, male):
    assert ckd_epi_2021(scr, age, male) == pytest.approx(reference(scr, age, male))


def test_at_kappa_only_age_and_sex_matter():
    # Scr equal to kappa: both min/max terms are 1
    assert ckd_epi_2021(0.9, 40, 1) == pytest.approx(142 * 0.9938**40)
    assert ckd_epi_2021(0.7, 40, 0) == pytest.approx(142 * 0.9938**40 * 1.012)


def test_vectorized_and_missing():
    out = ckd_epi_2021([1.0, np.nan, 1.0], [50, 50, 50], [1, 1, np.nan])
    assert out[0] == pytest.approx(reference(1.0, 50, 1))
    assert math.isnan(out[1]) and math.isnan(out[2])
