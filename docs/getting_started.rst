Getting Started
===============

Score one individual
--------------------

.. code-block:: python

   from egfr40 import egfr40_risk

   egfr40_risk(
       age=70, male=1, egfr=40, uacr=150, sbp=140, bp_meds=1,
       hf=0, chd=1, afib=1, smoking="former", bmi=28,
       dm=True, hba1c=7, oral_dm=0, insulin=0,
   )
   # 0.166  -> a 16.6% 3-year risk

This individual has diabetes and an eGFR below 60, so the function uses the
"diabetes, eGFR <60" model. The result matches the online CKD-PC calculator (16.6%).

Score a cohort
--------------

.. code-block:: python

   from egfr40 import add_egfr40_risk_col

   df = add_egfr40_risk_col(df)   # adds an "egfr40_3year" column

See :doc:`_notebooks/00_quickstart` for a worked example with output,
:doc:`usage_guide` for column mapping, and :doc:`inputs` for the expected
units and codes.

Library overview
----------------

.. code-block:: python

   import egfr40
   help(egfr40)   # prints the logo and a summary of the library

Table of Contents
-----------------

**Getting Started**

- :doc:`index`
- :doc:`getting_started`
- :doc:`_notebooks/00_quickstart`

**Documentation**

- :doc:`usage_guide`
- :doc:`inputs`
- :doc:`egfr`
- :doc:`conversions`
- :doc:`nhanes`
- :doc:`api`

**About egfr40**

- :doc:`model`
- :doc:`acknowledgements`
- :doc:`citing`
- :doc:`changelog`
- :doc:`references`
