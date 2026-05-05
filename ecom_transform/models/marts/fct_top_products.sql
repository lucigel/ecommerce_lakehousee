-- Top products by revenue
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.unit_price,
    COUNT(DISTINCT oi.order_id) AS times_ordered,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.line_total) AS total_revenue,
    RANK() OVER (PARTITION BY p.category ORDER BY SUM(oi.line_total) DESC) AS rank_in_category
FROM {{ ref('stg_products') }} p
JOIN {{ ref('stg_order_items') }} oi ON p.product_id = oi.product_id
JOIN {{ ref('stg_orders') }} o ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY 1, 2, 3, 4