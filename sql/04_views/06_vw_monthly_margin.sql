/*
View: vw_monthly_margin
Grain: month
Definition: net_revenue - total_costs
*/
SET search_path TO analytics;

CREATE OR REPLACE VIEW vw_monthly_margin AS
WITH revenue AS (
  SELECT
    DATE_TRUNC('month', payment_date)::date AS month,
    SUM(net_revenue) AS net_revenue
  FROM fact_transactions
  WHERE transaction_status = 'completed'
  GROUP BY 1
),
costs AS (
  SELECT
    date AS month,
    SUM(amount) AS total_costs
  FROM fact_costs
  GROUP BY 1
)
SELECT
  r.month,
  r.net_revenue,
  c.total_costs,
  (r.net_revenue - c.total_costs) AS gross_margin,
  ROUND((r.net_revenue - c.total_costs) / NULLIF(r.net_revenue, 0), 4) AS margin_pct
FROM revenue r
JOIN costs c USING (month)
ORDER BY r.month;
