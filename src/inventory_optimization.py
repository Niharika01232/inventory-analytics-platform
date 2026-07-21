import os
import pandas as pd
import numpy as np

def run_optimization():
    print("Initializing Inventory Optimization Engine...")
    processed_dir = os.path.join("data", "processed")
    
    # Load processed datasets
    df_products = pd.read_csv(os.path.join(processed_dir, "products.csv"))
    df_sales = pd.read_csv(os.path.join(processed_dir, "sales.csv"))
    df_inventory = pd.read_csv(os.path.join(processed_dir, "inventory.csv"))
    
    # ------------------ 1. ABC Analysis (Revenue Based) ------------------
    print("Running ABC Analysis...")
    product_revenue = df_sales.groupby("product_id")["revenue"].sum().reset_index()
    product_revenue = product_revenue.sort_values(by="revenue", ascending=False).reset_index(drop=True)
    
    total_rev = product_revenue["revenue"].sum()
    product_revenue["rev_share"] = product_revenue["revenue"] / total_rev
    product_revenue["cum_share"] = product_revenue["rev_share"].cumsum()
    
    # Classification: A: 70%, B: 20% (up to 90%), C: 10% (up to 100%)
    def classify_abc(cum_share):
        if cum_share <= 0.70:
            return "A"
        elif cum_share <= 0.90:
            return "B"
        else:
            return "C"
            
    product_revenue["abc_class"] = product_revenue["cum_share"].apply(classify_abc)
    print("ABC Classification results:")
    print(product_revenue["abc_class"].value_counts())
    
    # ------------------ 2. XYZ Analysis (Demand Variability Based) ------------------
    print("\nRunning XYZ Analysis...")
    df_sales["sale_date"] = pd.to_datetime(df_sales["sale_date"])
    df_sales["month"] = df_sales["sale_date"].dt.to_period("M")
    
    # Monthly sales per product
    monthly_sales = df_sales.groupby(["product_id", "month"])["quantity_sold"].sum().reset_index()
    
    # Calculate Mean and Std Dev of monthly demand per product
    sku_stats = monthly_sales.groupby("product_id")["quantity_sold"].agg(["mean", "std"]).reset_index()
    sku_stats["std"] = sku_stats["std"].fillna(0) # handle case of single month or constant demand
    
    # Coefficient of Variation (CV)
    sku_stats["cv"] = sku_stats["std"] / sku_stats["mean"]
    sku_stats["cv"] = sku_stats["cv"].fillna(0) # handle mean=0
    
    # XYZ Classification:
    # X: Stable (CV < 0.25)
    # Y: Fluctuating (0.25 <= CV <= 0.60)
    # Z: Erratic (CV > 0.60)
    def classify_xyz(cv):
        if cv < 0.25:
            return "X"
        elif cv <= 0.60:
            return "Y"
        else:
            return "Z"
            
    sku_stats["xyz_class"] = sku_stats["cv"].apply(classify_xyz)
    print("XYZ Classification results:")
    print(sku_stats["xyz_class"].value_counts())
    
    # Merge ABC and XYZ
    sku_classification = product_revenue[["product_id", "revenue", "abc_class"]].merge(
        sku_stats[["product_id", "mean", "std", "cv", "xyz_class"]], on="product_id", how="outer"
    )
    # Fill products that had no sales
    sku_classification["abc_class"] = sku_classification["abc_class"].fillna("C")
    sku_classification["xyz_class"] = sku_classification["xyz_class"].fillna("Z")
    sku_classification["revenue"] = sku_classification["revenue"].fillna(0)
    sku_classification["cv"] = sku_classification["cv"].fillna(999.0)
    
    sku_classification["abc_xyz_segment"] = sku_classification["abc_class"] + sku_classification["xyz_class"]
    
    # ------------------ 3. Safety Stock & EOQ & ROP Calculations ------------------
    print("\nCalculating Supply Chain Optimization Metrics (EOQ, Safety Stock, ROP)...")
    
    # Join sku details (unit cost, price, lead time, min order qty)
    df_opt = sku_classification.merge(df_products, on="product_id", how="left")
    
    # Parameter Defaults
    ordering_cost_s = 150.0  # cost per purchase order
    holding_cost_rate_h = 0.15  # annual holding cost percentage of item cost
    
    # Safety factors based on service level:
    # A-items: 99% service level (Z = 2.33)
    # B-items: 95% service level (Z = 1.65)
    # C-items: 90% service level (Z = 1.28)
    def get_safety_factor(abc):
        if abc == "A":
            return 2.33
        elif abc == "B":
            return 1.65
        else:
            return 1.28
            
    df_opt["safety_factor_z"] = df_opt["abc_class"].apply(get_safety_factor)
    
    # Calculate daily sales stats from transactional logs
    daily_sales = df_sales.groupby(["product_id", "sale_date"])["quantity_sold"].sum().reset_index()
    daily_stats = daily_sales.groupby("product_id")["quantity_sold"].agg(["mean", "std"]).reset_index()
    daily_stats.columns = ["product_id", "daily_mean", "daily_std"]
    
    df_opt = df_opt.merge(daily_stats, on="product_id", how="left")
    df_opt["daily_mean"] = df_opt["daily_mean"].fillna(0)
    df_opt["daily_std"] = df_opt["daily_std"].fillna(0)
    
    # Annual Demand D = Daily Mean * 365
    df_opt["annual_demand"] = df_opt["daily_mean"] * 365
    
    # EOQ = sqrt((2 * D * S) / H)
    df_opt["annual_holding_cost_per_unit"] = df_opt["unit_cost"] * holding_cost_rate_h
    df_opt["eoq"] = np.sqrt((2 * df_opt["annual_demand"] * ordering_cost_s) / df_opt["annual_holding_cost_per_unit"])
    df_opt["eoq"] = df_opt["eoq"].fillna(df_opt["min_order_qty"]).round(0).astype(int)
    
    # Avoid 0 EOQ or lower than min order qty
    df_opt["eoq"] = np.maximum(df_opt["eoq"], df_opt["min_order_qty"])
    
    # Safety Stock = Z * std_daily_demand * sqrt(LeadTime)
    df_opt["safety_stock"] = df_opt["safety_factor_z"] * df_opt["daily_std"] * np.sqrt(df_opt["lead_time_days"])
    df_opt["safety_stock"] = df_opt["safety_stock"].fillna(5).round(0).astype(int)
    
    # Reorder Point (ROP) = (Daily Mean * LeadTime) + Safety Stock
    df_opt["rop"] = (df_opt["daily_mean"] * df_opt["lead_time_days"]) + df_opt["safety_stock"]
    df_opt["rop"] = df_opt["rop"].fillna(10).round(0).astype(int)
    
    # Export optimization tables
    output_path = os.path.join(processed_dir, "inventory_optimization.csv")
    df_opt.to_csv(output_path, index=False)
    print(f"Inventory Optimization results exported to {output_path}")
    print("Sample Output:")
    print(df_opt[["product_id", "product_name", "abc_xyz_segment", "eoq", "safety_stock", "rop"]].head(5))

if __name__ == "__main__":
    run_optimization()
