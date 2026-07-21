import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_data():
    print("Initializing synthetic data generation...")
    np.random.seed(42)
    
    # Target folders
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    # 1. Generate Suppliers
    print("Generating Suppliers...")
    suppliers_data = {
        "supplier_id": [f"SUP{i:03d}" for i in range(1, 16)],
        "supplier_name": [
            "Apex Logistics", "Global Freight Corp", "Prime Goods Ltd", "Summit Supply Chain",
            "Integra Manufacturing", "Zenith Wholesalers", "Horizon Distribution", "Pinnacle Imports",
            "Omni Sources", "Alpha Logistics", "Vanguard Industries", "Delta Products",
            "Matrix Trade", "Quantum Corp", "Echo Supply"
        ],
        "contact_name": [
            "John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Charlie Green",
            "David White", "Eva Black", "Frank Grey", "Grace Pink", "Henry Gold",
            "Ivy Silver", "Jack Bronze", "Karen Copper", "Leo Brass", "Mia Iron"
        ],
        "email": [
            "contact@apex.com", "info@globalfreight.com", "sales@primegoods.co.uk", "summit@supply.com",
            "integra@mfg.net", "zenith@wholesale.com", "horizon@dist.org", "pinnacle@imports.com",
            "omni@sources.biz", "alpha@logistics.com", "vanguard@ind.com", "delta@products.com",
            "matrix@trade.net", "quantum@corp.com", "echo@supply.org"
        ],
        "rating": np.round(np.random.uniform(3.0, 5.0, 15), 1),
        "reliability_score": np.round(np.random.uniform(0.75, 0.98, 15), 2)
    }
    df_suppliers = pd.DataFrame(suppliers_data)
    
    # 2. Generate Warehouses
    print("Generating Warehouses...")
    warehouses_data = {
        "warehouse_id": [f"WH{i:02d}" for i in range(1, 6)],
        "warehouse_name": ["North Hub", "South Terminal", "East Gate", "West Depot", "Central Fulfillment"],
        "location": ["Chicago, IL", "Atlanta, GA", "Newark, NJ", "Los Angeles, CA", "Dallas, TX"],
        "capacity_sqft": [150000, 200000, 180000, 250000, 350000],
        "operational_cost_monthly": [45000.0, 55000.0, 50000.0, 75000.0, 95000.0]
    }
    df_warehouses = pd.DataFrame(warehouses_data)
    
    # 3. Generate Products
    print("Generating Products...")
    categories = ["Electronics", "Apparel", "Home & Kitchen", "Office Supplies", "Automotive"]
    product_prefixes = {
        "Electronics": ["Smartphone", "Laptop", "Headphones", "Smartwatch", "Tablet", "Camera", "Speaker"],
        "Apparel": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Socks", "Cap", "Hoodie"],
        "Home & Kitchen": ["Blender", "Coffee Maker", "Toaster", "Air Fryer", "Cookware Set", "Vacuum Cleaner"],
        "Office Supplies": ["Notebook", "Desk Organizer", "Ergonomic Chair", "Gel Pens", "Whiteboard", "Stapler"],
        "Automotive": ["Car Charger", "Seat Cover", "Floor Mats", "Wiper Blades", "Dash Cam", "Tire Inflator"]
    }
    
    products = []
    prod_id = 1
    for cat in categories:
        prefixes = product_prefixes[cat]
        for pref in prefixes:
            # Create multiple models/variants per prefix
            for model in ["Standard", "Pro", "Lite", "Elite"]:
                unit_cost = np.round(np.random.uniform(5.0, 450.0), 2)
                # Markup between 30% and 120%
                unit_price = np.round(unit_cost * np.random.uniform(1.3, 2.2), 2)
                supplier = np.random.choice(df_suppliers["supplier_id"])
                lead_time = int(np.random.randint(3, 22))
                min_order = int(np.random.choice([10, 50, 100, 200, 500]))
                
                products.append({
                    "product_id": f"PROD{prod_id:04d}",
                    "product_name": f"{pref} - {model}",
                    "category": cat,
                    "unit_price": unit_price,
                    "unit_cost": unit_cost,
                    "supplier_id": supplier,
                    "lead_time_days": lead_time,
                    "min_order_qty": min_order
                })
                prod_id += 1
                
    df_products = pd.DataFrame(products)
    
    # 4. Generate Sales Transactions (1 Year of daily data)
    print("Generating Sales transactions...")
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range(365)]
    
    sales = []
    sale_id_counter = 1
    
    # Category coefficients for demand fluctuations
    cat_seasonal_factors = {
        "Electronics": [1.0, 0.9, 0.95, 1.0, 1.1, 1.05, 1.0, 1.1, 1.2, 1.15, 1.3, 1.5], # peak in Nov-Dec
        "Apparel": [1.2, 1.1, 1.0, 1.1, 1.2, 1.3, 1.2, 1.1, 1.1, 1.2, 1.4, 1.6], # summer + winter peaks
        "Home & Kitchen": [1.0, 0.9, 1.0, 1.1, 1.1, 1.0, 1.0, 0.95, 1.1, 1.2, 1.4, 1.5],
        "Office Supplies": [1.3, 1.2, 1.0, 0.9, 0.9, 0.8, 1.1, 1.4, 1.2, 1.0, 1.0, 1.1], # back to school Aug-Sep
        "Automotive": [0.9, 0.9, 1.0, 1.1, 1.2, 1.25, 1.2, 1.1, 1.0, 1.0, 0.9, 0.9] # summer roadtrips
    }
    
    for date in dates:
        month = date.month
        day_of_week = date.weekday()
        # Weekends have 30% higher sales
        weekend_boost = 1.3 if day_of_week >= 5 else 1.0
        
        # Decide how many transactions on this day (100 to 200)
        num_transactions = int(np.random.randint(80, 160) * weekend_boost)
        
        for _ in range(num_transactions):
            prod = df_products.sample(1).iloc[0]
            cat = prod["category"]
            m_factor = cat_seasonal_factors[cat][month - 1]
            
            # Base qty based on category and cost
            if prod["unit_cost"] > 250:
                base_qty = np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1])
            elif prod["unit_cost"] > 50:
                base_qty = np.random.choice([1, 2, 3, 4, 5], p=[0.4, 0.3, 0.15, 0.1, 0.05])
            else:
                base_qty = int(np.random.randint(1, 15))
                
            qty = int(max(1, np.round(base_qty * m_factor)))
            wh = np.random.choice(df_warehouses["warehouse_id"], p=[0.15, 0.20, 0.15, 0.20, 0.30]) # Central is largest
            channel = np.random.choice(["Online", "Retail", "Wholesale"], p=[0.55, 0.35, 0.10])
            
            sales.append({
                "sale_id": f"TXN{sale_id_counter:06d}",
                "sale_date": date.strftime("%Y-%m-%d"),
                "product_id": prod["product_id"],
                "warehouse_id": wh,
                "quantity_sold": qty,
                "selling_price_per_unit": prod["unit_price"],
                "channel": channel
            })
            sale_id_counter += 1
            
    df_sales = pd.DataFrame(sales)
    
    # 5. Generate Inventory Snapshots (Daily for last 60 days)
    print("Generating Inventory Snapshots...")
    snapshot_dates = [datetime.now() - timedelta(days=x) for x in range(60)]
    snapshot_dates.reverse()
    
    inventory_ledger = []
    inv_id_counter = 1
    
    # Establish initial stock levels for all product-warehouse combinations
    stock_levels = {}
    for p_id in df_products["product_id"]:
        for w_id in df_warehouses["warehouse_id"]:
            # Initial stock based on category and warehouse size
            multiplier = 1.5 if w_id == "WH05" else 1.0
            stock_levels[(p_id, w_id)] = int(np.random.randint(20, 300) * multiplier)
            
    # Iterate through days and adjust inventory based on sales
    for s_date in snapshot_dates:
        date_str = s_date.strftime("%Y-%m-%d")
        
        # Filter sales for this day
        day_sales = df_sales[df_sales["sale_date"] == date_str]
        sales_by_pw = day_sales.groupby(["product_id", "warehouse_id"])["quantity_sold"].sum().to_dict()
        
        for (p_id, w_id), current_stock in stock_levels.items():
            qty_sold = sales_by_pw.get((p_id, w_id), 0)
            
            # Stock decrease from sales
            new_stock = max(0, current_stock - qty_sold)
            
            # Safety stock and replenishment logic simulation
            p_info = df_products[df_products["product_id"] == p_id].iloc[0]
            lead_time = p_info["lead_time_days"]
            min_order = p_info["min_order_qty"]
            
            # Check if we need to trigger reorder (simulated logic)
            # Reorder point is roughly 5 * daily sales
            rop = int(lead_time * 2.5) # simple approximation
            
            stock_on_order = 0
            # If stock level drops below ROP, order min_order_qty (placed with supplier)
            if new_stock < rop:
                # 30% chance there is a pending order arriving soon (represented as stock_on_order)
                if np.random.random() < 0.3:
                    stock_on_order = min_order
                # 15% chance it actually arrives today (re-stock)
                if np.random.random() < 0.15:
                    new_stock += min_order
                    stock_on_order = 0
            
            # Allocate stock (allocated but not shipped yet, e.g., 5% of stock)
            stock_allocated = int(np.round(new_stock * np.random.uniform(0.0, 0.15)))
            
            inventory_ledger.append({
                "inventory_id": f"INV{inv_id_counter:07d}",
                "date": date_str,
                "product_id": p_id,
                "warehouse_id": w_id,
                "stock_on_hand": new_stock,
                "stock_allocated": stock_allocated,
                "stock_on_order": stock_on_order
            })
            inv_id_counter += 1
            
            # Save final stock level for next day's simulation
            stock_levels[(p_id, w_id)] = new_stock
            
    df_inventory = pd.DataFrame(inventory_ledger)
    
    # ------------------ INTRODUCE ANOMALIES (For Data Cleaning step) ------------------
    print("Introducing intentional data anomalies...")
    
    # Anomaly 1: Missing values (NaNs)
    # Products table: some nulls in lead_time_days and min_order_qty
    null_p_idx1 = df_products.sample(frac=0.08).index
    df_products.loc[null_p_idx1, "lead_time_days"] = np.nan
    
    # Anomaly 2: Category text inconsistencies
    # Mix of cases and shorthand
    df_products.loc[df_products["category"] == "Electronics", "category"] = np.random.choice(
        ["Electronics", "electronics", "ELECTR"], len(df_products[df_products["category"] == "Electronics"]), p=[0.7, 0.2, 0.1]
    )
    df_products.loc[df_products["category"] == "Home & Kitchen", "category"] = np.random.choice(
        ["Home & Kitchen", "home & kitchen", "H&K"], len(df_products[df_products["category"] == "Home & Kitchen"]), p=[0.8, 0.1, 0.1]
    )
    
    # Anomaly 3: Sales duplicate rows
    # Duplicate ~1% of sales
    dup_sales = df_sales.sample(frac=0.01)
    df_sales = pd.concat([df_sales, dup_sales], ignore_index=True)
    
    # Anomaly 4: Outliers / Invalid values
    # Sales table: negative quantities
    neg_qty_idx = df_sales.sample(n=10).index
    df_sales.loc[neg_qty_idx, "quantity_sold"] = df_sales.loc[neg_qty_idx, "quantity_sold"] * -1
    
    # Sales table: extreme prices
    ext_price_idx = df_sales.sample(n=5).index
    df_sales.loc[ext_price_idx, "selling_price_per_unit"] = df_sales.loc[ext_price_idx, "selling_price_per_unit"] * 10
    
    # Inventory table: negative stock on hand (invalid)
    neg_stock_idx = df_inventory.sample(n=15).index
    df_inventory.loc[neg_stock_idx, "stock_on_hand"] = -5
    
    # Save raw CSV datasets
    print("Exporting raw CSV files to data/raw/...")
    df_suppliers.to_csv(os.path.join(raw_dir, "suppliers.csv"), index=False)
    df_warehouses.to_csv(os.path.join(raw_dir, "warehouses.csv"), index=False)
    df_products.to_csv(os.path.join(raw_dir, "products.csv"), index=False)
    df_sales.to_csv(os.path.join(raw_dir, "sales.csv"), index=False)
    df_inventory.to_csv(os.path.join(raw_dir, "inventory.csv"), index=False)
    
    print("Synthetic data generated successfully with anomalies!")
    print(f"Suppliers count: {len(df_suppliers)}")
    print(f"Warehouses count: {len(df_warehouses)}")
    print(f"Products count: {len(df_products)}")
    print(f"Sales records: {len(df_sales)}")
    print(f"Inventory ledger rows: {len(df_inventory)}")

if __name__ == "__main__":
    generate_synthetic_data()
