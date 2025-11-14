import csv
import sqlite3
from pathlib import Path
from typing import Iterable, List

DB_NAME = "ecom.db"
QUERY_FILE = Path("queries.sql")

TABLE_SPECS = {
    "products": """
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """,
    "customers": """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            signup_date TEXT NOT NULL
        )
    """,
    "orders": """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            total_amount REAL NOT NULL
        )
    """,
    "order_items": """
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL
        )
    """,
    "reviews": """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            review_text TEXT NOT NULL,
            review_date TEXT NOT NULL
        )
    """,
}

JOIN_QUERY = """
WITH order_totals AS (
    SELECT order_id, SUM(quantity) AS total_items
    FROM order_items
    GROUP BY order_id
),
top_items AS (
    SELECT
        oi.order_id,
        p.name AS top_product,
        oi.quantity AS top_product_quantity,
        ROW_NUMBER() OVER (
            PARTITION BY oi.order_id
            ORDER BY oi.quantity DESC, p.name ASC
        ) AS rn
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
),
order_ratings AS (
    SELECT
        oi.order_id,
        AVG(r.rating) AS avg_product_rating
    FROM order_items oi
    LEFT JOIN reviews r ON r.product_id = oi.product_id
    GROUP BY oi.order_id
)
SELECT
    o.order_id,
    o.order_date,
    c.first_name || ' ' || c.last_name AS customer_name,
    o.total_amount,
    ot.total_items,
    ti.top_product,
    ti.top_product_quantity,
    ROUND(orate.avg_product_rating, 2) AS avg_product_rating
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
LEFT JOIN order_totals ot ON ot.order_id = o.order_id
LEFT JOIN (
    SELECT order_id, top_product, top_product_quantity
    FROM top_items
    WHERE rn = 1
) ti ON ti.order_id = o.order_id
LEFT JOIN order_ratings orate ON orate.order_id = o.order_id
ORDER BY o.order_id;
""".strip()


def ensure_tables(cur):
    for ddl in TABLE_SPECS.values():
        cur.execute(ddl)


def load_csv_rows(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def insert_data(cur, table, rows):
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ",".join(["?"] * len(columns))
    sql = f'INSERT OR REPLACE INTO {table} ({",".join(columns)}) VALUES ({placeholders})'
    values = [[row[col] for col in columns] for row in rows]
    cur.executemany(sql, values)


def write_query_file():
    QUERY_FILE.write_text(JOIN_QUERY + "\n", encoding="utf-8")


def format_table(headers: List[str], rows: Iterable[Iterable]) -> str:
    str_rows = [[("" if value is None else str(value)) for value in row] for row in rows]
    widths = [
        max(len(header), *(len(row[idx]) for row in str_rows)) if str_rows else len(header)
        for idx, header in enumerate(headers)
    ]
    header_line = " | ".join(header.ljust(widths[idx]) for idx, header in enumerate(headers))
    separator = "-+-".join("-" * width for width in widths)
    data_lines = [
        " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(headers)))
        for row in str_rows
    ]
    return "\n".join([header_line, separator, *data_lines])


def main():
    base_path = Path(".")
    csv_files = {
        "products": base_path / "products.csv",
        "customers": base_path / "customers.csv",
        "orders": base_path / "orders.csv",
        "order_items": base_path / "order_items.csv",
        "reviews": base_path / "reviews.csv",
    }

    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        for table in TABLE_SPECS.keys():
            cur.execute(f"DROP TABLE IF EXISTS {table}")
        ensure_tables(cur)

        for table, csv_path in csv_files.items():
            rows = load_csv_rows(csv_path)
            insert_data(cur, table, rows)

        conn.commit()
    finally:
        conn.close()

    print("SQLite ingestion complete.")

    write_query_file()

    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute(JOIN_QUERY)
        rows = cur.fetchmany(20)
        headers = [desc[0] for desc in cur.description]
    finally:
        conn.close()

    table_output = format_table(headers, rows)
    print(table_output)


if __name__ == "__main__":
    main()

