/*
KPI: Monthly Gross Margin
Business question: What is our profitability after costs?
Definition: (net_revenue - total_costs) / net_revenue
Filters: transaction_status = 'completed'
Assumptions: Revenue and costs matched by month
Output grain: One row per month
*/
SET search_path TO analytics;

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
  GROUP BY date
)
SELECT
  r.month,
  r.net_revenue,
  c.total_costs,
  (r.net_revenue - c.total_costs) AS gross_margin,
  ROUND(
    (r.net_revenue - c.total_costs) / NULLIF(r.net_revenue, 0),
    4
  ) AS margin_pct
FROM revenue r
JOIN costs c USING (month)
ORDER BY r.month;