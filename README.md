# Subscription Analytics Dashboard

This project analyzes the performance of a subscription-based business, focusing on revenue growth, recurring revenue (MRR), churn behavior, and cost efficiency.

The goal is to provide a clear, decision-oriented analytics framework that supports strategic planning and operational optimization.

## Business Context

The analysis is based on a simulated subscription business offering multiple pricing plans with monthly and annual billing cycles.

The dashboard is designed to answer key business questions such as:
- Is revenue growth sustainable and predictable?
- How stable is recurring revenue (MRR)?
- What are the main drivers of customer churn?
- Are costs scaling efficiently as the business grows?

## Data Model

The project follows a star-schema-like structure with:

- Dimension tables:
  - dim_date
  - dim_customers
  - dim_plans
  - dim_subscriptions

- Fact tables:
  - fact_transactions (subscription payments)
  - fact_costs (operational and variable costs)

From these tables, analytical views were created to calculate KPIs such as revenue, MRR, churn rate, and margins.


## Key Metrics & KPIs

The dashboard tracks the following core metrics:

- Net Revenue
- Monthly Recurring Revenue (MRR)
- Revenue Growth (MoM / YoY)
- Churn Rate
- Churn Reasons
- Total Costs
- Gross Margin (%)
- Payment Fees Ratio


## Dashboard Structure

The Power BI dashboard is structured into six pages:

1. Executive Overview – High-level business health indicators
2. Revenue & Growth – Revenue trends and growth rates
3. Recurring Revenue (MRR) – Predictability and stability of subscriptions
4. Churn Analysis – Customer retention and churn drivers
5. Costs & Margin – Cost structure and profitability
6. Business Insights & Recommendations – Strategic conclusions and actions

## Key Insights

- Revenue and MRR show sustained and predictable growth.
- Gross margin improved steadily, reaching ~76%, driven by scalable revenue and controlled costs.
- Churn stabilized historically around 3–5%, with price being the main cancellation driver.
- Payment fees remained efficient (~2–3%), indicating healthy transaction cost management.

## Tools & Technologies

- PostgreSQL – Data storage and analytical views
- SQL – Data modeling and KPI calculation
- Power BI – Data visualization and dashboarding
- Python – Data generation and simulation


## How to Use

1. Load the dataset into PostgreSQL.
2. Execute the SQL scripts to create analytical views.
3. Connect Power BI to the database.
4. Refresh the dataset and explore the dashboard.
