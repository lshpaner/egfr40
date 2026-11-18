.. list-table:: Coefficients by stratum (Grams et al. 2022, Supplemental Table S5)
   :header-rows: 1
   :widths: 26 26 12 12 12 12

   * - Predictor
     - Centering and scale
     - eGFR ≥60, no diabetes
     - eGFR ≥60, diabetes
     - eGFR <60, no diabetes
     - eGFR <60, diabetes
   * - Age, per 10 years
     - (age − 60) / 10
     - 0.3690
     - 0.1465
     - -0.0796
     - -0.1725
   * - Male sex
     - male − 0.5
     - -0.1433
     - -0.2481
     - 0.0626
     - -0.1452
   * - eGFR, per 5 mL/min/1.73 m²
     - (eGFR − E) / 5 [#E]_
     - 0.0325
     - -0.0562
     - -0.1672
     - -0.0769
   * - uACR
     - ln(uACR / 10)
     - 0.4190
     - 0.4098
     - 0.3915
     - 0.4658
   * - Systolic BP, per 20 mmHg
     - (SBP − 130) / 20
     - 0.3048
     - 0.1518
     - 0.2373
     - 0.2068
   * - Antihypertensive medication
     - 1 or 0
     - 0.2656
     - 0.2846
     - 0.0790
     - 0.1665
   * - SBP × antihypertensive
     - [(SBP − 130) / 20] × (1 or 0)
     - -0.1140
     - -0.0321
     - -0.0214
     - -0.0549
   * - History of heart failure
     - HF − 0.05
     - 1.0534
     - 0.9234
     - 0.4898
     - 0.4216
   * - History of CHD
     - CHD − 0.15
     - 0.4102
     - 0.2168
     - 0.2343
     - 0.2173
   * - History of atrial fibrillation
     - 1 or 0
     - 0.1140
     - 0.3087
     - 0.0739
     - 0.0456
   * - Current smoker
     - 1 or 0
     - 0.3803
     - 0.1186
     - 0.2903
     - -0.0338
   * - Former smoker
     - 1 or 0
     - 0.1862
     - 0.0777
     - 0.1725
     - 0.1386
   * - BMI, per 5 kg/m²
     - (BMI − 30) / 5
     - 0.0425
     - 0.0308
     - -0.0231
     - 0.0253
   * - HbA1c (%)
     - HbA1c − 7
     - 
     - 0.0987
     - 
     - -0.0031
   * - Oral diabetes medication
     - 1 or 0
     - 
     - -0.0638
     - 
     - -0.1232
   * - Insulin
     - 1 or 0
     - 
     - 0.2359
     - 
     - 0.0980
   * - Intercept
     - 
     - -4.7045
     - -4.2125
     - -3.4540
     - -3.2874
