/*
View: vw_plan_performance
Grain: plan
Source: completed transactions only
*/
SET search_path TO analytics;

CREATE OR REPLACE VIEW vw_plan_performance AS
SELECT
  p.plan_id,
  p.plan_name,
  p.tier,
  COUNT(DISTINCT t.subscription_id) AS subscriptions,
  SUM(t.net_revenue) AS net_revenue,
  ROUND(AVG(t.net_revenue), 2) AS avg_revenue_per_tx
FROM fact_transactions t
JOIN dim_plans p ON t.plan_id = p.plan_id
WHERE t.transaction_status = 'completed'
GROUP BY 1,2,3
ORDER BY net_revenue DESC;
