-- ============================================================================
-- KPIs for the dashboard (Phase 6)
-- Run these against the `sales` table. In Metabase, paste each one into a new
-- SQL question, then pick the matching chart type and add it to a dashboard.
-- ============================================================================

-- 1. HEADLINE NUMBERS  ->  show as "Number" cards (total revenue, units, orders)
SELECT
    ROUND(SUM(revenue)::numeric, 2) AS total_revenue,
    SUM(quantity)                   AS total_units,
    COUNT(DISTINCT order_id)        AS total_orders,
    ROUND(SUM(profit)::numeric, 2)  AS total_profit
FROM sales;

-- 2. TOP 10 PRODUCTS BY REVENUE  ->  show as a horizontal Bar chart
SELECT
    product_name,
    ROUND(SUM(revenue)::numeric, 2) AS revenue
FROM sales
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 10;

-- 3a. SALES BY CATEGORY  ->  show as a Pie or Bar chart
SELECT
    category,
    ROUND(SUM(revenue)::numeric, 2) AS revenue
FROM sales
GROUP BY category
ORDER BY revenue DESC;

-- 3b. SALES BY REGION  ->  show as a Bar chart (or Map on `state`)
SELECT
    region,
    ROUND(SUM(revenue)::numeric, 2) AS revenue
FROM sales
GROUP BY region
ORDER BY revenue DESC;

-- 4. MONTHLY REVENUE TREND  ->  show as a Line chart (x = month, y = revenue)
SELECT
    DATE_TRUNC('month', order_date) AS month,
    ROUND(SUM(revenue)::numeric, 2) AS revenue
FROM sales
GROUP BY 1
ORDER BY 1;
