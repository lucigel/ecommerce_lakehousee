"""
E-commerce Daily ELT Pipeline (Airflow 3.0)
Schedule: Daily at 2:00 AM
Flow: Extract → Validate Bronze → dbt Run → dbt Test
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'data-engineering',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ecom_daily_pipeline',
    default_args=default_args,
    description='Daily ELT: Postgres → MinIO → dbt → DuckDB',
    schedule='0 2 * * *',       # ← Airflow 3.0: dùng 'schedule' thay 'schedule_interval'
    start_date=datetime(2024, 1, 1),
    catchup=False,              # Airflow 3.0 mặc định False, nhưng ghi rõ cho dễ đọc
    tags=['ecommerce', 'elt', 'daily'],
) as dag:

    # Step 1: Extract Postgres → Parquet on MinIO
    extract = PythonOperator(
        task_id='extract_to_bronze',
        python_callable=lambda: __import__('scripts.extract', fromlist=['main']).main(),
    )

    # Step 2: Validate bronze data
    validate_bronze = PythonOperator(
        task_id='validate_bronze',
        python_callable=lambda: __import__('scripts.validate_bronze', fromlist=['main']).main(),
    )

    # Step 3: dbt run (staging → marts)
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/ecom_transform && dbt run --profiles-dir .',
    )

    # Step 4: dbt test
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/ecom_transform && dbt test --profiles-dir .',
    )

    # DAG dependency chain
    extract >> validate_bronze >> dbt_run >> dbt_test