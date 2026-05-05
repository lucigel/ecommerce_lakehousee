-- Dimension: Customer lifetime summary
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    COUNT(DISTINCT o.order_id) AS lifetime_orders,
    SUM(o.total_amount) AS lifetime_revenue,
    MIN(o.order_date) AS first_order_date,
    MAX(o.order_date) AS last_order_date,
    DATEDIFF('day', MIN(o.order_date), MAX(o.order_date)) AS customer_tenure_days
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ ref('stg_orders') }} o ON c.customer_id = o.customer_id
    AND o.status = 'completed'
GROUP BY 1, 2, 3