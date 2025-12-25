/*
View: vw_monthly_costs
Grain: month, cost_type
*/
SET search_path TO analytics;

CREATE OR REPLACE VIEW vw_monthly_costs AS
SELECT
  date AS month,
  cost_type,
  SUM(amount) AS amount
FROM fact_costs
GROUP BY 1, 2
ORDER BY 1, 2;
