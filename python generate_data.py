# generate_data.py
import csv, random, datetime
try:
    from faker import Faker  # type: ignore
except:
    Faker = None

random.seed(42)
if Faker:
    faker = Faker()
else:
    faker = None

def rnd_date(start_days_ago=730):
    base = datetime.datetime.now()
    delta = datetime.timedelta(days=random.randint(0, start_days_ago))
    return (base - delta).strftime("%Y-%m-%d")

# Products
products = []
categories = ["Electronics","Home","Clothing","Toys","Beauty"]
for i in range(1,51):
    p = {
        "product_id": i,
        "name": (faker.word().title() if faker else f"Product{i}"),
        "category": random.choice(categories),
        "price": round(random.uniform(5,500),2)
    }
    products.append(p)

# Customers
customers = []
for i in range(1,201):
    customers.append({
        "customer_id": i,
        "first_name": faker.first_name() if faker else f"First{i}",
        "last_name": faker.last_name() if faker else f"Last{i}",
        "email": (faker.email() if faker else f"user{i}@example.com"),
        "signup_date": rnd_date(730)
    })

# Orders and order_items
orders = []
order_items = []
oi_id = 1
for oid in range(1,501):
    cust = random.choice(customers)
    order_date = rnd_date(730)
    n_items = random.randint(1,4)
    total = 0
    for _ in range(n_items):
        prod = random.choice(products)
        qty = random.randint(1,3)
        total += prod["price"] * qty
        order_items.append({
            "order_item_id": oi_id,
            "order_id": oid,
            "product_id": prod["product_id"],
            "quantity": qty,
            "unit_price": prod["price"]
        })
        oi_id += 1
    orders.append({
        "order_id": oid,
        "customer_id": cust["customer_id"],
        "order_date": order_date,
        "total_amount": round(total,2)
    })

# Reviews
reviews = []
r_id = 1
for _ in range(250):
    prod = random.choice(products)
    cust = random.choice(customers)
    reviews.append({
        "review_id": r_id,
        "product_id": prod["product_id"],
        "customer_id": cust["customer_id"],
        "rating": random.randint(1,5),
        "review_text": (faker.sentence() if faker else "Good product"),
        "review_date": rnd_date(730)
    })
    r_id += 1

# write csv helper
def write_csv(filename, rows, headers):
    with open(filename, "w", newline='', encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)

write_csv("products.csv", products, ["product_id","name","category","price"])
write_csv("customers.csv", customers, ["customer_id","first_name","last_name","email","signup_date"])
write_csv("orders.csv", orders, ["order_id","customer_id","order_date","total_amount"])
write_csv("order_items.csv", order_items, ["order_item_id","order_id","product_id","quantity","unit_price"])
write_csv("reviews.csv", reviews, ["review_id","product_id","customer_id","rating","review_text","review_date"])

print("CSV files generated: products.csv, customers.csv, orders.csv, order_items.csv, reviews.csv")
