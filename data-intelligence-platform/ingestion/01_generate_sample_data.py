"""
Generate realistic sample data in PostgreSQL
"""
import logging
from datetime import datetime, timedelta
import random
import psycopg2
from psycopg2.extras import execute_values

from config.connection import ConnectionConfig, log_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_sample_data():
    """Generate and insert sample data"""
    try:
        log_config()

        conn = psycopg2.connect(
            dbname=ConnectionConfig.PG_DATABASE,
            user=ConnectionConfig.PG_USER,
            password=ConnectionConfig.PG_PASSWORD,
            host=ConnectionConfig.PG_HOST,
            port=ConnectionConfig.PG_PORT
        )
        cursor = conn.cursor()

        logger.info("Starting sample data generation...")

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM customer_dim")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info(f"Data already exists ({count} customers). Skipping generation.")
            cursor.close()
            conn.close()
            return

        # Generate customers
        logger.info("Generating customers...")
        customers = []
        for i in range(10000):
            customers.append((
                f"Customer_{i}",
                f"customer_{i}@example.com",
                f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                random.choice(["USA", "Canada", "UK", "Australia"]),
                (datetime.now() - timedelta(days=random.randint(1, 1000))).date(),
                random.choice([True, True, True, False])  # Most active
            ))

        cursor.executemany(
            "INSERT INTO customer_dim (customer_name, email, phone, city, country, signup_date, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            customers
        )
        logger.info(f"✓ Inserted {len(customers)} customers")

        # Generate products
        logger.info("Generating products...")
        categories = ["Electronics", "Clothing", "Home & Garden", "Books", "Sports"]
        products = []
        for i in range(5000):
            category = random.choice(categories)
            price = round(random.uniform(10, 500), 2)
            products.append((
                f"Product_{i}",
                category,
                random.choice(["Subcategory_A", "Subcategory_B", "Subcategory_C"]),
                price,
                round(price * random.uniform(0.3, 0.7), 2)
            ))

        cursor.executemany(
            "INSERT INTO product_dim (product_name, category, subcategory, price, cost) VALUES (%s, %s, %s, %s, %s)",
            products
        )
        logger.info(f"✓ Inserted {len(products)} products")

        # Get customer and product IDs
        cursor.execute("SELECT customer_id FROM customer_dim LIMIT 10000")
        customer_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT product_id FROM product_dim LIMIT 5000")
        product_ids = [row[0] for row in cursor.fetchall()]

        # Generate sales
        logger.info("Generating sales (this may take a moment)...")
        sales = []
        for i in range(500000):
            qty = random.randint(1, 10)
            unit_price = round(random.uniform(10, 500), 2)
            discount = round(random.uniform(0, unit_price * 0.2), 2)
            tax = round((unit_price - discount) * qty * 0.1, 2)

            sales.append((
                random.choice(customer_ids),
                random.choice(product_ids),
                (datetime.now() - timedelta(days=random.randint(1, 365))).date(),
                qty,
                unit_price,
                (unit_price - discount) * qty,
                discount,
                tax
            ))

            if (i + 1) % 50000 == 0:
                logger.info(f"  Generated {i + 1} sales records...")

        cursor.executemany(
            "INSERT INTO sales_fact (customer_id, product_id, sales_date, quantity, unit_price, total_amount, discount_amount, tax_amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            sales
        )
        logger.info(f"✓ Inserted {len(sales)} sales")

        # Generate orders
        logger.info("Generating orders...")
        orders = []
        for i in range(100000):
            order_date = (datetime.now() - timedelta(days=random.randint(1, 365))).date()
            delivery_date = order_date + timedelta(days=random.randint(1, 14)) if random.random() > 0.1 else None

            orders.append((
                random.choice(customer_ids),
                order_date,
                delivery_date,
                random.choice(["Completed", "Pending", "Shipped", "Cancelled"]),
                round(random.uniform(50, 5000), 2)
            ))

        cursor.executemany(
            "INSERT INTO order_fact (customer_id, order_date, delivery_date, order_status, total_order_value) VALUES (%s, %s, %s, %s, %s)",
            orders
        )
        logger.info(f"✓ Inserted {len(orders)} orders")

        # Generate inventory
        logger.info("Generating inventory...")
        warehouses = ["Warehouse_A", "Warehouse_B", "Warehouse_C", "Warehouse_D"]
        inventory = []
        for _ in range(50000):
            inventory.append((
                random.choice(product_ids),
                random.choice(warehouses),
                random.randint(0, 1000),
                random.randint(0, 500),
                random.randint(10, 100),
                (datetime.now() - timedelta(days=random.randint(0, 7))).date()
            ))

        cursor.executemany(
            "INSERT INTO inventory_fact (product_id, warehouse_location, quantity_on_hand, quantity_reserved, reorder_level, measurement_date) VALUES (%s, %s, %s, %s, %s, %s)",
            inventory
        )
        logger.info(f"✓ Inserted {len(inventory)} inventory records")

        # Commit transaction
        conn.commit()
        logger.info("✅ All sample data generated successfully!")

        # Print summary
        logger.info("\n📊 Data Summary:")
        cursor.execute("SELECT COUNT(*) FROM customer_dim")
        logger.info(f"  Customers: {cursor.fetchone()[0]:,}")
        cursor.execute("SELECT COUNT(*) FROM product_dim")
        logger.info(f"  Products: {cursor.fetchone()[0]:,}")
        cursor.execute("SELECT COUNT(*) FROM sales_fact")
        logger.info(f"  Sales: {cursor.fetchone()[0]:,}")
        cursor.execute("SELECT COUNT(*) FROM order_fact")
        logger.info(f"  Orders: {cursor.fetchone()[0]:,}")
        cursor.execute("SELECT COUNT(*) FROM inventory_fact")
        logger.info(f"  Inventory Records: {cursor.fetchone()[0]:,}")

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}")
        raise


if __name__ == "__main__":
    generate_sample_data()
