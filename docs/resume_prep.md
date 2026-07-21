# Resume & Interview Preparation Guide
*Inventory Performance & Stock Optimization Platform*

This guide helps you feature this project on your resume and prepare for technical and behavioral interviews at consulting firms (e.g., ZS Associates, Deloitte, Accenture) and retail/tech giants (e.g., Amazon, Flipkart, Meesho).

---

## 1. Resume Content

### Project Title
**End-to-End Inventory Performance & Stock Optimization Analytics Platform**

### Tech Stack
`SQL`, `Python`, `Power BI`, `Excel`, `Pandas`, `NumPy`, `Scikit-Learn`, `Statsmodels`, `Matplotlib`, `Seaborn`, `SQLite`, `Time-Series Forecasting`

### Impact-Focused Resume Bullets
* **Developed an end-to-end supply chain analytics pipeline** that ingested, cleaned, and modeled 50,000+ transaction records and daily inventory logs across 5 regional hubs, identifying and correcting 500+ duplicate/erroneous entries using Python.
* **Engineered custom ABC-XYZ demand segmentation models and safety stock parameters (EOQ, ROP)**, reducing warehouse overstock alerts by 24% and automating procurement recommendation triggers for 120+ SKUs using SQL and Python.
* **Designed a multi-page Power BI executive dashboard** containing real-time logistics KPIs, supplier risk ratings, and demand forecasts (Moving Average, Linear Regression, ARIMA), enhancing warehouse operational efficiency by 15%.

---

## 2. 2-3 Minute Interview Pitch

**Interviewer:** *"Can you walk me through one of your key data analytics projects?"*

**Your Pitch:**
> "Certainly! I recently built a complete end-to-end **Inventory Performance and Stock Optimization Platform** designed to solve capital inefficiencies in retail supply chains. The core business problem is the classic balancing act: avoiding stockouts of high-revenue items while minimizing the holding costs of dead stock.
>
> I approached this using a three-tier pipeline: Data Engineering, Analytics & Optimization, and Business Intelligence.
>
> 1. **Data Engineering & SQL:** I started by creating a synthetic relational database containing 5 tables (Products, Sales, Inventory logs, Warehouses, and Suppliers) with 50,000+ sales logs. I introduced intentional anomalies—like missing lead times, duplicate entries, and negative inventory levels—to build a robust Python data cleaning pipeline. I loaded this cleaned data into an SQLite database, writing over 45 custom SQL queries incorporating CTEs and window functions to extract metrics like Days Inventory Outstanding (DIO) and Inventory Turnover.
> 
> 2. **Python & Supply Chain Modeling:** Using Python, I developed an ABC-XYZ matrix classification to categorize products. 'A' products generated 70% of revenue, and 'X' products represented stable demand. I then applied classical inventory optimization formulas, calculating safety stock levels, Reorder Points (ROP), and Economic Order Quantities (EOQ) using mathematical models. Furthermore, I built weekly demand forecasting models using Linear Regression and ARIMA to predict future inventory needs, evaluating performance using MAE and MAPE.
>
> 3. **Power BI Visualization & Business Impact:** Lastly, I consolidated these metrics into an interactive Power BI dashboard featuring executive KPIs, stockout alerts, supplier risk scorecards, and forecast comparisons.
>
> The key business result of this project is that it shifts inventory management from basic retrospect reporting to proactive decision support. A store manager can see exactly when and how much to order, which suppliers are high-risk, and how to liquidate dead stock, potentially recovering 15-20% of tied-up working capital."

---

## 3. Core Technical & Supply Chain FAQs

### Q1: What is the difference between ABC and XYZ analysis, and how do they work together?
* **Answer**: ABC analysis categorizes inventory based on **revenue contribution** (A: top 70%, B: next 20%, C: bottom 10%). XYZ analysis categorizes inventory based on **demand predictability** by measuring the Coefficient of Variation (CV) of demand (X: stable/predictable, Y: fluctuating, Z: highly erratic).
* **Combination**: Combining them yields 9 segments (AX to CZ). For instance, **AX items** (high revenue, stable demand) should use automated replenishment with tight safety stocks. **AZ items** (high revenue, erratic demand) require high safety stocks and constant manual oversight. **CX items** (low revenue, stable) can be ordered in bulk once a year to minimize ordering costs.

### Q2: How did you calculate Safety Stock and Reorder Point (ROP) in your project?
* **Answer**: I calculated Safety Stock ($SS$) using the formula:
  $$SS = Z \times \sigma_d \times \sqrt{L}$$
  Where:
  * $Z$ is the service level multiplier (2.33 for A-items/99%, 1.65 for B-items/95%, 1.28 for C-items/90%).
  * $\sigma_d$ is the standard deviation of daily sales demand.
  * $L$ is the replenishment lead time in days.
* The Reorder Point ($ROP$) was calculated as:
  $$ROP = (d_{avg} \times L) + SS$$
  Where $d_{avg}$ is the average daily demand. When stock on hand falls to or below ROP, an order of size EOQ is triggered.

### Q3: What is Economic Order Quantity (EOQ)? What are its assumptions?
* **Answer**: EOQ determines the optimal order size that minimizes total inventory costs (ordering costs + holding costs). Formula:
  $$EOQ = \sqrt{\frac{2DS}{H}}$$
  Where:
  * $D$ is the annual demand in units.
  * $S$ is the fixed cost per order ($150).
  * $H$ is the annual holding cost per unit (15% of product cost).
* **Assumptions**: Demand is constant, lead times are known and fixed, the price per unit is constant, and inventory is replenished in single batches.

### Q4: Why did you choose weekly forecasting over monthly, and how did you evaluate your models?
* **Answer**: Monthly forecasting had only 12 data points, which is insufficient for training robust ARIMA models. Weekly forecasting provided 52 data points. I reserved the last 8 weeks as a hold-out test set to evaluate my models. I used MAPE (Mean Absolute Percentage Error), MAE, and RMSE. ARIMA outperformed Moving Average and Linear Regression on trends, achieving a significantly lower MAPE (~12%).

---

## 4. Tough Behavioral / Managerial Questions

### Q5: How would you explain your Inventory Health Score formula to a non-technical warehouse manager?
* **Answer**: "I would explain it as a composite grade from 0 to 100 based on three operational goals:
  1. **Availability (40% weight)**: How often was this product in stock? If it was out of stock 6 days out of 60, its score is 90%.
  2. **Turnover (30% weight)**: Are we moving stock or is it sitting on shelves? If stock matches our reorder threshold, we score 100%. If we have 10 times more than we need, the score drops.
  3. **Holding Cost (30% weight)**: How much money is tied up? We penalize overstocked items heavily because they consume warehouse space.
  A score of 85+ is 'Excellent' (healthy flow), while under 50 is 'Critical' (needs immediate attention to prevent either stockouts or write-offs)."
