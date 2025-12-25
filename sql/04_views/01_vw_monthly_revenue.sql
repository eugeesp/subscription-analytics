/*
View: vw_monthly_revenue
Grain: month
Source: completed transactions only
*/
SET search_path TO analytics;

CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
  DATE_TRUNC('month', payment_date)::date AS month,
  SUM(net_revenue) AS net_revenue
FROM fact_transactions
WHERE transaction_status = 'completed'
GROUP BY 1
ORDER BY 1;
