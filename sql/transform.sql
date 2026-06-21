-- ============================================================================
-- ELT TRANSFORM — all cleaning + KPIs done INSIDE the database with SQL.
-- Input : raw_sales (everything stored as text, uncleaned)
-- Output: clean_sales  + four KPI tables
-- This mirrors what transform.py did in the ETL pipeline, but in SQL instead.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. CLEAN: cast text -> proper types, derive revenue/unit_price, drop bad rows
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS clean_sales;
CREATE TABLE clean_sales AS
SELECT
    row_id::int                                   AS row_id,
    order_id,
    TO_DATE(order_date, 'MM/DD/YYYY')             AS order_date,
    TO_DATE(ship_date,  'MM/DD/YYYY')             AS ship_date,
    ship_mode,
    customer_id,
    customer_name,
    segment,
    country,
    city,
    state,
    postal_code,
    region,
    product_id,
    category,
    sub_category,
    product_name,
    sales::numeric                                AS sales,
    quantity::int                                 AS quantity,
    discount::numeric                             AS discount,
    profit::numeric                               AS profit,
    ROUND(sales::numeric, 2)                      AS revenue,
    ROUND(sales::numeric / NULLIF(quantity::int, 0), 2) AS unit_price
FROM raw_sales
WHERE row_id     IS NOT NULL   -- the same "drop nulls in key cols" rule,
  AND order_id   IS NOT NULL   -- but expressed as a SQL WHERE clause
  AND order_date IS NOT NULL
  AND sales      IS NOT NULL
  AND quantity   IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 2. KPI: revenue by product category
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS kpi_revenue_by_category;
CREATE TABLE kpi_revenue_by_category AS
SELECT
    category,
    ROUND(SUM(revenue), 2) AS total_revenue,
    SUM(quantity)          AS total_units,
    COUNT(*)               AS line_items
FROM clean_sales
GROUP BY category
ORDER BY total_revenue DESC;

-- ---------------------------------------------------------------------------
-- 3. KPI: monthly revenue trend
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS kpi_monthly_revenue;
CREATE TABLE kpi_monthly_revenue AS
SELECT
    DATE_TRUNC('month', order_date)::date AS month,
    ROUND(SUM(revenue), 2)                AS total_revenue,
    COUNT(DISTINCT order_id)              AS orders
FROM clean_sales
GROUP BY 1
ORDER BY 1;

-- ---------------------------------------------------------------------------
-- 4. KPI: revenue + profit by region
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS kpi_revenue_by_region;
CREATE TABLE kpi_revenue_by_region AS
SELECT
    region,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2)  AS total_profit
FROM clean_sales
GROUP BY region
ORDER BY total_revenue DESC;

-- ---------------------------------------------------------------------------
-- 5. KPI: top 20 customers by revenue
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS kpi_top_customers;
CREATE TABLE kpi_top_customers AS
SELECT
    customer_id,
    customer_name,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM clean_sales
GROUP BY customer_id, customer_name
ORDER BY total_revenue DESC
LIMIT 20;
