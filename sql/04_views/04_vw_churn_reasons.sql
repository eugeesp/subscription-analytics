/*
View: vw_churn_reasons
Grain: reason (overall)
*/
SET search_path TO analytics;

CREATE OR REPLACE VIEW vw_churn_reasons AS
SELECT
  cancellation_reason,
  COUNT(*) AS cancellations,
  ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER (), 3) AS share
FROM dim_subscriptions
WHERE status = 'canceled'
GROUP BY cancellation_reason
ORDER BY cancellations DESC;
