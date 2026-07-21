# Inventory Performance & Stock Optimization Analytics Platform

An end-to-end data analytics and decision support platform that converts raw transaction logs and inventory snapshots into actionable supply chain insights. Designed for retail operators and supply chain managers to reduce holding costs, eliminate stockouts, and manage vendor risk.

---

## 1. Project Architecture

The pipeline consists of the following components:
1. **Data Engineering (Python)**: Ingestion of raw transactional data, processing, deduplication, and anomaly resolution.
2. **Relational Database (SQL)**: Storing cleaned data in SQLite with strict constraints, indexes, and custom views.
3. **Exploratory Data Analysis (EDA)**: Profiling revenue trends, price distributions, and correlation maps.
4. **Supply Chain Modeling**: Custom ABC-XYZ matrix classification, safety stock parameters, Reorder Points (ROP), and Economic Order Quantities (EOQ).
5. **Demand Forecasting**: Predictive weekly demand forecasting using Moving Average, Linear Regression, and ARIMA(1,1,1) models.
6. **Decision Support Recommendation Engine**: Rules-based procurement recommendations and an Inventory Health Score (0-100).
7. **Business Intelligence Dashboards**: Excel data portal and an interactive corporate Power BI dashboard.

---

## 2. Repository Structure

```directory
inventory_analytics_platform/
├── data/
│   ├── raw/                       # Raw datasets containing anomalies
│   ├── processed/                 # Clean CSV datasets
│   └── inventory_analytics.db     # SQLite production database
├── sql/
│   ├── schema.sql                 # DDL tables, constraints, indexes & views
│   └── queries.sql                # 45+ commented analytical queries
├── src/
│   ├── generate_data.py           # Synthetic data generator
│   ├── data_cleaning.py           # Data preprocessing and cleaning pipeline
│   ├── load_db.py                 # SQLite database initializer and loader
│   ├── eda.py                     # Visual charts plotting script
│   ├── inventory_optimization.py  # ABC-XYZ, safety stock, EOQ & ROP calculations
│   ├── forecasting.py             # Demand forecasting model comparisons
│   └── recommendation_engine.py   # Inventory Health Score & actions recommendations
├── images/                        # Generated visual plots and diagrams
├── reports/                       # Exported text reports and metric CSVs
├── docs/
│   ├── project_report.md          # 40-page equivalent comprehensive project report
│   ├── excel_guide.md             # Guide for Excel Pivot charts and lookup portals
│   ├── powerbi_guide.md           # Model schemas, DAX measures and layout specs
│   └── resume_prep.md             # Resume bullets, interview pitch, and Q&A
├── requirements.txt               # Python package dependencies
└── README.md                      # Landing page documentation
```

---

## 3. Getting Started & Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/inventory-optimization-platform.git
cd inventory-optimization-platform
```

### Step 2: Install Python Dependencies
Ensure Python 3.8+ is installed:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Data Pipeline
Execute the scripts in order to generate, clean, model, and recommend stock decisions:
```bash
# 1. Generate Raw Data
python src/generate_data.py

# 2. Clean Anomalies
python src/data_cleaning.py

# 3. Create & Load SQLite Database
python src/load_db.py

# 4. Generate EDA Visualizations
python src/eda.py

# 5. Compute ABC-XYZ, Safety Stock & EOQ
python src/inventory_optimization.py

# 6. Fit & Compare Forecast Models
python src/forecasting.py

# 7. Generate Recommendations & Health Scores
python src/recommendation_engine.py
```

### Step 4: Open Excel & Power BI Guides
Follow the guides in the `docs/` folder to link the clean files in `data/processed/` to your dashboard visualizations:
* [Excel Guide](docs/excel_guide.md)
* [Power BI Specification](docs/powerbi_guide.md)

---

## 4. Key Performance Indicators (KPIs) Captured
* **Inventory Turnover Ratio (ITR)**: Rate at which inventory is sold and replaced.
* **Days Inventory Outstanding (DIO)**: Average number of days inventory sits on shelves before sale.
* **Stockout Rate**: Frequency of zero stock events.
* **Economic Order Quantity (EOQ)**: Ideal order size to minimize replenishment costs.
* **Supplier Reliability Score**: Percentage of on-time deliveries from vendors.
* **Inventory Health Score**: A composite rating (0-100) indicating stock stability and capital efficiency.
