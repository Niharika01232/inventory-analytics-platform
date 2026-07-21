-- ==============================================================================
-- INVENTORY ANALYTICS & STOCK OPTIMIZATION PLATFORM: BUSINESS SQL QUERIES
-- Dialect: SQLite
-- Total Queries: 45 Queries grouped by analytical complexity
-- ==============================================================================

-- ==============================================================================
-- GROUP 1: CORE DATA EXPLORATION & PROFILE QUERIES (1-5)
-- Goal: Basic audits, metadata verification, and simple aggregations
-- ==============================================================================

-- Query 1: Total records in each database table to verify ingestion completeness
SELECT 'suppliers' AS table_name, COUNT(*) AS row_count FROM suppliers
UNION ALL
SELECT 'warehouses', COUNT(*) FROM warehouses
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sales', COUNT(*) FROM sales
UNION ALL
SELECT 'inventory', COUNT(*) FROM inventory;

-- Query 2: List top 10 products with the highest unit price
SELECT product_id, product_name, category, unit_price, unit_cost
FROM products
ORDER BY unit_price DESC
LIMIT 10;

-- Query 3: Distinct categories list and the count of unique SKUs in each
SELECT category, COUNT(product_id) AS total_skus
FROM products
GROUP BY category
ORDER BY total_skus DESC;

-- Query 4: Basic sales channel distribution analysis
SELECT channel, COUNT(*) AS txn_count, SUM(quantity_sold) AS total_qty, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY channel
ORDER BY total_revenue DESC;

-- Query 5: Average supplier ratings and reliability scores
SELECT 
    ROUND(AVG(rating), 2) AS avg_rating, 
    ROUND(AVG(reliability_score) * 100, 2) AS avg_reliability_pct
FROM suppliers;


-- ==============================================================================
-- GROUP 2: REVENUE PERFORMANCE & SALES ANALYTICS (6-15)
-- Goal: Identify revenue drivers, seasonal shifts, and transaction characteristics
-- ==============================================================================

-- Query 6: Top 10 products generating the highest total revenue
SELECT 
    s.product_id, 
    p.product_name, 
    p.category, 
    SUM(s.quantity_sold) AS total_qty_sold,
    ROUND(SUM(s.revenue), 2) AS total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY s.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;

-- Query 7: Monthly sales trend (Revenue & Volume)
SELECT 
    STRFTIME('%Y-%m', sale_date) AS sales_month,
    COUNT(sale_id) AS order_count,
    SUM(quantity_sold) AS units_sold,
    ROUND(SUM(revenue), 2) AS gross_revenue
FROM sales
GROUP BY sales_month
ORDER BY sales_month ASC;

-- Query 8: Average Order Value (AOV) by sales channel
SELECT 
    channel,
    COUNT(DISTINCT sale_id) AS total_orders,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(revenue) / COUNT(DISTINCT sale_id), 2) AS average_order_value
FROM sales
GROUP BY channel;

-- Query 9: Profit Margin analysis by Product Category
SELECT 
    p.category,
    ROUND(SUM(s.revenue), 2) AS total_revenue,
    ROUND(SUM(s.quantity_sold * p.unit_cost), 2) AS total_cost,
    ROUND(SUM(s.revenue) - SUM(s.quantity_sold * p.unit_cost), 2) AS total_profit,
    ROUND(((SUM(s.revenue) - SUM(s.quantity_sold * p.unit_cost)) / SUM(s.revenue)) * 100, 2) AS profit_margin_percentage
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY total_profit DESC;

-- Query 10: Weekday vs Weekend Sales Performance
SELECT 
    CASE 
        WHEN STRFTIME('%w', sale_date) IN ('0', '6') THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(sale_id) AS total_orders,
    SUM(quantity_sold) AS units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS avg_txn_value
FROM sales
GROUP BY day_type;

-- Query 11: Top-performing warehouse by revenue contribution
SELECT 
    s.warehouse_id,
    w.warehouse_name,
    w.location,
    ROUND(SUM(s.revenue), 2) AS total_revenue,
    ROUND((SUM(s.revenue) / (SELECT SUM(revenue) FROM sales)) * 100, 2) AS revenue_pct_contribution
FROM sales s
JOIN warehouses w ON s.warehouse_id = w.warehouse_id
GROUP BY s.warehouse_id, w.warehouse_name, w.location
ORDER BY total_revenue DESC;

-- Query 12: Sales velocity - Category sales share per warehouse
SELECT 
    s.warehouse_id,
    w.warehouse_name,
    p.category,
    SUM(s.quantity_sold) AS total_units_sold,
    ROUND(SUM(s.revenue), 2) AS total_revenue
FROM sales s
JOIN warehouses w ON s.warehouse_id = w.warehouse_id
JOIN products p ON s.product_id = p.product_id
GROUP BY s.warehouse_id, w.warehouse_name, p.category
ORDER BY s.warehouse_id, total_revenue DESC;

-- Query 13: Product cost-price markup analysis
SELECT 
    product_id,
    product_name,
    unit_cost,
    unit_price,
    ROUND(unit_price - unit_cost, 2) AS markup_abs,
    ROUND(((unit_price - unit_cost) / unit_cost) * 100, 2) AS markup_pct
FROM products
ORDER BY markup_pct DESC
LIMIT 15;

-- Query 14: Daily average revenue by month to detect operational peaks
SELECT 
    STRFTIME('%Y-%m', sale_date) AS sales_month,
    COUNT(DISTINCT sale_date) AS active_days,
    ROUND(SUM(revenue), 2) AS monthly_revenue,
    ROUND(SUM(revenue) / COUNT(DISTINCT sale_date), 2) AS daily_avg_revenue
FROM sales
GROUP BY sales_month
ORDER BY sales_month;

-- Query 15: Low performing SKUs (Revenue < $2000 in the past year)
SELECT 
    s.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(s.revenue), 2) AS total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY s.product_id, p.product_name, p.category
HAVING total_revenue < 2000.0
ORDER BY total_revenue ASC;


-- ==============================================================================
-- GROUP 3: WAREHOUSE & INVENTORY SNAPSHOT METRICS (16-25)
-- Goal: Current inventory valuations, stock distributions, and space usage
-- ==============================================================================

-- Query 16: Total current inventory valuation across all warehouses
SELECT 
    w.warehouse_id,
    w.warehouse_name,
    SUM(i.stock_on_hand) AS total_units,
    ROUND(SUM(i.stock_on_hand * p.unit_cost), 2) AS inventory_value_cost,
    ROUND(SUM(i.stock_on_hand * p.unit_price), 2) AS inventory_value_retail
FROM view_current_inventory i
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
JOIN products p ON i.product_id = p.product_id
GROUP BY w.warehouse_id, w.warehouse_name
ORDER BY inventory_value_cost DESC;

-- Query 17: Average holding cost per warehouse (Assuming 2% monthly cost of inventory value)
SELECT 
    w.warehouse_id,
    w.warehouse_name,
    ROUND(SUM(i.stock_on_hand * p.unit_cost), 2) AS current_inventory_value,
    ROUND(SUM(i.stock_on_hand * p.unit_cost) * 0.02, 2) AS monthly_holding_cost_est,
    w.operational_cost_monthly AS warehouse_fixed_cost
FROM view_current_inventory i
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
JOIN products p ON i.product_id = p.product_id
GROUP BY w.warehouse_id, w.warehouse_name;

-- Query 18: Out-of-Stock SKUs (Stock on hand is 0)
SELECT 
    product_id,
    product_name,
    category,
    warehouse_name,
    stock_on_hand,
    stock_on_order
FROM view_current_inventory
WHERE stock_on_hand = 0
ORDER BY stock_on_order DESC;

-- Query 19: High-risk allocated stock (Stock allocated exceeds stock on hand)
SELECT 
    product_id,
    product_name,
    warehouse_name,
    stock_on_hand,
    stock_allocated,
    (stock_allocated - stock_on_hand) AS short_units
FROM view_current_inventory
WHERE stock_allocated > stock_on_hand;

-- Query 20: Product stock concentration (Percentage of inventory in each warehouse)
SELECT 
    i.product_id,
    p.product_name,
    SUM(CASE WHEN i.warehouse_id = 'WH01' THEN i.stock_on_hand ELSE 0 END) AS wh01_stock,
    SUM(CASE WHEN i.warehouse_id = 'WH02' THEN i.stock_on_hand ELSE 0 END) AS wh02_stock,
    SUM(CASE WHEN i.warehouse_id = 'WH03' THEN i.stock_on_hand ELSE 0 END) AS wh03_stock,
    SUM(CASE WHEN i.warehouse_id = 'WH04' THEN i.stock_on_hand ELSE 0 END) AS wh04_stock,
    SUM(CASE WHEN i.warehouse_id = 'WH05' THEN i.stock_on_hand ELSE 0 END) AS wh05_stock,
    SUM(i.stock_on_hand) AS total_stock
FROM view_current_inventory i
JOIN products p ON i.product_id = p.product_id
GROUP BY i.product_id, p.product_name
LIMIT 15;

-- Query 21: Stock Status Classification (Overstocked vs Healthy vs Understocked)
-- Criteria: Overstocked (> 300 units), Understocked (< 20 units), Out of stock (0), Normal (20-300)
SELECT 
    CASE 
        WHEN stock_on_hand = 0 THEN '1. Out of Stock'
        WHEN stock_on_hand < 20 THEN '2. Understocked'
        WHEN stock_on_hand > 300 THEN '4. Overstocked'
        ELSE '3. Healthy'
    END AS stock_status,
    COUNT(DISTINCT product_id) AS unique_skus,
    SUM(stock_on_hand) AS total_units_in_status
FROM view_current_inventory
GROUP BY stock_status
ORDER BY stock_status;

-- Query 22: Days Inventory Outstanding (DIO) per product category
-- DIO = (Average Inventory Value / Cost of Goods Sold) * 365
-- We'll approximate using current inventory vs COGS over past 365 days
WITH category_cogs AS (
    SELECT 
        p.category,
        SUM(s.quantity_sold * p.unit_cost) AS annual_cogs
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category
),
category_inventory AS (
    SELECT 
        p.category,
        SUM(i.stock_on_hand * p.unit_cost) AS current_inv_value
    FROM view_current_inventory i
    JOIN products p ON i.product_id = p.product_id
    GROUP BY p.category
)
SELECT 
    ci.category,
    ROUND(ci.current_inv_value, 2) AS current_inventory_value,
    ROUND(cc.annual_cogs, 2) AS annual_cogs,
    ROUND((ci.current_inv_value / cc.annual_cogs) * 365, 1) AS days_inventory_outstanding
FROM category_inventory ci
JOIN category_cogs cc ON ci.category = cc.category;

-- Query 23: Inventory Turnover Ratio (ITR) per product category
-- ITR = Cost of Goods Sold / Average Inventory Value
-- High ITR means fast-moving inventory; low ITR implies slow/dead stock.
WITH category_metrics AS (
    SELECT 
        p.category,
        SUM(s.quantity_sold * p.unit_cost) AS annual_cogs,
        (SELECT SUM(stock_on_hand * p2.unit_cost) 
         FROM view_current_inventory curr_i 
         JOIN products p2 ON curr_i.product_id = p2.product_id 
         WHERE p2.category = p.category) AS current_inv_val
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category
)
SELECT 
    category,
    ROUND(annual_cogs, 2) AS annual_cogs,
    ROUND(current_inv_val, 2) AS current_inv_value,
    ROUND(annual_cogs / current_inv_val, 2) AS inventory_turnover_ratio
FROM category_metrics;

-- Query 24: Top 10 products with the lowest inventory turnover (Potential dead stock)
WITH product_sales AS (
    SELECT 
        product_id,
        SUM(quantity_sold) AS units_sold
    FROM sales
    GROUP BY product_id
),
product_inv AS (
    SELECT 
        product_id,
        SUM(stock_on_hand) AS total_stock
    FROM view_current_inventory
    GROUP BY product_id
)
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    COALESCE(s.units_sold, 0) AS annual_units_sold,
    i.total_stock AS current_units_in_stock,
    ROUND(CAST(COALESCE(s.units_sold, 0) AS REAL) / NULLIF(i.total_stock, 0), 2) AS sku_turnover_ratio
FROM products p
JOIN product_inv i ON p.product_id = i.product_id
LEFT JOIN product_sales s ON p.product_id = s.product_id
ORDER BY sku_turnover_ratio ASC
LIMIT 10;

-- Query 25: Pending Order Ratio (Allocated vs On Order)
SELECT 
    warehouse_name,
    SUM(stock_on_hand) AS stock_on_hand,
    SUM(stock_allocated) AS stock_allocated,
    SUM(stock_on_order) AS stock_on_order,
    ROUND((CAST(SUM(stock_allocated) AS REAL) / SUM(stock_on_hand)) * 100, 2) AS allocation_percentage,
    ROUND((CAST(SUM(stock_on_order) AS REAL) / SUM(stock_on_hand)) * 100, 2) AS replenishing_percentage
FROM view_current_inventory
GROUP BY warehouse_name;


-- ==============================================================================
-- GROUP 4: WINDOW FUNCTIONS & COMPLEX ANALYTICS (26-35)
-- Goal: Cumulative sums, rankings, rolling averages, and lead/lag analyses
-- ==============================================================================

-- Query 26: Rank products by revenue within each category (Window Function)
WITH product_revenue AS (
    SELECT 
        p.category,
        p.product_id,
        p.product_name,
        ROUND(SUM(s.revenue), 2) AS total_revenue
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT 
    category,
    product_id,
    product_name,
    total_revenue,
    RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS revenue_rank
FROM product_revenue
WHERE revenue_rank <= 3; -- Show top 3 products in each category

-- Query 27: Monthly running total of sales revenue (Cumulative Sum)
WITH monthly_sales AS (
    SELECT 
        STRFTIME('%Y-%m', sale_date) AS sales_month,
        SUM(revenue) AS monthly_revenue
    FROM sales
    GROUP BY sales_month
)
SELECT 
    sales_month,
    ROUND(monthly_revenue, 2) AS monthly_revenue,
    ROUND(SUM(monthly_revenue) OVER (ORDER BY sales_month), 2) AS running_total_revenue
FROM monthly_sales;

-- Query 28: Rolling 7-day average sales revenue (Moving Average)
WITH daily_sales AS (
    SELECT 
        sale_date,
        SUM(revenue) AS daily_rev
    FROM sales
    GROUP BY sale_date
)
SELECT 
    sale_date,
    ROUND(daily_rev, 2) AS daily_revenue,
    ROUND(AVG(daily_rev) OVER (ORDER BY sale_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS rolling_7d_avg
FROM daily_sales
ORDER BY sale_date DESC
LIMIT 15;

-- Query 29: Month-over-Month (MoM) sales revenue growth rate (LAG Function)
WITH monthly_sales AS (
    SELECT 
        STRFTIME('%Y-%m', sale_date) AS sales_month,
        SUM(revenue) AS monthly_rev
    FROM sales
    GROUP BY sales_month
)
SELECT 
    sales_month,
    ROUND(monthly_rev, 2) AS current_month_revenue,
    ROUND(LAG(monthly_rev, 1) OVER (ORDER BY sales_month), 2) AS prior_month_revenue,
    ROUND(((monthly_rev - LAG(monthly_rev, 1) OVER (ORDER BY sales_month)) / LAG(monthly_rev, 1) OVER (ORDER BY sales_month)) * 100, 2) AS mom_growth_pct
FROM monthly_sales;

-- Query 30: Sales quantity percentile ranking across all orders
SELECT 
    sale_id,
    product_id,
    quantity_sold,
    ROUND(PERCENT_RANK() OVER (ORDER BY quantity_sold), 4) * 100 AS quantity_percentile
FROM sales
ORDER BY quantity_sold DESC
LIMIT 15;

-- Query 31: Find first and last sales dates for each product
SELECT 
    product_id,
    MIN(sale_date) AS first_sale_date,
    MAX(sale_date) AS last_sale_date,
    JULIANDAY(MAX(sale_date)) - JULIANDAY(MIN(sale_date)) AS sales_duration_days
FROM sales
GROUP BY product_id
LIMIT 10;

-- Query 32: Classify order sizes into baskets using CASE statement
SELECT 
    basket_size,
    COUNT(*) AS order_count,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS avg_order_revenue
FROM (
    SELECT 
        sale_id,
        revenue,
        CASE 
            WHEN quantity_sold = 1 THEN 'Single Unit (1)'
            WHEN quantity_sold BETWEEN 2 AND 5 THEN 'Small Basket (2-5)'
            WHEN quantity_sold BETWEEN 6 AND 10 THEN 'Medium Basket (6-10)'
            ELSE 'Bulk Order (>10)'
        END AS basket_size
    FROM sales
)
GROUP BY basket_size
ORDER BY order_count DESC;

-- Query 33: Identifying "Super-Users" (Customers/Transactions with above average basket size)
WITH avg_qty AS (
    SELECT AVG(quantity_sold) AS overall_avg FROM sales
)
SELECT 
    sale_id,
    sale_date,
    product_id,
    quantity_sold,
    ROUND(revenue, 2) AS revenue,
    ROUND(quantity_sold - (SELECT overall_avg FROM avg_qty), 2) AS variance_from_average
FROM sales
WHERE quantity_sold > (SELECT overall_avg FROM avg_qty) * 2.5
ORDER BY quantity_sold DESC
LIMIT 10;

-- Query 34: Rolling 3-Month average quantity sold by product category
WITH monthly_cat_qty AS (
    SELECT 
        STRFTIME('%Y-%m', s.sale_date) AS sales_month,
        p.category,
        SUM(s.quantity_sold) AS monthly_units
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY sales_month, p.category
)
SELECT 
    sales_month,
    category,
    monthly_units,
    ROUND(AVG(monthly_units) OVER (PARTITION BY category ORDER BY sales_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS rolling_3m_avg_units
FROM monthly_cat_qty
ORDER BY category, sales_month;

-- Query 35: Top sales channels per product category by volume
WITH channel_shares AS (
    SELECT 
        p.category,
        s.channel,
        SUM(s.quantity_sold) AS total_qty,
        RANK() OVER (PARTITION BY p.category ORDER BY SUM(s.quantity_sold) DESC) AS channel_rank
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category, s.channel
)
SELECT category, channel, total_qty
FROM channel_shares
WHERE channel_rank = 1;


-- ==============================================================================
-- GROUP 5: SUPPLY CHAIN OPTIMIZATION & INVENTORY HEALTH (36-45)
-- Goal: Reorder points, safety stock alerts, dead stock flags, and supplier analysis
-- ==============================================================================

-- Query 36: Reorder Alert System (ROP calculation in SQL)
-- ROP = (Average Daily Sales * Lead Time) + Safety Stock
-- For SQLite simplicity, we'll estimate daily sales as annual sales / 365
-- We assume Safety Stock = 2 days of average sales
WITH sku_daily_demand AS (
    SELECT 
        product_id,
        CAST(SUM(quantity_sold) AS REAL) / 365.0 AS avg_daily_demand
    FROM sales
    GROUP BY product_id
)
SELECT 
    i.product_id,
    p.product_name,
    i.warehouse_id,
    i.stock_on_hand,
    i.stock_on_order,
    p.lead_time_days,
    ROUND(dd.avg_daily_demand, 2) AS daily_demand_units,
    ROUND((dd.avg_daily_demand * p.lead_time_days) + (dd.avg_daily_demand * 2.0), 0) AS reorder_point
FROM view_current_inventory i
JOIN products p ON i.product_id = p.product_id
JOIN sku_daily_demand dd ON i.product_id = dd.product_id
WHERE i.stock_on_hand <= ((dd.avg_daily_demand * p.lead_time_days) + (dd.avg_daily_demand * 2.0))
  AND i.stock_on_order = 0 -- Reorder needed because no pending delivery exists
ORDER BY i.stock_on_hand ASC
LIMIT 15;

-- Query 37: Slow-moving and Dead Stock Identification (No sales in 30 / 90 days)
-- As of the max sales date in the database
WITH last_sales AS (
    SELECT 
        product_id,
        MAX(sale_date) AS last_sold_date,
        (SELECT MAX(sale_date) FROM sales) AS max_system_date
    FROM sales
    GROUP BY product_id
),
dead_stock_candidates AS (
    SELECT 
        ls.product_id,
        ls.last_sold_date,
        CAST(JULIANDAY(ls.max_system_date) - JULIANDAY(ls.last_sold_date) AS INT) AS days_since_last_sale
    FROM last_sales ls
)
SELECT 
    dsc.product_id,
    p.product_name,
    p.category,
    dsc.days_since_last_sale,
    SUM(i.stock_on_hand) AS total_stock_on_hand,
    ROUND(SUM(i.stock_on_hand * p.unit_cost), 2) AS tied_up_capital,
    CASE 
        WHEN dsc.days_since_last_sale > 90 THEN 'Dead Stock (>90 Days)'
        WHEN dsc.days_since_last_sale > 30 THEN 'Slow Moving (30-90 Days)'
        ELSE 'Active'
    END AS movement_class
FROM dead_stock_candidates dsc
JOIN products p ON dsc.product_id = p.product_id
JOIN view_current_inventory i ON dsc.product_id = i.product_id
WHERE dsc.days_since_last_sale > 30
GROUP BY dsc.product_id, p.product_name, p.category, dsc.days_since_last_sale, movement_class
ORDER BY tied_up_capital DESC
LIMIT 15;

-- Query 38: Economic Order Quantity (EOQ) Estimation in SQL
-- EOQ = SQRT((2 * Annual Demand * Ordering Cost) / Holding Cost per Unit)
-- Assume: Ordering cost (S) = $150 per order, annual holding cost rate (H_pct) = 15% of product cost
WITH annual_demand AS (
    SELECT 
        product_id,
        SUM(quantity_sold) AS d_annual
    FROM sales
    GROUP BY product_id
)
SELECT 
    p.product_id,
    p.product_name,
    ad.d_annual AS annual_demand_units,
    p.unit_cost,
    ROUND(p.unit_cost * 0.15, 2) AS unit_holding_cost_annual,
    ROUND(SQRT((2 * ad.d_annual * 150.0) / (p.unit_cost * 0.15)), 0) AS economic_order_quantity,
    p.min_order_qty AS supplier_min_order
FROM products p
JOIN annual_demand ad ON p.product_id = ad.product_id
LIMIT 15;

-- Query 39: ABC Analysis (Revenue-based SKU categorization)
-- A: Top 70% of total revenue, B: Next 20%, C: Bottom 10%
WITH product_sales AS (
    SELECT 
        product_id,
        SUM(revenue) AS sku_revenue
    FROM sales
    GROUP BY product_id
),
sku_cumulative AS (
    SELECT 
        ps.product_id,
        ps.sku_revenue,
        SUM(ps.sku_revenue) OVER (ORDER BY ps.sku_revenue DESC) AS cumulative_revenue,
        (SELECT SUM(revenue) FROM sales) AS total_revenue
    FROM product_sales ps
)
SELECT 
    product_id,
    ROUND(sku_revenue, 2) AS sku_revenue,
    ROUND((sku_revenue / total_revenue) * 100, 2) AS revenue_share_pct,
    ROUND((cumulative_revenue / total_revenue) * 100, 2) AS cumulative_share_pct,
    CASE 
        WHEN (cumulative_revenue / total_revenue) <= 0.70 THEN 'A'
        WHEN (cumulative_revenue / total_revenue) <= 0.90 THEN 'B'
        ELSE 'C'
    END AS abc_class
FROM sku_cumulative
ORDER BY sku_revenue DESC
LIMIT 20;

-- Query 40: XYZ Analysis (Demand Variability / Coefficient of Variation)
-- X: Low variation (CV < 0.2), Y: Medium variation (0.2 <= CV <= 0.5), Z: High variation (CV > 0.5)
-- We calculate monthly sales standard deviation and mean for each product
WITH monthly_sku_sales AS (
    SELECT 
        product_id,
        STRFTIME('%Y-%m', sale_date) AS sales_month,
        SUM(quantity_sold) AS monthly_qty
    FROM sales
    GROUP BY product_id, sales_month
),
sku_variance AS (
    SELECT 
        product_id,
        AVG(monthly_qty) AS avg_monthly_qty,
        -- SQLite standard deviation approximation since SQLite doesn't have STDDEV built-in
        -- Approximating sample variance = (SUM(x^2) - N*mean^2) / (N - 1)
        -- We will compute CV based on mathematical approximation
        SQRT(
            (SUM(monthly_qty * monthly_qty) - COUNT(monthly_qty) * AVG(monthly_qty) * AVG(monthly_qty)) 
            / NULLIF(COUNT(monthly_qty) - 1, 0)
        ) AS stddev_monthly_qty
    FROM monthly_sku_sales
    GROUP BY product_id
)
SELECT 
    sv.product_id,
    p.product_name,
    p.category,
    ROUND(sv.avg_monthly_qty, 1) AS avg_monthly_demand,
    ROUND(sv.stddev_monthly_qty, 1) AS stddev_monthly_demand,
    ROUND(sv.stddev_monthly_qty / NULLIF(sv.avg_monthly_qty, 0), 3) AS coefficient_of_variation,
    CASE 
        WHEN (sv.stddev_monthly_qty / sv.avg_monthly_qty) < 0.25 THEN 'X (Stable)'
        WHEN (sv.stddev_monthly_qty / sv.avg_monthly_qty) BETWEEN 0.25 AND 0.6 THEN 'Y (Variable)'
        ELSE 'Z (Highly Erratic)'
    END AS xyz_class
FROM sku_variance sv
JOIN products p ON sv.product_id = p.product_id
WHERE sv.avg_monthly_qty > 0
ORDER BY coefficient_of_variation ASC
LIMIT 15;

-- Query 41: Combined ABC-XYZ Matrix Inventory Valuation
-- Creates 9 segments (AX, AY, AZ, BX, BY, BZ, CX, CY, CZ) to drive replenishment policies
WITH sku_abc AS (
    SELECT 
        product_id,
        CASE 
            WHEN cumulative_share <= 0.70 THEN 'A'
            WHEN cumulative_share <= 0.90 THEN 'B'
            ELSE 'C'
        END AS abc_class
    FROM (
        SELECT 
            product_id,
            SUM(revenue) OVER (ORDER BY SUM(revenue) DESC) / (SELECT SUM(revenue) FROM sales) AS cumulative_share
        FROM sales
        GROUP BY product_id
    )
),
sku_xyz AS (
    SELECT 
        product_id,
        CASE 
            WHEN cv < 0.35 THEN 'X'
            WHEN cv BETWEEN 0.35 AND 0.7 THEN 'Y'
            ELSE 'Z'
        END AS xyz_class
    FROM (
        SELECT 
            product_id,
            -- Approximated coefficient of variation
            (
                SQRT((SUM(quantity_sold * quantity_sold) - COUNT(quantity_sold) * AVG(quantity_sold) * AVG(quantity_sold)) 
                / NULLIF(COUNT(quantity_sold) - 1, 0))
            ) / NULLIF(AVG(quantity_sold), 0) AS cv
        FROM (
            SELECT product_id, STRFTIME('%Y-%m', sale_date) AS mth, SUM(quantity_sold) AS quantity_sold
            FROM sales GROUP BY product_id, mth
        )
        GROUP BY product_id
    )
)
SELECT 
    (abc.abc_class || xyz.xyz_class) AS matrix_segment,
    COUNT(DISTINCT abc.product_id) AS sku_count,
    SUM(i.stock_on_hand) AS total_stock_on_hand,
    ROUND(SUM(i.stock_on_hand * p.unit_cost), 2) AS total_inventory_value
FROM sku_abc abc
JOIN sku_xyz xyz ON abc.product_id = xyz.product_id
JOIN view_current_inventory i ON abc.product_id = i.product_id
JOIN products p ON abc.product_id = p.product_id
GROUP BY matrix_segment
ORDER BY total_inventory_value DESC;

-- Query 42: Supplier Risk Evaluation Score card
-- A composite metric: 60% based on supplier reliability, 40% based on ratings
SELECT 
    supplier_id,
    supplier_name,
    rating,
    reliability_score,
    ROUND((reliability_score * 60) + (rating * 8), 1) AS supplier_health_score,
    CASE 
        WHEN (reliability_score * 60) + (rating * 8) >= 85 THEN 'Preferred Partner'
        WHEN (reliability_score * 60) + (rating * 8) BETWEEN 70 AND 84 THEN 'Satisfactory'
        ELSE 'High Risk / Under Review'
    END AS supplier_risk_status
FROM suppliers
ORDER BY supplier_health_score DESC;

-- Query 43: Warehouse Cost vs Revenue Efficiency
-- Operational efficiency = Revenue generated by warehouse sales / monthly operational cost
SELECT 
    w.warehouse_id,
    w.warehouse_name,
    w.operational_cost_monthly * 12 AS annual_fixed_cost,
    ROUND(SUM(s.revenue), 2) AS annual_sales_revenue,
    ROUND(SUM(s.revenue) / (w.operational_cost_monthly * 12), 2) AS efficiency_ratio
FROM sales s
JOIN warehouses w ON s.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name
ORDER BY efficiency_ratio DESC;

-- Query 44: Supplier SKU dependencies (Identify single source bottlenecks)
SELECT 
    supplier_name,
    category,
    COUNT(product_id) AS total_skus_supplied,
    ROUND(AVG(unit_cost), 2) AS average_cost
FROM products p
JOIN suppliers s ON p.supplier_id = s.supplier_id
GROUP BY supplier_name, category
ORDER BY total_skus_supplied DESC;

-- Query 45: Stock Outages vs Supplier Reliability
-- Count of out of stock products per supplier and average lead time
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.reliability_score,
    COUNT(CASE WHEN i.stock_on_hand = 0 THEN 1 END) AS out_of_stock_skus,
    ROUND(AVG(p.lead_time_days), 1) AS avg_lead_time_days
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
JOIN view_current_inventory i ON p.product_id = i.product_id
GROUP BY s.supplier_id, s.supplier_name, s.reliability_score
ORDER BY out_of_stock_skus DESC, reliability_score ASC;
