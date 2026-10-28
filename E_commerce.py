import sqlite3
import numpy as np

# Connect to database
conn = sqlite3.connect("ecommerce.db")
cur = conn.cursor()

# Create tables
cur.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER,
    order_date TEXT
)
""")

# Insert sample products
products = [
    (1, "Laptop", 50000),
    (2, "Mobile", 20000),
    (3, "Headphones", 2000),
    (4, "Keyboard", 1500),
    (5, "Mouse", 800)
]

cur.executemany(
    "INSERT OR IGNORE INTO products VALUES (?, ?, ?)",
    products
)

# Insert sample orders
orders = [
    (101, 1, 2, "2026-01-10"),
    (102, 2, 3, "2026-01-15"),
    (103, 3, 5, "2026-02-05"),
    (104, 4, 4, "2026-02-12"),
    (105, 5, 10, "2026-03-08"),
    (106, 1, 1, "2026-03-15"),
    (107, 2, 2, "2026-03-20"),
    (108, 3, 3, "2026-04-02")
]

cur.executemany(
    "INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?)",
    orders
)

conn.commit()

while True:
    print("\n===== E-COMMERCE SALES ANALYZER =====")
    print("1. View Products")
    print("2. Total Revenue")
    print("3. Product Sales Report")
    print("4. Best-Selling Product")
    print("5. Monthly Sales")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        cur.execute("SELECT * FROM products")
        for product in cur.fetchall():
            print(product)

    elif choice == "2":
        cur.execute("""
            SELECT SUM(p.price * o.quantity)
            FROM products p
            JOIN orders o ON p.id = o.product_id
        """)
        revenue = cur.fetchone()[0] or 0
        print("Total Revenue: Rs.", revenue)

    elif choice == "3":
        cur.execute("""
            SELECT p.name, SUM(o.quantity),
                   SUM(p.price * o.quantity)
            FROM products p
            JOIN orders o ON p.id = o.product_id
            GROUP BY p.id
            ORDER BY SUM(o.quantity) DESC
        """)

        data = cur.fetchall()

        print("\nProduct | Units Sold | Revenue")
        for row in data:
            print(row[0], "|", row[1], "| Rs.", row[2])

        if data:
            quantities = np.array([row[1] for row in data])
            print("Total Units Sold:", np.sum(quantities))
            print("Average Units Sold:", np.mean(quantities))

    elif choice == "4":
        cur.execute("""
            SELECT p.name, SUM(o.quantity) AS total
            FROM products p
            JOIN orders o ON p.id = o.product_id
            GROUP BY p.id
            ORDER BY total DESC
            LIMIT 1
        """)
        print("Best-Selling Product:", cur.fetchone())

    elif choice == "5":
        cur.execute("""
            SELECT SUBSTR(o.order_date, 1, 7),
                   SUM(p.price * o.quantity)
            FROM orders o
            JOIN products p ON p.id = o.product_id
            GROUP BY SUBSTR(o.order_date, 1, 7)
            ORDER BY SUBSTR(o.order_date, 1, 7)
        """)

        monthly_data = cur.fetchall()
        for month, sales in monthly_data:
            print(month, "| Revenue: Rs.", sales)

        if monthly_data:
            amounts = np.array([row[1] for row in monthly_data])
            print("Average Monthly Revenue: Rs.",
                  round(np.mean(amounts), 2))

    elif choice == "6":
        break

    else:
        print("Invalid choice! Try again.")

conn.close()
print("Program closed.")