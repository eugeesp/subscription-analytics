/*
KPI: Total Revenue (Gross vs Net)
Business question: What is our total revenue and discount impact?
Definition: Sum of all completed transactions
Filters: transaction_status = 'completed'
Assumptions: Only completed transactions generate real revenue
Output grain: Single row aggregate
*/
SET search_path TO analytics;

SELECT
  SUM(gross_amount)    AS gross_revenue,
  SUM(discount_amount) AS total_discounts,
  SUM(net_revenue)     AS net_revenue
FROM fact_transactions
WHERE transaction_status = 'completed';