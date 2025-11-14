# E-commerce Data Exercise

This workspace contains a complete, reproducible pipeline for generating synthetic e-commerce datasets, ingesting them into SQLite, and running an aggregated analytics query.

## Contents

- `python generate_data.py` – synthetic data generator for five CSVs (products, customers, orders, order_items, reviews) using `random` (seeded at 42) with optional `faker` fallback.
- `ingest_ecom.py` – end-to-end ingestion and reporting script that:
  1. Drops/recreates SQLite tables in `ecom.db`.
  2. Loads all CSV rows via bulk inserts.
  3. Writes the analytics join query to `queries.sql`.
  4. Executes the query and prints the first 20 rows in a formatted table.
- `queries.sql` – saved SQL join that combines orders, customers, products, order_items, and reviews to surface key per-order insights.
- Generated data assets: `products.csv`, `customers.csv`, `orders.csv`, `order_items.csv`, `reviews.csv`, plus the hydrated `ecom.db`.

## How to Reproduce

1. **Install dependencies**
   ```bash
   pip install faker
   ```
   (The generator works without Faker but uses deterministic placeholder values.)

2. **Generate CSV data**
   ```bash
   python "python generate_data.py"
   ```
   This script regenerates all five CSV files with 50/200/500 order scaffolding and prints a completion notice.

3. **Ingest data & run analytics**
   ```bash
   python ingest_ecom.py
   ```
   Results:
   - Creates/refreshes `ecom.db`.
   - Populates every table from the CSVs.
   - Outputs `SQLite ingestion complete.` followed by a 20-row preview with columns:
     `order_id`, `order_date`, `customer_name`, `total_amount`, `total_items`, `top_product`, `top_product_quantity`, `avg_product_rating`.

4. **Review saved query**
   ```bash
   type queries.sql
   ```
   The SQL uses CTEs and window functions to derive total items, top product per order, and average product ratings.

## Notes

- Randomness is seeded (`random.seed(42)`) for reproducibility.
- `ingest_ecom.py` is idempotent: it drops tables before reinserting.
- All files are committed (including CSVs and SQLite DB) to keep the dataset self-contained.
- To push to GitHub, authenticate `gh` (`gh auth login ...`), then run:
  ```bash
  gh repo create cursor-ecom-exercise --private --source=. --remote=origin
  git push -u origin main
  ```

