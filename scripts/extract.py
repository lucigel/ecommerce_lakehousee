"""
Extract data from PostgreSQL → Parquet on MinIO
Pattern: Full extract per table, partitioned by extract date
"""
import os
from datetime import datetime
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
import psycopg2
from io import BytesIO

# --- Config ---
PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'ecommerce', 
    'user': 'cinammon', 
    'password': 'cinammonpass'
}

S3_CONFIG = {
    'endpoint_url': 'http://localhost:9000',
    'aws_access_key_id': 'cinammon',
    'aws_secret_access_key': 'cinammonpass',
}

BUCKET = 'datalake'
TABLES = ['customers', 'products', 'orders', 'order_items']

def get_s3_client():
    return boto3.client('s3', **S3_CONFIG)

def extract_table(table_name: str, extract_date: str):
    """
    Extract toàn bộ table từ Postgres → Parquet trên MinIO
    Path pattern: bronze/{table_name}/extract_date={date}/{table_name}.parquet
    """
    # Read from Postgres
    conn = psycopg2.connect(**PG_CONFIG)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()

    print(f"  📊 {table_name}: {len(df)} rows, {len(df.columns)} columns")

    # Convert to Parquet in memory
    table = pa.Table.from_pandas(df)
    buffer = BytesIO()
    pq.write_table(table, buffer, compression='snappy')
    buffer.seek(0)

    # Upload to MinIO
    s3_key = f"bronze/{table_name}/extract_date={extract_date}/{table_name}.parquet"
    s3 = get_s3_client()
    s3.put_object(Bucket=BUCKET, Key=s3_key, Body=buffer.getvalue())

    print(f"  ✅ Uploaded to s3://{BUCKET}/{s3_key}")
    return len(df)

def main():
    extract_date = datetime.now().strftime('%Y-%m-%d')
    print(f"🚀 Starting extract — date: {extract_date}\n")

    total_rows = 0
    for table in TABLES:
        rows = extract_table(table, extract_date)
        total_rows += rows

    print(f"\n🎉 Extract complete! Total: {total_rows} rows across {len(TABLES)} tables")

if __name__ == "__main__":
    main()