/*
View: vw_payment_fees_ratio
Definition: payment_fees / net_revenue
Grain: month
*/

SET search_path TO analytics;

CREATE OR REPLACE VIEW vw_payment_fees_ratio AS
WITH fees AS (
  SELECT
    month,
    SUM(amount) AS payment_fees
  FROM vw_monthly_costs_by_type
  WHERE cost_type = 'payment_fees'
  GROUP BY 1
),
rev AS (
  SELECT
    month,
    net_revenue
  FROM vw_monthly_revenue
)
SELECT
  r.month,
  ROUND(COALESCE(f.payment_fees, 0)::numeric, 2) AS payment_fees,
  ROUND(r.net_revenue::numeric, 2) AS net_revenue,
  ROUND(COALESCE(f.payment_fees, 0)::numeric / NULLIF(r.net_revenue, 0), 4) AS fee_ratio
FROM rev r
LEFT JOIN fees f USING (month)
ORDER BY r.month;

