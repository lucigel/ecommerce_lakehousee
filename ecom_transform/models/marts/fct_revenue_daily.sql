-- Fact: Daily revenue by category and city
SELECT
    DATE_TRUNC('day', o.order_date) AS order_day,
    c.city,
    p.category,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.line_total) AS total_revenue,
    AVG(oi.line_total) AS avg_item_value,
    SUM(oi.quantity) AS total_items_sold
FROM {{ ref('stg_orders') }} o
JOIN {{ ref('stg_order_items') }} oi ON o.order_id = oi.order_id
JOIN {{ ref('stg_products') }} p ON oi.product_id = p.product_id
JOIN {{ ref('stg_customers') }} c ON o.customer_id = c.customer_id
WHERE o.status = 'completed'
GROUP BY 1, 2, 3