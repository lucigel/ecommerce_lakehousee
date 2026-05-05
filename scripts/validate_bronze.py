# scripts/validate_bronze.py
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# Compatible với Great Expectations >= 1.0 (Fluent API)
# Dùng file-based context để Data Docs được lưu ra đĩa → mở được trên browser
import great_expectations as gx
import pandas as pd

# ── 1. Đọc Bronze data từ MinIO ──────────────────────────────────────────────
# Dùng directory path, PyArrow tự scan Hive partitions: extract_date=.../orders.parquet
orders = pd.read_parquet(
    "s3://datalake/bronze/orders/",
    storage_options={
        "key": "cinammon",
        "secret": "cinammonpass",
        "client_kwargs": {"endpoint_url": "http://localhost:9000"},
    },
)
print(f"[OK] Loaded {len(orders):,} rows from bronze/orders/")

# ── 2. GX Context (file-based → lưu Data Docs ra thư mục gx/) ───────────────
# Tạo thư mục gx/ trong project root, Data Docs sẽ ở:
# gx/uncommitted/data_docs/local_site/index.html
context = gx.get_context(mode="file")

# ── 3. Data Source → Asset → Batch Definition (GX v1.x Fluent API) ───────────
# Dùng add_or_update để tránh lỗi khi chạy lại script nhiều lần
data_source = context.data_sources.add_or_update_pandas("pandas_datasource")
data_asset  = data_source.add_dataframe_asset("orders_asset")
batch_def   = data_asset.add_batch_definition_whole_dataframe("orders_batch")

# ── 4. Expectation Suite ──────────────────────────────────────────────────────
suite = gx.ExpectationSuite(name="bronze_orders_suite")

# Schema checks — đảm bảo các cột bắt buộc tồn tại
suite.add_expectation(gx.expectations.ExpectColumnToExist(column="order_id"))
suite.add_expectation(gx.expectations.ExpectColumnToExist(column="customer_id"))
suite.add_expectation(gx.expectations.ExpectColumnToExist(column="total_amount"))

# Volume check — phát hiện extract thiếu data
suite.add_expectation(
    gx.expectations.ExpectTableRowCountToBeBetween(min_value=1000, max_value=500_000)
)

# Value checks — data quality
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="order_id"))
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="total_amount", min_value=0, max_value=10_000_000
    )
)

# Lưu suite vào context (add_or_update để chạy lại không bị lỗi duplicate)
suite = context.suites.add_or_update(suite)

# ── 5. Validation Definition + Run ───────────────────────────────────────────
validation_def = gx.ValidationDefinition(
    name="bronze_orders_validation",
    data=batch_def,
    suite=suite,
)
validation_def = context.validation_definitions.add_or_update(validation_def)

result = validation_def.run(batch_parameters={"dataframe": orders})

# ── 6. Kết quả ───────────────────────────────────────────────────────────────
if not result.success:
    print("[FAIL] Bronze validation FAILED!")
else:
    print("[PASS] Bronze validation passed")

# ── 7. Build Data Docs và mở browser ─────────────────────────────────────────
context.build_data_docs()
print("\n[INFO] Mo Data Docs tai:")
print("   gx/uncommitted/data_docs/local_site/index.html")
context.open_data_docs()   # tự động mở browser