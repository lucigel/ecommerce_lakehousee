SELECT
    product_id,
    product_name,
    category,
    CAST(price AS DECIMAL(10, 2)) AS unit_price,
    created_at
FROM read_parquet('s3://datalake/bronze/products/**/*.parquet')
WHERE product_id IS NOT NULL AND price > 0