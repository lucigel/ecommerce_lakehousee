SELECT 
    customer_id, 
    name AS customer_name, 
    email,  
    city,  
    created_at 
FROM read_parquet('s3://datalake/bronze/customers/**/*.parquet')
WHERE customer_id IS NOT NULL 
