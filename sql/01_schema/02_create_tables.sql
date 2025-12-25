/*
Purpose: Create dimension and fact tables for subscription analytics
*/

SET search_path TO analytics;

-- Dim Date
CREATE TABLE dim_date (
  date        DATE PRIMARY KEY,
  year        INT NOT NULL,
  month       INT NOT NULL,
  quarter     INT NOT NULL,
  month_name  TEXT NOT NULL
);

-- Dim Plans
CREATE TABLE dim_plans (
  plan_id               INT PRIMARY KEY,
  plan_name             TEXT NOT NULL,
  tier                  TEXT NOT NULL CHECK (tier IN ('basic','pro','premium')),
  price                 NUMERIC(12,2) NOT NULL CHECK (price > 0),
  cost_per_subscription NUMERIC(12,2) NOT NULL CHECK (cost_per_subscription >= 0),
  active_flag           BOOLEAN NOT NULL
);

-- Dim Customers
CREATE TABLE dim_customers (
  customer_id          INT PRIMARY KEY,
  signup_date          DATE NOT NULL,
  country              TEXT NOT NULL,
  acquisition_channel  TEXT NOT NULL CHECK (acquisition_channel IN ('organic','paid','referral','other'))
);

-- Dim Subscriptions
CREATE TABLE dim_subscriptions (
  subscription_id      INT PRIMARY KEY,
  customer_id          INT NOT NULL REFERENCES dim_customers(customer_id),
  plan_id              INT NOT NULL REFERENCES dim_plans(plan_id),
  start_date           DATE NOT NULL,
  end_date             DATE,
  status               TEXT NOT NULL CHECK (status IN ('active','canceled')),
  billing_cycle        TEXT NOT NULL CHECK (billing_cycle IN ('monthly','yearly')),
  cancellation_reason  TEXT CHECK (cancellation_reason IN ('price','competitor','features','other'))
);

-- Fact Transactions
CREATE TABLE fact_transactions (
  transaction_id        INT PRIMARY KEY,
  payment_date          DATE NOT NULL,
  customer_id           INT NOT NULL REFERENCES dim_customers(customer_id),
  subscription_id       INT NOT NULL REFERENCES dim_subscriptions(subscription_id),
  plan_id               INT NOT NULL REFERENCES dim_plans(plan_id),
  gross_amount          NUMERIC(12,2) NOT NULL,
  discount_amount       NUMERIC(12,2) NOT NULL,
  net_revenue           NUMERIC(12,2) NOT NULL,
  payment_method        TEXT NOT NULL CHECK (payment_method IN ('card','transfer','wallet')),
  transaction_status    TEXT NOT NULL CHECK (transaction_status IN ('completed','failed')),
  billing_period_start  DATE NOT NULL,
  billing_period_end    DATE NOT NULL
);

-- Fact Costs
CREATE TABLE fact_costs (
  cost_id           INT PRIMARY KEY,
  date              DATE NOT NULL,
  cost_type         TEXT NOT NULL CHECK (cost_type IN ('payment_fees','marketing','infra','support')),
  amount            NUMERIC(14,2) NOT NULL,
  fixed_or_variable TEXT NOT NULL CHECK (fixed_or_variable IN ('fixed','variable'))
);
