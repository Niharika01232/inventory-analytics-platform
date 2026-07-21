import os
import pandas as pd
import numpy as np

def clean_data():
    print("Initializing Data Cleaning Pipeline...")
    raw_dir = os.path.join("data", "raw")
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    # 1. Load data
    print("Loading raw files...")
    df_suppliers = pd.read_csv(os.path.join(raw_dir, "suppliers.csv"))
    df_warehouses = pd.read_csv(os.path.join(raw_dir, "warehouses.csv"))
    df_products = pd.read_csv(os.path.join(raw_dir, "products.csv"))
    df_sales = pd.read_csv(os.path.join(raw_dir, "sales.csv"))
    df_inventory = pd.read_csv(os.path.join(raw_dir, "inventory.csv"))
    
    # ------------------ Clean Suppliers ------------------
    print("\nCleaning Suppliers...")
    # No major anomalies introduced in suppliers, but we check for nulls
    nulls_sup = df_suppliers.isnull().sum().sum()
    print(f"Suppliers null values found: {nulls_sup}")
    df_suppliers.to_csv(os.path.join(processed_dir, "suppliers.csv"), index=False)
    
    # ------------------ Clean Warehouses ------------------
    print("Cleaning Warehouses...")
    nulls_wh = df_warehouses.isnull().sum().sum()
    print(f"Warehouses null values found: {nulls_wh}")
    df_warehouses.to_csv(os.path.join(processed_dir, "warehouses.csv"), index=False)
    
    # ------------------ Clean Products ------------------
    print("Cleaning Products...")
    
    # Text consistency in 'category'
    print("Standardizing category names...")
    print("Before:", df_products["category"].unique())
    df_products["category"] = df_products["category"].replace({
        "electronics": "Electronics",
        "ELECTR": "Electronics",
        "home & kitchen": "Home & Kitchen",
        "H&K": "Home & Kitchen"
    })
    print("After:", df_products["category"].unique())
    
    # Impute missing values in lead_time_days
    null_lead_times = df_products["lead_time_days"].isnull().sum()
    print(f"Missing lead_time_days: {null_lead_times}")
    
    # Fill with median lead time by category
    median_leads = df_products.groupby("category")["lead_time_days"].transform("median")
    df_products["lead_time_days"] = df_products["lead_time_days"].fillna(median_leads)
    # If any remaining (e.g. category has no median), fill with overall median or 7
    df_products["lead_time_days"] = df_products["lead_time_days"].fillna(7).astype(int)
    
    print(f"Remaining nulls in Products: {df_products.isnull().sum().sum()}")
    df_products.to_csv(os.path.join(processed_dir, "products.csv"), index=False)
    
    # ------------------ Clean Sales ------------------
    print("\nCleaning Sales Transactions...")
    
    # Remove duplicates
    initial_sales_rows = len(df_sales)
    df_sales = df_sales.drop_duplicates()
    duplicates_removed = initial_sales_rows - len(df_sales)
    print(f"Removed {duplicates_removed} duplicate transaction records.")
    
    # Outliers/negative quantities
    neg_qties = (df_sales["quantity_sold"] < 0).sum()
    print(f"Found {neg_qties} records with negative quantity_sold.")
    # Convert negative quantity to positive (data entry fix)
    df_sales["quantity_sold"] = df_sales["quantity_sold"].abs()
    
    # Price anomalies (selling price is more than 5x standard price in products)
    # We join with products to check selling price vs unit price
    df_sales_merged = df_sales.merge(df_products[["product_id", "unit_price"]], on="product_id", how="left")
    
    # Identify price outliers (e.g. 5x standard unit price)
    outlier_prices = df_sales_merged["selling_price_per_unit"] > (df_sales_merged["unit_price"] * 5)
    outlier_count = outlier_prices.sum()
    print(f"Found {outlier_count} price outlier transactions. Fixing to catalog unit price...")
    
    # Correct them in the original sales df
    # Match indices of outliers
    outlier_idx = df_sales_merged[outlier_prices].index
    # Map index back to df_sales and replace with unit_price
    for idx in outlier_idx:
        prod_id = df_sales.loc[idx, "product_id"]
        correct_price = df_products.loc[df_products["product_id"] == prod_id, "unit_price"].values[0]
        df_sales.loc[idx, "selling_price_per_unit"] = correct_price
        
    # Calculate revenue columns
    df_sales["revenue"] = np.round(df_sales["quantity_sold"] * df_sales["selling_price_per_unit"], 2)
    
    print(f"Sales table check: Negative quantities left? {(df_sales['quantity_sold'] < 0).sum()}")
    df_sales.to_csv(os.path.join(processed_dir, "sales.csv"), index=False)
    
    # ------------------ Clean Inventory ------------------
    print("\nCleaning Inventory Ledger...")
    
    # Negative stock on hand
    neg_stock = (df_inventory["stock_on_hand"] < 0).sum()
    print(f"Found {neg_stock} records with negative stock_on_hand.")
    df_inventory.loc[df_inventory["stock_on_hand"] < 0, "stock_on_hand"] = 0
    
    # Check for nulls
    nulls_inv = df_inventory.isnull().sum().sum()
    print(f"Inventory nulls found: {nulls_inv}")
    
    df_inventory.to_csv(os.path.join(processed_dir, "inventory.csv"), index=False)
    print("\nData Cleaning Pipeline complete. Processed files written to data/processed/")

if __name__ == "__main__":
    clean_data()
