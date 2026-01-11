SELECT DISTINCT
    c1.full_name AS customer1,
    c2.full_name AS customer2
FROM customer c1
JOIN customer c2 ON c1.customer_id < c2.customer_id
WHERE c1.city = c2.city 
    AND c1.manager_id = c2.manager_id
    AND c1.manager_id IS NOT NULL;