import os
import sqlite3
import pandas as pd

def initialize_and_load_db():
    db_path = os.path.join("data", "inventory_analytics.db")
    schema_path = os.path.join("sql", "schema.sql")
    processed_dir = os.path.join("data", "processed")
    
    # Remove existing db to start fresh if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Existing database removed. Rebuilding...")
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Execute schema.sql to create tables and views
    print(f"Executing schema from {schema_path}...")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # SQLite allows executing multiple statements with executescript
    cursor.executescript(schema_sql)
    conn.commit()
    print("Database tables, indexes, and views created successfully.")
    
    # 2. Load clean CSVs into tables
    tables_to_load = {
        "suppliers": "suppliers.csv",
        "warehouses": "warehouses.csv",
        "products": "products.csv",
        "sales": "sales.csv",
        "inventory": "inventory.csv"
    }
    
    for table_name, csv_file in tables_to_load.items():
        csv_path = os.path.join(processed_dir, csv_file)
        print(f"Loading {csv_file} into SQLite table '{table_name}'...")
        
        df = pd.read_csv(csv_path)
        
        # In sales and inventory, sqlite may enforce foreign keys, 
        # so load order is: suppliers, warehouses, products, sales, inventory.
        # This is already handled by iterating in order.
        if table_name == "sales" and "revenue" in df.columns:
            df = df.drop(columns=["revenue"])
        df.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"Loaded {len(df)} rows into table '{table_name}'.")
        
    conn.commit()
    
    # Verify view executions
    print("\nVerifying database views...")
    views = ["view_product_profitability", "view_supplier_performance", "view_current_inventory"]
    for view in views:
        cursor.execute(f"SELECT COUNT(*) FROM {view}")
        cnt = cursor.fetchone()[0]
        print(f"View '{view}' contains {cnt} records.")
        
    conn.close()
    print("\nDatabase initialization and load completed successfully!")

if __name__ == "__main__":
    initialize_and_load_db()
