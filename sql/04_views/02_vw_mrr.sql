CREATE OR REPLACE VIEW vw_mrr AS
WITH bounds AS (
  SELECT DATE_TRUNC('month', MAX(payment_date))::date AS max_month
  FROM fact_transactions
  WHERE transaction_status = 'completed'
),
expanded AS (
  SELECT
    t.transaction_id,
    gs::date AS month,
    t.net_revenue
  FROM fact_transactions t
  CROSS JOIN bounds b
  CROSS JOIN LATERAL
    GENERATE_SERIES(
      DATE_TRUNC('month', t.billing_period_start),
      LEAST(DATE_TRUNC('month', t.billing_period_end), b.max_month),
      INTERVAL '1 month'
    ) gs
  WHERE t.transaction_status = 'completed'
),
months_per_tx AS (
  SELECT
    transaction_id,
    COUNT(*) AS months_in_period
  FROM expanded
  GROUP BY transaction_id
)
SELECT
  e.month,
  ROUND(SUM(e.net_revenue / NULLIF(m.months_in_period, 0))::numeric, 2) AS mrr
FROM expanded e
JOIN months_per_tx m USING (transaction_id)
GROUP BY e.month
ORDER BY e.month;
