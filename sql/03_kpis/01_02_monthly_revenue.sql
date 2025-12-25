/*
KPI: Monthly Revenue
Business question: What is our revenue trend over time?
Definition: Net revenue aggregated by month
Filters: transaction_status = 'completed'
Assumptions: Payment date determines revenue recognition
Output grain: One row per month
*/
SET search_path TO analytics;

SELECT
  DATE_TRUNC('month', payment_date)::date AS month,
  SUM(net_revenue) AS monthly_net_revenue
FROM fact_transactions
WHERE transaction_status = 'completed'
GROUP BY 1
ORDER BY 1;