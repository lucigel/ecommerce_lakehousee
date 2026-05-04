SELECT
    item_id,
    order_id,
    product_id,
    quantity,
    CAST(unit_price AS DECIMAL(10, 2)) AS unit_price,
    CAST(line_total AS DECIMAL(12, 2)) AS line_total
FROM read_parquet('s3://datalake/bronze/order_items/**/*.parquet')
WHERE item_id IS NOT NULL AND quantity > 0