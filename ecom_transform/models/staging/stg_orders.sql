SELECT
    order_id,
    customer_id,
    CAST(order_date AS TIMESTAMP) AS order_date,
    status,
    CAST(total_amount AS DECIMAL(12, 2)) AS total_amount,
    created_at
FROM read_parquet('s3://datalake/bronze/orders/**/*.parquet')
WHERE order_id IS NOT NULL