/*
View: vw_revenue_growth
Grain: month
Metrics: MoM% and YoY% revenue growth
*/
SET search_path TO analytics;

CREATE OR REPLACE VIEW vw_revenue_growth AS
WITH monthly_revenue AS (
  SELECT
    DATE_TRUNC('month', payment_date)::date AS month,
    SUM(net_revenue) AS revenue
  FROM fact_transactions
  WHERE transaction_status = 'completed'
  GROUP BY 1
)
SELECT
  month,
  revenue,
  LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
  ROUND(
    (revenue - LAG(revenue) OVER (ORDER BY month)) /
    NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100,
    2
  ) AS growth_mom_pct,
  ROUND(
    (revenue - LAG(revenue, 12) OVER (ORDER BY month)) /
    NULLIF(LAG(revenue, 12) OVER (ORDER BY month), 0) * 100,
    2
  ) AS growth_yoy_pct
FROM monthly_revenue
ORDER BY month;
