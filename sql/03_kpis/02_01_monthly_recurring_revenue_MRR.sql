/*
KPI: Monthly Recurring Revenue (MRR)
Business question: What is our normalized monthly revenue?
Definition: Sum of all active subscription revenues, normalized monthly
Filters: transaction_status = 'completed'
Assumptions: 
  1. Only completed transactions
  2. Revenue prorated across billing period months
  3. Handles annual/quarterly subscriptions
Output grain: One row per month
*/
SET search_path TO analytics;

WITH periods AS (
  SELECT
    billing_period_start,
    billing_period_end,
    net_revenue
  FROM fact_transactions
  WHERE transaction_status = 'completed'
),
expanded AS (
  SELECT
    gs::date AS month,
    net_revenue /
      (DATE_PART('month', AGE(billing_period_end + INTERVAL '1 day', billing_period_start)))
      AS mrr_amount
  FROM periods
  CROSS JOIN LATERAL
    GENERATE_SERIES(
      DATE_TRUNC('month', billing_period_start),
      DATE_TRUNC('month', billing_period_end),
      INTERVAL '1 month'
    ) gs
)
SELECT
  month,
  ROUND(SUM(mrr_amount), 2) AS mrr
FROM expanded
GROUP BY month
ORDER BY month;