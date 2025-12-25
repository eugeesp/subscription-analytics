/*
KPI: Churn Reasons Distribution
Business question: Why are customers canceling?
Definition: Distribution of cancellation reasons
Filters: status = 'canceled'
Assumptions: Cancellation reason is recorded at time of cancellation
Output grain: One row per cancellation reason
*/
SET search_path TO analytics;

SELECT
  cancellation_reason,
  COUNT(*) AS cancellations,
  ROUND(
    COUNT(*)::numeric / SUM(COUNT(*)) OVER (),
    3
  ) AS share
FROM dim_subscriptions
WHERE status = 'canceled'
GROUP BY cancellation_reason
ORDER BY cancellations DESC;