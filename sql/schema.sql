-- Database DDL for Inventory Performance & Stock Optimization Platform
-- Dialect: SQLite

-- Enable Foreign Key constraints
PRAGMA foreign_keys = ON;

-- 1. Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id TEXT PRIMARY KEY,
    supplier_name TEXT NOT NULL,
    contact_name TEXT,
    email TEXT,
    rating REAL CHECK(rating BETWEEN 1.0 AND 5.0),
    reliability_score REAL CHECK(reliability_score BETWEEN 0.0 AND 1.0)
);

-- 2. Warehouses Table
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id TEXT PRIMARY KEY,
    warehouse_name TEXT NOT NULL,
    location TEXT NOT NULL,
    capacity_sqft INTEGER CHECK(capacity_sqft > 0),
    operational_cost_monthly REAL CHECK(operational_cost_monthly >= 0.0)
);

-- 3. Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price REAL NOT NULL CHECK(unit_price >= 0.0),
    unit_cost REAL NOT NULL CHECK(unit_cost >= 0.0),
    supplier_id TEXT,
    lead_time_days INTEGER CHECK(lead_time_days >= 0),
    min_order_qty INTEGER CHECK(min_order_qty >= 0),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
);

-- 4. Sales Table (Transactional Log)
CREATE TABLE IF NOT EXISTS sales (
    sale_id TEXT PRIMARY KEY,
    sale_date TEXT NOT NULL, -- ISO Format: YYYY-MM-DD
    product_id TEXT NOT NULL,
    warehouse_id TEXT NOT NULL,
    quantity_sold INTEGER NOT NULL CHECK(quantity_sold > 0),
    selling_price_per_unit REAL NOT NULL CHECK(selling_price_per_unit >= 0.0),
    revenue REAL GENERATED ALWAYS AS (quantity_sold * selling_price_per_unit) STORED,
    channel TEXT CHECK(channel IN ('Online', 'Retail', 'Wholesale')),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
);

-- 5. Inventory Table (Daily snapshots)
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id TEXT PRIMARY KEY,
    date TEXT NOT NULL, -- ISO Format: YYYY-MM-DD
    product_id TEXT NOT NULL,
    warehouse_id TEXT NOT NULL,
    stock_on_hand INTEGER NOT NULL CHECK(stock_on_hand >= 0),
    stock_allocated INTEGER DEFAULT 0 CHECK(stock_allocated >= 0),
    stock_on_order INTEGER DEFAULT 0 CHECK(stock_on_order >= 0),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
);

-- Create Indexes for Query Optimization
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_prod_wh ON sales(product_id, warehouse_id);
CREATE INDEX IF NOT EXISTS idx_inventory_date ON inventory(date);
CREATE INDEX IF NOT EXISTS idx_inventory_prod_wh ON inventory(product_id, warehouse_id);

-- ------------------ Business Views ------------------

-- View: Product Profitability
CREATE VIEW IF NOT EXISTS view_product_profitability AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.unit_cost,
    p.unit_price,
    (p.unit_price - p.unit_cost) AS unit_margin,
    ROUND(((p.unit_price - p.unit_cost) / p.unit_price) * 100, 2) AS margin_percentage
FROM products p;

-- View: Supplier Summary Performance
CREATE VIEW IF NOT EXISTS view_supplier_performance AS
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.rating,
    s.reliability_score,
    COUNT(DISTINCT p.product_id) AS products_supplied,
    ROUND(AVG(p.lead_time_days), 1) AS avg_lead_time_days
FROM suppliers s
LEFT JOIN products p ON s.supplier_id = p.supplier_id
GROUP BY s.supplier_id;

-- View: Current Inventory Status (Latest Date in Snapshots)
CREATE VIEW IF NOT EXISTS view_current_inventory AS
WITH latest_date AS (
    SELECT MAX(date) AS max_date FROM inventory
)
SELECT 
    i.date,
    i.product_id,
    p.product_name,
    p.category,
    i.warehouse_id,
    w.warehouse_name,
    i.stock_on_hand,
    i.stock_allocated,
    i.stock_on_order,
    (i.stock_on_hand - i.stock_allocated) AS net_available_stock
FROM inventory i
JOIN products p ON i.product_id = p.product_id
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
WHERE i.date = (SELECT max_date FROM latest_date);
