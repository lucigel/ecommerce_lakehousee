"""
E-commerce Data Generator
Tạo data realistic cho 4 bảng: customers, products, orders, order_items
"""
import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2

fake = Faker('vi_VN')  # Vietnamese locale for realistic names/cities

# --- Config ---
NUM_CUSTOMERS = 500
NUM_PRODUCTS = 100
NUM_ORDERS = 50_000      # 50K orders across 3 months
ITEMS_PER_ORDER = (1, 5)  # Each order has 1-5 items
START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 3, 31)
RESET_BEFORE_GENERATE = True

# Vietnamese cities with weighted probability (realistic distribution)
CITIES = {
    'Hồ Chí Minh': 0.35,
    'Hà Nội': 0.30,
    'Đà Nẵng': 0.10,
    'Cần Thơ': 0.05,
    'Hải Phòng': 0.05,
    'Nha Trang': 0.05,
    'Huế': 0.04,
    'Biên Hòa': 0.03,
    'Vũng Tàu': 0.03,
}

CATEGORIES = {
    'Điện thoại': (2_000_000, 30_000_000),
    'Laptop': (8_000_000, 50_000_000),
    'Phụ kiện': (50_000, 2_000_000),
    'Quần áo': (100_000, 3_000_000),
    'Sách': (30_000, 500_000),
    'Đồ gia dụng': (200_000, 5_000_000),
    'Thực phẩm': (20_000, 1_000_000),
}

ORDER_STATUSES = ['completed', 'completed', 'completed', 'completed',
                  'pending', 'cancelled', 'returned']  # 57% completed

def connect_db():
    return psycopg2.connect(
        host='localhost', port=5432,
        dbname='ecommerce', user='cinammon', password='cinammonpass'
    )

def clear_existing_data(conn):
    """Clear existing generated data to avoid duplicates on rerun."""
    cur = conn.cursor()
    cur.execute(
        "TRUNCATE TABLE order_items, orders, products, customers "
        "RESTART IDENTITY CASCADE"
    )
    conn.commit()
    print("🧹 Cleared existing data in target tables")

def generate_customers(conn):
    """Generate realistic Vietnamese customers"""
    cur = conn.cursor()
    cities = list(CITIES.keys())
    weights = list(CITIES.values())

    for _ in range(NUM_CUSTOMERS):
        name = fake.name()
        email = fake.unique.email()
        city = random.choices(cities, weights=weights, k=1)[0]
        cur.execute(
            "INSERT INTO customers (name, email, city) VALUES (%s, %s, %s)",
            (name, email, city)
        )
    conn.commit()
    print(f"✅ Generated {NUM_CUSTOMERS} customers")

def generate_products(conn):
    """Generate products across categories with realistic pricing"""
    cur = conn.cursor()
    categories = list(CATEGORIES.items())
    for _ in range(NUM_PRODUCTS):
        category, (min_price, max_price) = random.choice(categories)
        name = f"{category} - {fake.word().capitalize()} {fake.word().capitalize()}"
        price = round(random.uniform(min_price, max_price), -3)  # Round to nearest 1000
        cur.execute(
            "INSERT INTO products (product_name, category, price) VALUES (%s, %s, %s)",
            (name, category, price / 1_000_000)  # Store in millions for easier reading
        )
    conn.commit()
    print(f"✅ Generated {NUM_PRODUCTS} products")

def generate_orders(conn):
    """Generate orders with realistic time distribution"""
    cur = conn.cursor()
    delta = (END_DATE - START_DATE).days
    cur.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT product_id, price FROM products")
    products = cur.fetchall()

    if not customer_ids:
        raise ValueError("No customers found. Generate customers before orders.")
    if not products:
        raise ValueError("No products found. Generate products before orders.")

    product_ids = [row[0] for row in products]
    product_price = {row[0]: float(row[1]) for row in products}

    for _ in range(NUM_ORDERS):
        customer_id = random.choice(customer_ids)
        order_date = START_DATE + timedelta(
            days=random.randint(0, delta),
            hours=random.randint(7, 23),  # Orders mostly during daytime
            minutes=random.randint(0, 59)
        )
        status = random.choice(ORDER_STATUSES)

        # Generate order items
        num_items = random.randint(*ITEMS_PER_ORDER)
        selected_product_ids = random.sample(product_ids, min(num_items, len(product_ids)))

        total_amount = 0
        items = []
        for product_id in selected_product_ids:
            price = product_price[product_id]
            quantity = random.choices([1, 1, 1, 2, 2, 3], k=1)[0]  # Mostly buy 1-2
            line_total = price * quantity
            total_amount += line_total
            items.append((product_id, quantity, price, line_total))

        # Insert order
        cur.execute(
            "INSERT INTO orders (customer_id, order_date, status, total_amount) "
            "VALUES (%s, %s, %s, %s) RETURNING order_id",
            (customer_id, order_date, status, total_amount)
        )
        order_id = cur.fetchone()[0]

        # Insert order items
        for product_id, quantity, unit_price, line_total in items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total) "
                "VALUES (%s, %s, %s, %s, %s)",
                (order_id, product_id, quantity, unit_price, line_total)
            )

        if _ % 5000 == 0:
            conn.commit()
            print(f"  ... generated {_}/{NUM_ORDERS} orders")

    conn.commit()
    print(f"✅ Generated {NUM_ORDERS} orders with items")

if __name__ == "__main__":
    conn = connect_db()
    if RESET_BEFORE_GENERATE:
        clear_existing_data(conn)
    generate_customers(conn)
    generate_products(conn)
    generate_orders(conn)
    conn.close()
    print("\n🎉 Data generation complete!")
