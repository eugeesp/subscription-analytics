/*
KPI: Plan Performance
Business question: Which subscription plans generate the most revenue?
Definition: Revenue and subscription count by plan
Filters: transaction_status = 'completed'
Assumptions: Plan performance measured by net revenue
Output grain: One row per plan
*/
SET search_path TO analytics;

SELECT
  p.plan_name,
  COUNT(DISTINCT t.subscription_id) AS subscriptions,
  SUM(t.net_revenue) AS net_revenue,
  ROUND(AVG(t.net_revenue), 2) AS avg_revenue_per_tx
FROM fact_transactions t
JOIN dim_plans p ON t.plan_id = p.plan_id
WHERE t.transaction_status = 'completed'
GROUP BY p.plan_name
ORDER BY net_revenue DESC;