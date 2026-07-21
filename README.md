# Inventory Performance & Stock Optimization Analytics Platform

An end-to-end data analytics and decision support platform that converts raw transaction logs and inventory snapshots into actionable supply chain insights. Designed for retail operators and supply chain managers to reduce holding costs, eliminate stockouts, and manage vendor risk.


## Project Architecture

The pipeline consists of the following components:
1. **Data Engineering (Python)**: Ingestion of raw transactional data, processing, deduplication, and anomaly resolution.
2. **Relational Database (SQL)**: Storing cleaned data in SQLite with strict constraints, indexes, and custom views.
3. **Exploratory Data Analysis (EDA)**: Profiling revenue trends, price distributions, and correlation maps.
4. **Supply Chain Modeling**: Custom ABC-XYZ matrix classification, safety stock parameters, Reorder Points (ROP), and Economic Order Quantities (EOQ).
5. **Demand Forecasting**: Predictive weekly demand forecasting using Moving Average, Linear Regression, and ARIMA(1,1,1) models.
6. **Decision Support Recommendation Engine**: Rules-based procurement recommendations and an Inventory Health Score (0-100).
7. **Business Intelligence Dashboards**: Excel data portal and an interactive corporate Power BI dashboard.


## Key Performance Indicators (KPIs) Captured
* **Inventory Turnover Ratio (ITR)**: Rate at which inventory is sold and replaced.
* **Days Inventory Outstanding (DIO)**: Average number of days inventory sits on shelves before sale.
* **Stockout Rate**: Frequency of zero stock events.
* **Economic Order Quantity (EOQ)**: Ideal order size to minimize replenishment costs.
* **Supplier Reliability Score**: Percentage of on-time deliveries from vendors.
* **Inventory Health Score**: A composite rating (0-100) indicating stock stability and capital efficiency.
