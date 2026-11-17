-- E-Commerce Business Intelligence: SQLite analysis queries
-- Table name: orders (created by main.py)

-- 1. Monthly recognized revenue and profit
SELECT strftime('%Y-%m', order_date) AS year_month,
       ROUND(SUM(recognized_revenue),2) AS revenue,
       ROUND(SUM(recognized_profit),2) AS profit,
       COUNT(*) AS delivered_orders
FROM orders WHERE order_status='Delivered'
GROUP BY year_month ORDER BY year_month;

-- 2. Category revenue and profit margin
SELECT category, ROUND(SUM(recognized_revenue),2) AS revenue,
       ROUND(SUM(recognized_profit),2) AS profit,
       ROUND(100.0*SUM(recognized_profit)/NULLIF(SUM(recognized_revenue),0),2) AS margin_pct
FROM orders WHERE order_status='Delivered'
GROUP BY category ORDER BY revenue DESC;

-- 3. Regional performance
SELECT region, COUNT(*) AS delivered_orders,
       ROUND(SUM(recognized_revenue),2) AS revenue
FROM orders WHERE order_status='Delivered'
GROUP BY region ORDER BY revenue DESC;

-- 4. Top 10 customers by recognized revenue
SELECT customer_id, COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(recognized_revenue),2) AS revenue
FROM orders WHERE order_status='Delivered'
GROUP BY customer_id ORDER BY revenue DESC LIMIT 10;

-- 5. Return and cancellation rates
SELECT category, COUNT(*) AS total_orders,
       SUM(CASE WHEN order_status='Returned' THEN 1 ELSE 0 END) AS returned,
       SUM(CASE WHEN order_status='Cancelled' THEN 1 ELSE 0 END) AS cancelled,
       ROUND(100.0*SUM(CASE WHEN order_status='Returned' THEN 1 ELSE 0 END)/COUNT(*),2) AS return_rate_pct
FROM orders GROUP BY category ORDER BY return_rate_pct DESC;

-- 6. Payment method mix for delivered orders
SELECT payment_method, COUNT(*) AS orders,
       ROUND(SUM(recognized_revenue),2) AS revenue
FROM orders WHERE order_status='Delivered'
GROUP BY payment_method ORDER BY orders DESC;

-- 7. Discount band performance
SELECT CASE WHEN discount_pct=0 THEN 'No discount'
            WHEN discount_pct<=0.10 THEN '1-10%'
            WHEN discount_pct<=0.15 THEN '11-15%'
            ELSE 'Above 15%' END AS discount_band,
       COUNT(*) AS delivered_orders,
       ROUND(SUM(recognized_revenue),2) AS revenue,
       ROUND(SUM(recognized_profit),2) AS profit
FROM orders WHERE order_status='Delivered'
GROUP BY discount_band ORDER BY delivered_orders DESC;

-- 8. Month-over-month revenue growth
WITH monthly AS (
  SELECT strftime('%Y-%m',order_date) AS ym,SUM(recognized_revenue) AS revenue
  FROM orders WHERE order_status='Delivered' GROUP BY ym
)
SELECT ym,ROUND(revenue,2) AS revenue,
       ROUND(LAG(revenue) OVER(ORDER BY ym),2) AS previous_month,
       ROUND(100.0*(revenue-LAG(revenue) OVER(ORDER BY ym))/
       NULLIF(LAG(revenue) OVER(ORDER BY ym),0),2) AS mom_growth_pct
FROM monthly ORDER BY ym;

-- 9. Rank categories within each region
WITH regional AS (
 SELECT region,category,SUM(recognized_revenue) AS revenue
 FROM orders WHERE order_status='Delivered' GROUP BY region,category
)
SELECT region,category,ROUND(revenue,2) AS revenue,
       DENSE_RANK() OVER(PARTITION BY region ORDER BY revenue DESC) AS category_rank
FROM regional ORDER BY region,category_rank;

-- 10. RFM-style customer metrics
SELECT customer_id,
       CAST(julianday((SELECT MAX(order_date) FROM orders WHERE order_status='Delivered')) -
       julianday(MAX(order_date)) AS INTEGER) AS recency_days,
       COUNT(DISTINCT order_id) AS frequency,
       ROUND(SUM(recognized_revenue),2) AS monetary
FROM orders WHERE order_status='Delivered'
GROUP BY customer_id ORDER BY monetary DESC;
