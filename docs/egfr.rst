eGFR (CKD-EPI 2021)
===================

The model was developed using eGFR from the race-free CKD-EPI 2021 creatinine
equation (Inker et al., 2021). ``ckd_epi_2021`` computes it from serum
creatinine, age and sex.

.. code-block:: python

   from egfr40 import ckd_epi_2021

   ckd_epi_2021(scr=1.2, age=70, male=1)   # mL/min/1.73 m²

It accepts scalars or arrays and returns ``NaN`` where inputs are missing.

The equation
------------

.. math::

   \begin{aligned}
   \text{eGFR} = 142 \, & \times \min\left(\frac{S_{cr}}{\kappa},\, 1\right)^{\alpha}
     \times \max\left(\frac{S_{cr}}{\kappa},\, 1\right)^{-1.200} \\
   & \times 0.9938^{\text{age}} \times 1.012 \; [\text{if female}]
   \end{aligned}

where :math:`S_{cr}` is serum creatinine in mg/dL, :math:`\kappa` is 0.7 for
females and 0.9 for males, and :math:`\alpha` is -0.241 for females and -0.302
for males.

.. note::

   The supplement of Grams et al. (2022) prints the female constant as 143,
   which is 142 × 1.012 rounded. ``egfr40`` uses the exact published equation,
   so hand calculations from that table can differ slightly.
