/*
View: vw_churn_rate
Definition: cancellations_in_month / active_subscriptions_at_month_start
Grain: month
Notes:
  - Adds is_complete_month flag based on last available month in the dataset
*/

SET search_path TO analytics;

CREATE OR REPLACE VIEW vw_churn_rate AS
WITH months AS (
  SELECT DISTINCT DATE_TRUNC('month', date)::date AS month
  FROM dim_date
),
active_at_start AS (
  SELECT
    m.month,
    COUNT(*) AS active_at_start
  FROM months m
  JOIN dim_subscriptions s
    ON s.start_date <= m.month
   AND (s.end_date IS NULL OR s.end_date >= m.month)
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
),
base AS (
  SELECT
    a.month,
    COALESCE(c.cancellations, 0) AS cancellations,
    a.active_at_start,
    ROUND(COALESCE(c.cancellations, 0)::numeric / NULLIF(a.active_at_start, 0), 4) AS churn_rate
  FROM active_at_start a
  LEFT JOIN cancellations c USING (month)
),
max_month AS (
  SELECT MAX(month) AS max_month
  FROM base
)
SELECT
  b.month,
  b.cancellations,
  b.active_at_start,
  b.churn_rate,
  CASE
    WHEN b.month < m.max_month THEN TRUE
    ELSE FALSE
  END AS is_complete_month
FROM base b
CROSS JOIN max_month m
ORDER BY b.month;
