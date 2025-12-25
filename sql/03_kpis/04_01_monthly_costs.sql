/*
KPI: Monthly Costs
Business question: What are our total monthly operational costs?
Definition: Sum of all costs by month
Filters: None
Assumptions: Cost date represents when cost was incurred
Output grain: One row per month
*/
SET search_path TO analytics;

SELECT
  date AS month,
  SUM(amount) AS total_costs
FROM fact_costs
GROUP BY date
ORDER BY date;