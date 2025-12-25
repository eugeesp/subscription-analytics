# ETL / Data Loading

## Overview
This project uses a simplified ETL approach.

The data used in the analysis was **generated programmatically using Python** and exported as CSV files, which are stored in the `data/raw/` directory.

The loading of these CSV files into PostgreSQL was performed **manually using pgAdmin's Import/Export tool**, rather than automated SQL or Python-based ETL scripts.

---

## Rationale

The goal of this project is to focus on:
- Data modeling
- Financial and subscription analytics
- SQL-based KPI computation
- Business insights and storytelling

Automating the ETL process was intentionally **out of scope** to keep the project focused and avoid unnecessary complexity.

However, this folder is kept to:
- Reflect a realistic analytics pipeline structure
- Document the data loading decision explicitly
- Allow easy extension in the future (e.g., automated ETL with Python or SQL)

---

## Data Sources

The following CSV files were loaded into PostgreSQL:

- `date_dim.csv`
- `plans.csv`
- `customers.csv`
- `subscriptions.csv`
- `transactions.csv`
- `costs.csv`

All files are located in:
data/raw/


---

## Notes

- Referential integrity is enforced at the database level via foreign keys.
- The data loading order followed table dependencies:
  1. Dimensions
  2. Fact tables
- All subsequent transformations and aggregations are handled directly in SQL (`03_kpis/` and `04_views/`).

---

## Future Improvements (Optional)

- Automate data loading using Python (`psycopg2` / `SQLAlchemy`)
- Add incremental loading logic
- Implement data quality checks as part of ETL
