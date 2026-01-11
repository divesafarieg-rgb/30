SELECT 
    c.full_name
FROM customer c
LEFT JOIN "order" o ON c.customer_id = o.customer_id
WHERE o.order_no IS NULL;