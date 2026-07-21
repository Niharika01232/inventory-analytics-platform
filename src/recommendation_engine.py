import os
import pandas as pd
import numpy as np

def run_recommendation_engine():
    print("Initializing Rule-Based Recommendation Engine & Health Scoring...")
    processed_dir = os.path.join("data", "processed")
    
    # Load processed datasets
    df_products = pd.read_csv(os.path.join(processed_dir, "products.csv"))
    df_suppliers = pd.read_csv(os.path.join(processed_dir, "suppliers.csv"))
    df_warehouses = pd.read_csv(os.path.join(processed_dir, "warehouses.csv"))
    df_sales = pd.read_csv(os.path.join(processed_dir, "sales.csv"))
    df_inventory = pd.read_csv(os.path.join(processed_dir, "inventory.csv"))
    df_opt = pd.read_csv(os.path.join(processed_dir, "inventory_optimization.csv"))
    
    # ------------------ Calculate Stockout Days in Snapshots ------------------
    # Total days in snapshot = 60
    total_days = df_inventory["date"].nunique()
    
    # Count stockout days per product-warehouse
    stockout_df = df_inventory[df_inventory["stock_on_hand"] == 0].groupby(["product_id", "warehouse_id"])["date"].count().reset_index()
    stockout_df.columns = ["product_id", "warehouse_id", "stockout_days"]
    
    # Merge current status (latest snapshot date)
    max_date = df_inventory["date"].max()
    df_curr = df_inventory[df_inventory["date"] == max_date].copy()
    df_curr = df_curr.merge(stockout_df, on=["product_id", "warehouse_id"], how="left")
    df_curr = df_curr.merge(df_warehouses[["warehouse_id", "warehouse_name"]], on="warehouse_id", how="left")
    df_curr["stockout_days"] = df_curr["stockout_days"].fillna(0)
    
    # Stock Availability % = 100 * (1 - stockout_days/total_days)
    df_curr["stock_availability_pct"] = np.round((1 - (df_curr["stockout_days"] / total_days)) * 100, 1)
    
    # ------------------ Merge Optimization parameters (ROP, EOQ) ------------------
    df_rec = df_curr.merge(df_opt, on="product_id", how="left")
    
    # ------------------ Calculate Inventory Health Score ------------------
    # Formula: Health Score (0-100) =
    #   0.40 * Stock Availability Score (availability %)
    #   + 0.30 * Turnover Score (based on current stock relative to ROP/Safety stock)
    #   + 0.30 * Cost Efficiency Score (penalize if overstocked)
    
    # Availability Score
    df_rec["availability_score"] = df_rec["stock_availability_pct"]
    
    # Turnover Score: 100 if stock on hand is close to ROP; decays if 0 or excessively high
    def get_turnover_score(row):
        stock = row["stock_on_hand"]
        rop = row["rop"]
        if stock == 0:
            return 20.0
        elif stock < rop:
            return 60.0
        elif stock <= rop * 2:
            return 100.0
        elif stock <= rop * 4:
            return 70.0
        else:
            return 40.0
            
    df_rec["turnover_score"] = df_rec.apply(get_turnover_score, axis=1)
    
    # Cost Efficiency Score: Penalize high ratios of stock to safety stock
    def get_cost_score(row):
        stock = row["stock_on_hand"]
        ss = row["safety_stock"]
        if ss == 0:
            return 100
        ratio = stock / ss
        if ratio <= 2.0:
            return 100.0
        elif ratio <= 4.0:
            return 80.0
        elif ratio <= 6.0:
            return 50.0
        else:
            return 20.0
            
    df_rec["cost_score"] = df_rec.apply(get_cost_score, axis=1)
    
    # Weighted Health Score
    df_rec["health_score"] = (
        0.40 * df_rec["availability_score"] +
        0.30 * df_rec["turnover_score"] +
        0.30 * df_rec["cost_score"]
    ).round(1)
    
    # Category Labeling
    def get_health_label(score):
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Needs Attention"
        else:
            return "Critical"
            
    df_rec["health_label"] = df_rec["health_score"].apply(get_health_label)
    
    # ------------------ Generate Rule-Based Recommendations ------------------
    # Rules:
    # 1. Stock = 0: "CRITICAL: Stockout! Trigger emergency reorder."
    # 2. Stock < ROP and Stock On Order = 0: "Reorder: Place order of size EOQ."
    # 3. Stock < ROP and Stock On Order > 0: "Pending: Awaiting supplier shipment."
    # 4. Stock > 3 * Safety Stock: "Overstocked: Stop procurement. Run clearance promotions."
    # 5. Otherwise: "Healthy: Maintain current stock levels."
    
    def generate_recommendation(row):
        stock = row["stock_on_hand"]
        rop = row["rop"]
        on_order = row["stock_on_order"]
        ss = row["safety_stock"]
        
        if stock == 0:
            return "CRITICAL: Out of stock! Place emergency order of size " + str(int(row["eoq"])) + " units immediately."
        elif stock < rop:
            if on_order == 0:
                return "Reorder Alert: Stock is below Reorder Point (" + str(int(rop)) + "). Order " + str(int(row["eoq"])) + " units."
            else:
                return "Pending Replenishment: Stock is below ROP, but order of " + str(int(on_order)) + " units is in transit."
        elif stock > ss * 4:
            return "Overstocked: Current stock (" + str(int(stock)) + ") is far above Safety Stock (" + str(int(ss)) + "). Halt procurement; run markdown campaigns."
        else:
            return "Optimal: Inventory levels are healthy. No action required."
            
    df_rec["recommendation"] = df_rec.apply(generate_recommendation, axis=1)
    
    # Check for Supplier Risk
    df_rec = df_rec.merge(df_suppliers[["supplier_id", "supplier_name", "rating", "reliability_score"]], on="supplier_id", how="left")
    
    def check_supplier_risk(row):
        if row["reliability_score"] < 0.85:
            return "High Risk (Supplier reliability is " + str(int(row["reliability_score"]*100)) + "%). Evaluate alternative vendors."
        elif row["rating"] < 3.8:
            return "Medium Risk (Supplier rating: " + str(row["rating"]) + "). Review service-level agreement."
        else:
            return "Low Risk"
            
    df_rec["supplier_risk_status"] = df_rec.apply(check_supplier_risk, axis=1)
    
    # Output file
    output_path = os.path.join(processed_dir, "inventory_recommendations.csv")
    
    # Filter columns for output
    cols_to_save = [
        "product_id", "product_name", "category", "warehouse_name", 
        "stock_on_hand", "stock_allocated", "stock_on_order", "rop", "eoq",
        "safety_stock", "stockout_days", "stock_availability_pct", 
        "health_score", "health_label", "recommendation", "supplier_name", "supplier_risk_status"
    ]
    df_save = df_rec[cols_to_save]
    df_save.to_csv(output_path, index=False)
    
    print(f"Recommendations and Health Scores exported to {output_path}")
    print("\nSummary of Inventory Health Labels:")
    print(df_save["health_label"].value_counts())
    print("\nSample Recommendations:")
    print(df_save[["product_name", "warehouse_name", "health_label", "recommendation"]].head(5))

if __name__ == "__main__":
    run_recommendation_engine()
