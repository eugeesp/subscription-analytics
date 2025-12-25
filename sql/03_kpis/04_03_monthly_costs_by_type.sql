/*
View: vw_monthly_costs_by_type
Definition: monthly costs by cost_type
Grain: month, cost_type
Source: fact_costs
*/

SET search_path TO analytics;

CREATE OR REPLACE VIEW vw_monthly_costs_by_type AS
SELECT
  DATE_TRUNC('month', date)::date AS month,
  cost_type,
  ROUND(SUM(amount)::numeric, 2) AS amount
FROM fact_costs
GROUP BY 1, 2
ORDER BY 1, 2;
