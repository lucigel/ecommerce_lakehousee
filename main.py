import duckdb 

conn = duckdb.connect()
conn.sql("""
    SET s3_endpoint='localhost:9000';
    SET s3_access_key_id='cinammon';
    SET s3_secret_access_key='cinammonpass';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")

# Query Parquet trực tiếp từ MinIO — không cần import!
conn.sql("""
    SELECT COUNT(*) as total_orders 
    FROM 's3://datalake/bronze/orders/**/*.parquet'
""").show()

conn.sql("""
    SELECT * 
    FROM 's3://datalake/bronze/orders/**/*.parquet'
    LIMIT 5
""").show()