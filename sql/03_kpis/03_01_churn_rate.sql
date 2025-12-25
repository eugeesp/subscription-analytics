/*
KPI: Monthly Churn Rate
Business question: What percentage of our customer base are we losing each month?
Definition: cancellations_in_month / active_subscriptions_at_month_start
Filters: Only canceled subscriptions with end_date
Assumptions:
  - Active at month start = subscriptions with start_date <= month_start
    and (end_date is null or end_date >= month_start)
  - Restricted to dataset range using the max month present in dim_date
Output grain: One row per month
*/
SET search_path TO analytics;

WITH bounds AS (
  SELECT MAX(date) AS max_date
  FROM dim_date
),
months AS (
  SELECT DISTINCT DATE_TRUNC('month', date)::date AS month_start
  FROM dim_date
),
active_at_start AS (
  SELECT
    m.month_start AS month,
    COUNT(*) AS active_at_start
  FROM months m
  JOIN dim_subscriptions s
    ON s.start_date <= m.month_start
   AND (s.end_date IS NULL OR s.end_date >= m.month_start)
  GROUP BY 1
),
cancellations AS (
  SELECT
    DATE_TRUNC('month', end_date)::date AS month,
    COUNT(*) AS cancellations
  FROM dim_subscriptions
  WHERE status = 'canceled'
    AND end_date IS NOT NULL
  GROUP BY 1
)
SELECT
  a.month,
  COALESCE(c.cancellations, 0) AS cancellations,
  a.active_at_start,
  ROUND(COALESCE(c.cancellations, 0)::numeric / NULLIF(a.active_at_start, 0), 4) AS churn_rate
FROM active_at_start a
LEFT JOIN cancellations c USING (month)
ORDER BY a.month;