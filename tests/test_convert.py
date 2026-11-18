import math

import numpy as np
import pytest

from egfr40 import acr_mg_g_to_mg_mmol, acr_mg_mmol_to_mg_g, dipstick_to_acr, pcr_to_acr


def ref_pcr(p):
    return math.exp(5.3920 + 0.3072 * math.log(min(p / 50, 1))
                    + 1.5793 * math.log(max(min(p / 500, 1), 0.1))
                    + 1.1266 * math.log(max(p / 500, 1)))


@pytest.mark.parametrize("pcr", [10, 50, 150, 500, 1500])
def test_pcr_matches_sumida_equation(pcr):
    assert pcr_to_acr(pcr) == pytest.approx(ref_pcr(pcr))


def test_pcr_knots():
    assert pcr_to_acr(500) == pytest.approx(math.exp(5.3920))          # every log term is 0
    assert pcr_to_acr(50) == pytest.approx(math.exp(5.3920 + 1.5793 * math.log(0.1)))


def test_pcr_vectorized_and_nonpositive():
    out = pcr_to_acr([150, 0, np.nan])
    assert out[0] == pytest.approx(ref_pcr(150)) and np.isnan(out[1]) and np.isnan(out[2])


@pytest.mark.parametrize("cat,coef", [("negative", 0), ("trace", 0.7539), ("+", 1.7243),
                                      ("++", 3.3475), (">++", 4.6399), ("2+", 3.3475), ("4+", 4.6399)])
def test_dipstick(cat, coef):
    assert dipstick_to_acr(cat) == pytest.approx(math.exp(2.4738 + coef))


def test_dipstick_bad_value():
    with pytest.raises(ValueError):
        dipstick_to_acr("lots")


def test_unit_round_trip():
    assert acr_mg_g_to_mg_mmol(acr_mg_mmol_to_mg_g(3.0)) == pytest.approx(3.0)
    assert acr_mg_mmol_to_mg_g(3.0) == pytest.approx(26.52)
