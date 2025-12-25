/*
KPI: Revenue Growth (MoM / YoY)
Business question: How fast are we growing?
Definition:
  - MoM% = (rev_t - rev_t-1) / rev_t-1
  - YoY% = (rev_t - rev_t-12) / rev_t-12
Revenue basis: net_revenue from completed transactions
Filters: transaction_status = 'completed'
Assumptions: Month-over-month and year-over-year comparison
Output grain: One row per month
*/
SET search_path TO analytics;

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