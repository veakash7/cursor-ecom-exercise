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
