# CropForecastLK: Dataset & Feature Dictionary

This document details the agricultural census schema, data cleaning transformations, and engineered feature definitions utilized across **CropForecastLK**.

---

## 1. Raw Census Fields (`researchData.xlsx`)

The raw dataset spans **94,755 historical records** (2000–2023) sourced from the **Department of Census and Statistics (DCS), Sri Lanka**.

| Field Name | Raw Type | Cleaned Type | Unit | Description & Invariants |
| :--- | :--- | :--- | :--- | :--- |
| **`District`** | `str` / `object` | `category` / `str` | N/A | Sri Lankan Administrative District (e.g. Nuwara Eliya, Badulla, Kandy, Matale, Moneragala). Summary aggregates (`"National Total"`, `"Total"`) are filtered out. |
| **`Season`** | `str` / `object` | `category` / `str` | N/A | Monsoonal regime: `Maha` (North-East Monsoon, Sep–Mar) or `Yala` (South-West Monsoon, May–Aug). Aggregate `'Total'` season rows are filtered out. |
| **`CropCategory`** | `str` / `object` | `category` / `str` | N/A | Broad agricultural classification (e.g. `Cereals`, `Pulses`, `Roots and Tubers`, `Low Country Vegetable`, `Up Country Vegetable`). |
| **`Crop`** | `str` / `object` | `category` / `str` | N/A | Agricultural crop species (e.g. `Potato`, `Maize`, `Kurakkan`, `Chili`, `Cassava`, `Sweet Potato`, `Green Gram`). |
| **`Year`** | `str` / `object` | `int` | Calendar Year | Harvest year (e.g. `2001`, `2023`). Split seasons (`2000/2001`) are parsed to harvest year. |
| **`Extent`** | `str` / `object` | `float64` | Hectares (Ha) | Cultivated land area. Cleaned via regex to strip thousands-commas, hyphens (`"-"`), and `"n.a."` text placeholders. |
| **`Production`** | `str` / `object` | `float64` | Metric Tons (MT) | Total harvested output. Cleaned via regex. Primary target variable. |

---

## 2. Engineered Domain & Temporal Features

| Feature Name | Type | Unit | Formula / Derivation | Agronomic Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **`Crop_Yield`** | `float64` | MT/Ha | $\text{Crop\_Yield} = \frac{\text{Production}}{\text{Extent}}$ | Physical productivity metric. Clipped to 100 MT/Ha to remove extreme division anomalies. |
| **`Production_Lag_1Y`** | `float64` | MT | $\text{Production}_{t-1}$ for cohort `(District, Crop, Season)` | Captures temporal momentum and local capacity from the previous agricultural year. |
| **`Yield_Lag_1Y`** | `float64` | MT/Ha | $\text{Crop\_Yield}_{t-1}$ for cohort `(District, Crop, Season)` | Reflects recent soil productivity, microclimate trends, and pest incidence. |
| **`Extent_RollMean_3Y`** | `float64` | Ha | $\frac{1}{3}\sum_{k=0}^{2} \text{Extent}_{t-k}$ | Smooths multi-year land allocation trends and farmer planting response. |
| **`Extent_RollStd_3Y`** | `float64` | Ha | $\text{StdDev}(\text{Extent}_{t-2:t})$ | Measures acreage volatility and climate vulnerability. |
| **`Season_Maha`** | `int` | Binary (0/1) | $1 \text{ if Season} = \text{'Maha'} \text{ else } 0$ | Accounts for the higher precipitation of the North-East monsoon compared to Yala. |
| **`District_TargetEnc`** | `float64` | MT | Out-of-fold smoothed mean: $\frac{n \cdot \bar{y}_d + 10 \cdot \bar{y}}{n + 10}$ | Encodes regional agro-ecological soil fertility without causing categorical leakage. |
| **`Crop_TargetEnc`** | `float64` | MT | Out-of-fold smoothed mean: $\frac{n \cdot \bar{y}_c + 10 \cdot \bar{y}}{n + 10}$ | Distinguishes high-biomass crops (Cassava, Potato) from low-density pulses (Green Gram). |

---

## 3. Data Cleaning & Integrity Rules

1. **Zero-Extent Anomaly**: If $\text{Extent} = 0$ and $\text{Production} > 0$, the record is biologically invalid (crops cannot produce without cultivated land). `Production` is set to `NaN` and cohort-imputed.
2. **Crop Failure Scenario**: If $\text{Extent} > 0$ and $\text{Production} = 0$, the record is a legitimate agricultural crop failure (e.g. severe drought or flood); preserved as 0.
3. **Group Median Imputation**: Missing values are imputed hierarchically:
   - Primary: Median of `(District, Crop, Season)` cohort.
   - Secondary: Median of `(Crop, Season)` cohort.
   - Tertiary: Global median for that specific crop.
4. **Chronological Splitting**:
   - **Training Set**: 2000–2017 (18 years)
   - **Validation Set**: 2018–2020 (3 years)
   - **Holdout Test Set**: 2021–2023 (3 years)
   - Strict temporal boundaries guarantee zero future-to-past information leakage.
