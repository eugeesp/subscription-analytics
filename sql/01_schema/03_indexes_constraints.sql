/*
Purpose: Performance indexes for analytics queries
*/

SET search_path TO analytics;

CREATE INDEX ix_transactions_payment_date ON fact_transactions(payment_date);
CREATE INDEX ix_transactions_plan_id ON fact_transactions(plan_id);
CREATE INDEX ix_subscriptions_customer ON dim_subscriptions(customer_id);
CREATE INDEX ix_costs_date ON fact_costs(date);
