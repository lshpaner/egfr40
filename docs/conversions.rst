uPCR and Dipstick to uACR
=========================

The model needs uACR in mg/g. When only a urine protein-to-creatinine ratio
(uPCR) or a dipstick reading is available, ``egfr40`` can estimate uACR with
the crude (unadjusted) equations of Sumida et al. (2020). Grams et al. (2022)
used the same conversions when developing the model.

.. warning::

   Converted values are approximations that carry measurement error. A
   directly measured uACR is preferred when available.

uPCR to uACR
------------

.. code-block:: python

   from egfr40 import pcr_to_acr

   pcr_to_acr(150)          # uPCR 150 mg/g -> about 32.8 mg/g
   pcr_to_acr([50, 500])    # arrays work too

.. math::

   \begin{aligned}
   \text{uACR} = \exp\Big(\, & 5.3920
     + 0.3072 \log\left(\min\left(\tfrac{\text{PCR}}{50},\, 1\right)\right) \\
   & + 1.5793 \log\left(\max\left(\min\left(\tfrac{\text{PCR}}{500},\, 1\right),\, 0.1\right)\right) \\
   & + 1.1266 \log\left(\max\left(\tfrac{\text{PCR}}{500},\, 1\right)\right) \Big)
   \end{aligned}

with uPCR and uACR in mg/g and natural logarithms. Non-positive or missing uPCR
returns ``NaN``.

.. note::

   **Why this differs from kfre.** Sumida et al. (2020) publish two versions of
   this equation: a crude one (uPCR only) and an adjusted one that adds sex,
   diabetes and hypertension. ``egfr40`` uses the crude equation because Grams
   et al. (2022) converted uPCR with the unadjusted equation when developing
   the model. The `kfre <https://lshpaner.github.io/kfre>`_ library uses the
   adjusted equation, so the same uPCR can give uACR values that differ by
   up to about 20% between the two libraries, depending on the patient.

Dipstick to uACR
----------------

.. code-block:: python

   from egfr40 import dipstick_to_acr

   dipstick_to_acr("++")    # about 337 mg/g

.. list-table::
   :header-rows: 1

   * - Category
     - Also accepted
     - Estimated uACR (mg/g)
   * - ``negative``
     - ``neg``, ``-``, ``0``
     - 11.9
   * - ``trace``
     - ``tr``, ``+/-``
     - 25.2
   * - ``+``
     - ``1+``
     - 66.6
   * - ``++``
     - ``2+``
     - 337.4
   * - ``>++``
     - ``+++``, ``3+``, ``4+``
     - 1,228.7

Unit conversion
---------------

.. code-block:: python

   from egfr40 import acr_mg_mmol_to_mg_g, acr_mg_g_to_mg_mmol

   acr_mg_mmol_to_mg_g(3.0)   # 26.5 mg/g
   acr_mg_g_to_mg_mmol(30)    # 3.4 mg/mmol

1 mg/mmol equals 8.84 mg/g.
