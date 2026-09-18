# 🌾 CropForecastLK: Sri Lankan Highland Crop Harvest Prediction

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black)

**CropForecastLK** is an advanced Machine Learning microservice and interactive web dashboard designed to predict highland crop yields and overall harvest production across Sri Lankan districts. 

By leveraging historical agronomic data, time-series lags, and a highly-tuned **XGBoost regression model**, this system provides actionable intelligence for agricultural planning, resource distribution, and food security forecasting.

---

## 🏗️ System Architecture

The project is structured as a modern Monorepo containing three distinct, decoupled modules:

1. **`ml_pipeline/`**: The Core Data Science Engine. Automates data ingestion, leakage-free chronological splitting, smoothed out-of-fold target encoding, temporal feature engineering (rolling averages & lags), and Bayesian hyperparameter tuning via Optuna.
2. **`backend/`**: A high-performance REST API built with **FastAPI**. It securely deserializes the serialized ML artifact (`.joblib`) into memory via a Singleton pattern, providing highly concurrent prediction and analytics endpoints guarded by Pydantic validation schemas.
3. **`frontend/`**: An interactive, responsive Single Page Application (SPA) built with **React** & **Vite**. It features interactive forms, batch prediction simulations, and real-time visualization dashboards powered by Chart.js.

---


## 🧬 The 11-Step Machine Learning Lifecycle

Our predictive engine is strictly serialized into an 11-step autonomous pipeline designed to prevent temporal data leakage and maximize feature richness:

| Step | Lifecycle Phase | Technical Description |
| :---: | :--- | :--- |
| **1** | **Raw Data Ingestion** | Safely load and validate multi-sheet governmental Excel consensus data. |
| **2** | **String Parsing & Sanitization** | Filter biological anomalies with highly-optimized regex string mapping. |
| **3** | **Missing Value Imputation** | Calculate continuous aggregations for missing values across crop cohorts. |
| **4** | **Agronomic Math Formulations** | Mathematically derive the true Yield capability (Metric Tons per Hectare). |
| **5** | **Time-Series Lags (t-1)** | Generate historical (1-year prior) prior lags for Production/Yield variables. |
| **6** | **Rolling Window Statistics** | Implement 3-year statistical moving averages for cultivated geographic Extent. |
| **7** | **Chronological Splitting** | Hard-split (Train: ≤2017, Val: 2018-20, Test: 2021-23) to prevent future leakage. |
| **8** | **Smoothed Target Encoding** | Map categorical districts and crop strains to normalized numeric representations. |
| **9** | **Algorithm Benchmarking** | Compare Ridge, Random Forest, LightGBM, and XGBoost regressor structures. |
| **10**| **Expanding-Window Cross-Val**| Evaluate models natively through progressive chronological shifting methodologies. |
| **11**| **Bayesian Serialization** | Leverage Optuna (TPE) for hyperparameters, serializing the champion to `.joblib`. |

---


## 👥 Team Members & Academic Contributions

This project was developed strictly adhering to industry-standard Git Flow and branch chaining methodologies. The implementation responsibilities were divided among the group members as detailed below:

### 1. Machine Learning Pipeline (Phase 1)
| Member Name | Student ID | Phase 1 Branch Name | Core Responsibilities |
| :--- | :--- | :--- | :--- |
| **Sathindu** | `241711053` | `feature/ml/data-preprocessing` | Raw data ingestion, regex string cleaning, handling biological anomalies, and EDA setup. |
| **Prashan** | `241711044` | `feature/ml/feature-engineering` | Target encoding, temporal lags (1Y), rolling extent statistics, and strict chronological train/val bounds. |
| **Visun** | `241711009` | `feature/ml/model-training` | XGBoost baseline configuration, expanding-window temporal CV, and diagnostic metric formulas. |
| **Lahiru** | `241711074` | `feature/ml/pipeline-export` | Optuna Bayesian optimization, model packaging/serialization, and metric artifact `.json` extraction. |

### 2. FastAPI Backend Server (Phase 2)
| Member Name | Student ID | Phase 2 Branch Name | Core Responsibilities |
| :--- | :--- | :--- | :--- |
| **Prashan** | `241711044` | `feature/backend/core-foundation` | Established server configurations, built Pydantic schemas, and engineered the Singleton ML loader class. |
| **Lahiru** | `241711074` | `feature/backend/api-endpoints` | Developed the Health, Inference (Single & Batch), and Analytics endpoints, combining them via API Router. |
| **Visun** | `241711009` | `feature/backend/server-and-testing` | Assembled the server lifecycle (`main.py`), configured CORS, and built the automated integration tests. |


### 3. React Frontend Dashboard (Phase 3)
*Note: The frontend was exclusively developed by Prashan and Lahiru using an alternating sequential branch-chaining workflow. Visun and Sathindu did not participate in the frontend phase.*

| Order | Member Name | Student ID | Phase 3 Branch Name | Core Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| **1st** | **Prashan** | `241711044` | `feature/frontend/setup-and-base` | Vite framework initialization, CSS architectures, and foundational package configuration. |
| **2nd** | **Lahiru** | `241711074` | `feature/frontend/api-and-routes` | Axios integration, API routing mechanisms, and initial layout wrappers via layout components. |
| **3rd** | **Prashan** | `241711044` | `feature/frontend/ui-implementation` | Implemented primary UI visual components including `PredictorCard` and Global `Navbar`. |
| **4th** | **Lahiru** | `241711074` | `feature/frontend/analytics-assembly` | Built the complex `AllCropsPredictor` and `AnalyticsChart`, finalizing the `App.jsx` compilation. |


---

## 🚀 Installation & Execution Guide

### Prerequisite Setup
We heavily recommend running both the ML Pipeline and Backend using a shared Python Virtual Environment to prevent package pollution.
```bash
# 1. Create and Activate the Virtual Environment
python -m venv venv
.\venv\Scripts\activate      # Windows
# source venv/bin/activate    # Mac/Linux
```

### Module 1: Executing the ML Pipeline (Offline Training)
If you wish to recalculate the agronomic formulas and re-train the XGBoost model from scratch:
```bash
# 1. Install ML Dependencies
pip install -r ml_pipeline/requirements.txt

# 2. Re-create the processed datasets (In sequence)
python ml_pipeline/preprocessing.py
python ml_pipeline/feature_engineering.py

# 3. Train algorithms and Export Production Artifacts
python ml_pipeline/export_pipeline.py

# Ensure data/artifacts/crop_forecaster_pipeline.joblib has been successfully generated.
```

### Module 2: Booting the FastAPI Backend
With the `.joblib` model successfully compiled, the server can be initialized:
```bash
# 1. Install Backend Web Dependencies
pip install -r backend/requirements.txt

# 2. Launch the Uvicorn ASGI Server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
*   **Interactive API Docs (Swagger UI):** Navigate to `http://localhost:8000/docs` in your browser.
*   **Run Automated Tests:** Open a secondary terminal, activate the environment, and execute `pytest backend/tests/`.

### Module 3: Booting the React Frontend
The GUI runs independently on Node.js using the Vite compiler.
```bash
# 1. Enter the frontend directory
cd frontend

# 2. Download NPM Packages
npm install

# 3. Start the Vite Development Server
npm run dev
```
*   **Access Dashboard:** Open the localhost link provided by Vite (typically `http://localhost:5173`).


---

## 🔬 Technologies Utilized
*   **Data Science & Modeling:** Python, Pandas, Scikit-Learn, XGBoost, Optuna, SHAP, Joblib
*   **Backend engineering:** FastAPI, Pydantic, Uvicorn, PyTest
*   **Frontend UI:** React.js, Vite, Axios, Chart.js / Recharts, CSS3
*   **Version Control:** Git, GitHub Feature Branching

*This project was submitted for academic evaluation. For queries regarding the core implementations, please check the commit histories in the respective phase branches.*
