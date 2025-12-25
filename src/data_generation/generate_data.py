from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd


# -----------------------------
# Config
# -----------------------------
@dataclass(frozen=True)
class Config:
    start_date: str = "2023-01-01"
    end_date: str = "2024-06-30"
    n_customers: int = 8000
    seed: int = 42
    out_dir: str = os.path.join("data", "raw")


PLAN_DEFS = [
    # plan_id, plan_name, tier, price, cost_per_subscription, active_flag
    (1, "Basic",   "basic",   10.0,  1.0, True),
    (2, "Pro",     "pro",     25.0,  2.5, True),
    (3, "Premium", "premium", 40.0,  4.0, True),
    (4, "Pro Year","pro",    250.0, 20.0, True),  # anual con descuento implícito
]

TIER_DIST = {
    "basic": 0.50,
    "pro": 0.35,
    "premium": 0.15
}

ACQUISITION_CHANNEL_DIST = {
    "organic": 0.40,
    "paid": 0.30,
    "referral": 0.20,
    "other": 0.10
}

COUNTRY_DIST = {
    "AR": 0.55,
    "MX": 0.25,
    "CL": 0.12,
    "UY": 0.08
}


def set_seeds(seed: int) -> None:
    np.random.seed(seed)
    random.seed(seed)


def ensure_out_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


# -----------------------------
# Generators
# -----------------------------
def generate_date_dim(cfg: Config) -> pd.DataFrame:
    start = pd.Timestamp(cfg.start_date)
    end = pd.Timestamp(cfg.end_date)

    dates = pd.date_range(start=start, end=end, freq="D")
    df = pd.DataFrame({"date": dates})
    df["year"] = df["date"].dt.year.astype(int)
    df["month"] = df["date"].dt.month.astype(int)
    df["quarter"] = df["date"].dt.quarter.astype(int)
    df["month_name"] = df["date"].dt.strftime("%b")

    # Validations
    assert df["date"].min() == start
    assert df["date"].max() == end
    assert df["date"].is_unique

    return df


def generate_plans() -> pd.DataFrame:
    df = pd.DataFrame(
        PLAN_DEFS,
        columns=["plan_id", "plan_name", "tier", "price", "cost_per_subscription", "active_flag"]
    )

    # Validations
    assert df["plan_id"].is_unique
    assert (df["price"] > 0).all()
    assert set(df["tier"]).issubset({"basic", "pro", "premium"})

    return df


def _seasonal_weights(dates: pd.DatetimeIndex) -> np.ndarray:
    """
    Leve estacionalidad: más signups en Q1 y Q4.
    Base = 1.0; Q1/Q4 = 1.25
    """
    quarters = dates.quarter.to_numpy()
    w = np.ones(len(dates), dtype=float)
    w[(quarters == 1) | (quarters == 4)] = 1.25
    w = w / w.sum()
    return w


def generate_customers(cfg: Config) -> pd.DataFrame:
    start = pd.Timestamp(cfg.start_date)
    end = pd.Timestamp(cfg.end_date)

    # IDs
    customer_ids = np.arange(1, cfg.n_customers + 1)

    # Signup dates with mild seasonality
    all_days = pd.date_range(start=start, end=end, freq="D")
    day_probs = _seasonal_weights(all_days)
    signup_dates = np.random.choice(all_days, size=cfg.n_customers, replace=True, p=day_probs)
    signup_dates = pd.to_datetime(signup_dates)

    # Channels
    channels = np.random.choice(
        list(ACQUISITION_CHANNEL_DIST.keys()),
        size=cfg.n_customers,
        p=list(ACQUISITION_CHANNEL_DIST.values())
    )

    # Countries
    countries = np.random.choice(
        list(COUNTRY_DIST.keys()),
        size=cfg.n_customers,
        p=list(COUNTRY_DIST.values())
    )

    df = pd.DataFrame({
        "customer_id": customer_ids,
        "signup_date": signup_dates,
        "country": countries,
        "acquisition_channel": channels
    }).sort_values("customer_id").reset_index(drop=True)

    # Validations (las que pediste + algunas extra)
    assert df["customer_id"].is_unique
    assert df["signup_date"].min() >= start
    assert df["signup_date"].max() <= end
    assert set(df["acquisition_channel"]).issubset(set(ACQUISITION_CHANNEL_DIST.keys()))
    assert set(df["country"]).issubset(set(COUNTRY_DIST.keys()))

    # Quick distribution sanity (tolerancias suaves)
    # Evita casos raros por azar; no hace falta exactitud perfecta.
    channel_share = df["acquisition_channel"].value_counts(normalize=True)
    assert channel_share.max() < 0.60, "Channel distribution looks too skewed; check probabilities."

    return df


CANCELLATION_REASON_DIST = {
    "price": 0.35,
    "competitor": 0.25,
    "features": 0.20,
    "other": 0.20
}

BILLING_CYCLE_DIST = {
    "monthly": 0.80,
    "yearly": 0.20
}

SUBSCRIPTIONS_PER_CUSTOMER_DIST = {
    1: 0.82,
    2: 0.18
    # si quisieras 3+: lo agregamos luego, pero no hace falta
}


def _sample_subscription_count(n_customers: int) -> np.ndarray:
    return np.random.choice(
        list(SUBSCRIPTIONS_PER_CUSTOMER_DIST.keys()),
        size=n_customers,
        p=list(SUBSCRIPTIONS_PER_CUSTOMER_DIST.values())
    )


def _sample_cancellation_reason(n: int) -> np.ndarray:
    return np.random.choice(
        list(CANCELLATION_REASON_DIST.keys()),
        size=n,
        p=list(CANCELLATION_REASON_DIST.values())
    )


def _sample_billing_cycle(n: int) -> np.ndarray:
    return np.random.choice(
        list(BILLING_CYCLE_DIST.keys()),
        size=n,
        p=list(BILLING_CYCLE_DIST.values())
    )


def _sample_churn_duration_months(n: int) -> np.ndarray:
    """
    Duración (en meses) para suscripciones canceladas:
    - 40%: 1–2 meses
    - 40%: 3–8 meses
    - 20%: 9–12 meses
    """
    buckets = np.random.choice([1, 2, 3], size=n, p=[0.40, 0.40, 0.20])
    out = np.empty(n, dtype=int)
    for i, b in enumerate(buckets):
        if b == 1:
            out[i] = np.random.randint(1, 3)      # 1-2
        elif b == 2:
            out[i] = np.random.randint(3, 9)      # 3-8
        else:
            out[i] = np.random.randint(9, 13)     # 9-12
    return out


def generate_subscriptions(cfg: Config, customers: pd.DataFrame, plans: pd.DataFrame) -> pd.DataFrame:
    start = pd.Timestamp(cfg.start_date)
    end = pd.Timestamp(cfg.end_date)

    customer_ids = customers["customer_id"].to_numpy()
    subs_counts = _sample_subscription_count(len(customer_ids))

    # Plan selection: tier mix (basic/pro/premium) y luego mapeo a plan_id
    # Nota: plan anual "Pro Year" lo dejamos como opción cuando billing_cycle = yearly.
    plan_map_monthly = {
        "basic": int(plans.loc[plans["plan_name"] == "Basic", "plan_id"].iloc[0]),
        "pro": int(plans.loc[plans["plan_name"] == "Pro", "plan_id"].iloc[0]),
        "premium": int(plans.loc[plans["plan_name"] == "Premium", "plan_id"].iloc[0]),
    }
    plan_id_pro_year = int(plans.loc[plans["plan_name"] == "Pro Year", "plan_id"].iloc[0])

    rows = []
    subscription_id = 1

    for cust_id, k in zip(customer_ids, subs_counts):
        # Para customers con 2 suscripciones, generamos períodos secuenciales no superpuestos
        prev_end = None
        for _ in range(int(k)):
            # start_date: si hay una suscripción previa cancelada, arranca después (gap 0-30 días)
            if prev_end is None:
                sub_start = pd.Timestamp(np.random.choice(pd.date_range(start, end, freq="D")))
            else:
                gap_days = np.random.randint(0, 31)
                sub_start = prev_end + pd.Timedelta(days=gap_days)
                if sub_start > end:
                    break  # no entra en el rango

            billing_cycle = _sample_billing_cycle(1)[0]

            if billing_cycle == "monthly":
                tier = np.random.choice(list(TIER_DIST.keys()), p=list(TIER_DIST.values()))
                plan_id = plan_map_monthly[tier]
            else:
                # anual: lo simplificamos a Pro Year (realista y manejable)
                plan_id = plan_id_pro_year

            # Status: churn target global ~35%
            status = np.random.choice(["active", "canceled"], p=[0.65, 0.35])

            if status == "canceled":
                dur_months = _sample_churn_duration_months(1)[0]
                sub_end = sub_start + pd.DateOffset(months=int(dur_months))
                # recortar al rango máximo
                if sub_end > end:
                    sub_end = end
                cancellation_reason = _sample_cancellation_reason(1)[0]
            else:
                sub_end = pd.NaT
                cancellation_reason = None

            # si la cancelación quedara antes del inicio por recortes raros, corregimos
            if status == "canceled" and sub_end <= sub_start:
                sub_end = sub_start + pd.DateOffset(months=1)

            rows.append({
                "subscription_id": subscription_id,
                "customer_id": int(cust_id),
                "plan_id": int(plan_id),
                "start_date": sub_start,
                "end_date": sub_end,
                "status": status,
                "billing_cycle": billing_cycle,
                "cancellation_reason": cancellation_reason
            })
            subscription_id += 1

            prev_end = sub_end if status == "canceled" else None
            if status == "active":
                # si está activa, no generamos otra suscripción posterior para este customer
                break

    df = pd.DataFrame(rows)

    # Validations
    assert df["subscription_id"].is_unique
    assert df["customer_id"].isin(customers["customer_id"]).all()
    assert df["plan_id"].isin(plans["plan_id"]).all()
    assert df["start_date"].min() >= start
    assert df["start_date"].max() <= end

    canceled = df[df["status"] == "canceled"]
    active = df[df["status"] == "active"]

    assert canceled["end_date"].notna().all()
    assert active["end_date"].isna().all()

    # cancellation_reason only for canceled
    assert canceled["cancellation_reason"].notna().all()
    assert active["cancellation_reason"].isna().all()

    # churn rate sanity (tolerancia por aleatoriedad)
    churn_rate = (df["status"] == "canceled").mean()
    assert 0.30 <= churn_rate <= 0.40, f"Churn rate out of bounds: {churn_rate:.3f}"

    return df.sort_values("subscription_id").reset_index(drop=True)


FAILED_RATE = 0.05

DISCOUNT_TXN_RATE = 0.15  # promedio; luego lo sesgamos por Q1/Q4
DISCOUNT_PCT_RANGE = (0.05, 0.25)  # 5% a 25%


def _month_start(d: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=d.year, month=d.month, day=1)


def _add_month(d: pd.Timestamp) -> pd.Timestamp:
    return (d + pd.offsets.MonthBegin(1)).normalize()


def _add_year(d: pd.Timestamp) -> pd.Timestamp:
    return (d + pd.DateOffset(years=1))


def _is_campaign_month(d: pd.Timestamp) -> bool:
    # campañas en Q1 (ene-mar) y Q4 (oct-dic)
    return d.month in (1, 2, 3, 10, 11, 12)


def generate_transactions(cfg: Config, subscriptions: pd.DataFrame, plans: pd.DataFrame) -> pd.DataFrame:
    start = pd.Timestamp(cfg.start_date)
    end = pd.Timestamp(cfg.end_date)

    # precio por plan_id
    plan_price = dict(zip(plans["plan_id"].astype(int), plans["price"].astype(float)))

    rows = []
    transaction_id = 1

    for _, sub in subscriptions.iterrows():
        sub_id = int(sub["subscription_id"])
        cust_id = int(sub["customer_id"])
        plan_id = int(sub["plan_id"])
        billing_cycle = sub["billing_cycle"]

        sub_start = pd.Timestamp(sub["start_date"])
        # si está cancelada, end_date; si activa, fin de rango
        if sub["status"] == "canceled":
            sub_end = pd.Timestamp(sub["end_date"])
        else:
            sub_end = end

        # seguridad
        if sub_start > end:
            continue

        price = float(plan_price[plan_id])

        if billing_cycle == "monthly":
            # generamos períodos mensuales
            period_start = _month_start(sub_start)
            # no antes de start
            if period_start < sub_start:
                period_start = _month_start(_add_month(sub_start))

            while period_start <= sub_end and period_start <= end:
                period_end = (_add_month(period_start) - pd.Timedelta(days=1)).normalize()

                # payment_date: usamos el inicio del período (simple y defendible)
                payment_date = period_start

                # status
                status = np.random.choice(["completed", "failed"], p=[1 - FAILED_RATE, FAILED_RATE])

                # descuento: más probable en meses de campaña (Q1/Q4)
                base_disc_prob = DISCOUNT_TXN_RATE
                disc_prob = base_disc_prob * (1.8 if _is_campaign_month(payment_date) else 0.7)
                disc_prob = min(max(disc_prob, 0.0), 0.6)

                if status == "completed" and (np.random.rand() < disc_prob):
                    disc_pct = np.random.uniform(*DISCOUNT_PCT_RANGE)
                    discount_amount = round(price * disc_pct, 2)
                else:
                    discount_amount = 0.0

                gross_amount = price
                net_revenue = round(gross_amount - discount_amount, 2) if status == "completed" else 0.0

                rows.append({
                    "transaction_id": transaction_id,
                    "payment_date": payment_date,
                    "customer_id": cust_id,
                    "subscription_id": sub_id,
                    "plan_id": plan_id,
                    "gross_amount": round(gross_amount, 2),
                    "discount_amount": round(discount_amount, 2),
                    "net_revenue": net_revenue,
                    "payment_method": np.random.choice(["card", "transfer", "wallet"], p=[0.78, 0.07, 0.15]),
                    "transaction_status": status,
                    "billing_period_start": period_start,
                    "billing_period_end": period_end
                })

                transaction_id += 1
                period_start = _add_month(period_start)

        else:  # yearly
            # 1 pago por año: pago al inicio (normalizado al día del start)
            payment_date = sub_start

            # primer período anual
            period_start = payment_date
            period_end = (_add_year(period_start) - pd.Timedelta(days=1)).normalize()

            def emit_year_payment(p_date: pd.Timestamp) -> None:
                nonlocal transaction_id
                status = np.random.choice(["completed", "failed"], p=[1 - FAILED_RATE, FAILED_RATE])

                # descuentos en anual: menos comunes, pero pueden existir
                base_disc_prob = 0.08
                disc_prob = base_disc_prob * (1.5 if _is_campaign_month(p_date) else 0.8)

                if status == "completed" and (np.random.rand() < disc_prob):
                    disc_pct = np.random.uniform(0.03, 0.15)
                    discount_amount = round(price * disc_pct, 2)
                else:
                    discount_amount = 0.0

                gross_amount = price
                net_revenue = round(gross_amount - discount_amount, 2) if status == "completed" else 0.0

                rows.append({
                    "transaction_id": transaction_id,
                    "payment_date": p_date,
                    "customer_id": cust_id,
                    "subscription_id": sub_id,
                    "plan_id": plan_id,
                    "gross_amount": round(gross_amount, 2),
                    "discount_amount": round(discount_amount, 2),
                    "net_revenue": net_revenue,
                    "payment_method": np.random.choice(["card", "transfer", "wallet"], p=[0.78, 0.07, 0.15]),
                    "transaction_status": status,
                    "billing_period_start": p_date,
                    "billing_period_end": (_add_year(p_date) - pd.Timedelta(days=1)).normalize()
                })
                transaction_id += 1

            # emit primer pago si entra en rango
            if start <= payment_date <= end:
                emit_year_payment(payment_date)

            # renovación: si sigue activa/cubierta más de 1 año y cae dentro del rango
            renewal_date = _add_year(payment_date)
            if renewal_date <= sub_end and renewal_date <= end:
                emit_year_payment(renewal_date)

    df = pd.DataFrame(rows)

    # Validations
    assert df["transaction_id"].is_unique
    assert df["customer_id"].notna().all()
    assert df["subscription_id"].isin(subscriptions["subscription_id"]).all()
    assert df["plan_id"].isin(plans["plan_id"]).all()

    assert df["payment_date"].min() >= start
    assert df["payment_date"].max() <= end

    # net_revenue rule
    failed = df[df["transaction_status"] == "failed"]
    assert (failed["net_revenue"] == 0).all()

    # sanity on failed rate
    fr = (df["transaction_status"] == "failed").mean()
    assert 0.03 <= fr <= 0.07, f"Failed rate out of bounds: {fr:.3f}"

    return df.sort_values("transaction_id").reset_index(drop=True)


def generate_costs(cfg: Config, transactions: pd.DataFrame) -> pd.DataFrame:
    start = pd.Timestamp(cfg.start_date)
    end = pd.Timestamp(cfg.end_date)

    tx_completed = transactions[transactions["transaction_status"] == "completed"].copy()
    tx_completed["month"] = tx_completed["payment_date"].dt.to_period("M").dt.to_timestamp()

    monthly_rev = (
        tx_completed.groupby("month", as_index=False)["net_revenue"]
        .sum()
        .rename(columns={"net_revenue": "monthly_net_revenue"})
        .sort_values("month")
    )

    # Generamos costos por mes
    rows = []
    cost_id = 1

    # Parámetros base (ajustables, pero razonables)
    base_infra = 12000.0     # fijo mensual
    base_support = 7000.0    # fijo mensual
    base_marketing = 9000.0  # variable con picos

    for _, r in monthly_rev.iterrows():
        month_date = pd.Timestamp(r["month"])
        rev = float(r["monthly_net_revenue"])

        # 1) payment_fees: 2-3% del revenue
        fee_rate = float(np.random.uniform(0.02, 0.03))
        payment_fees = round(rev * fee_rate, 2)

        # 2) marketing: picos en Q1/Q4 (campañas)
        is_campaign = month_date.month in (1, 2, 3, 10, 11, 12)
        # multiplicador de campaña: 1.3 a 2.2
        marketing_mult = float(np.random.uniform(1.3, 2.2)) if is_campaign else float(np.random.uniform(0.6, 1.1))
        marketing = round(base_marketing * marketing_mult, 2)

        # 3) infra: estable con ruido leve
        infra = round(base_infra * float(np.random.uniform(0.95, 1.05)), 2)

        # 4) support: estable con ruido + leve relación con revenue (opcional)
        support = round(base_support * float(np.random.uniform(0.95, 1.08)) + (rev * 0.002), 2)

        # Emit rows
        for cost_type, amount, fov in [
            ("payment_fees", payment_fees, "variable"),
            ("marketing", marketing, "variable"),
            ("infra", infra, "fixed"),
            ("support", support, "fixed"),
        ]:
            rows.append({
                "cost_id": cost_id,
                "date": month_date,  # primer día del mes
                "cost_type": cost_type,
                "amount": float(amount),
                "fixed_or_variable": fov
            })
            cost_id += 1

    df = pd.DataFrame(rows)

    # Validations
    assert df["cost_id"].is_unique
    assert df["date"].min() >= pd.Timestamp(cfg.start_date).to_period("M").to_timestamp()
    assert df["date"].max() <= pd.Timestamp(cfg.end_date).to_period("M").to_timestamp()

    # Payment fee sanity: ratio 2-3% en promedio (tolerancia)
    pf = df[df["cost_type"] == "payment_fees"].copy()
    pf = pf.merge(monthly_rev, left_on="date", right_on="month", how="left")
    pf_ratio = (pf["amount"] / pf["monthly_net_revenue"]).mean()
    assert 0.019 <= pf_ratio <= 0.031, f"Payment fee ratio out of bounds: {pf_ratio:.4f}"

    return df.sort_values("cost_id").reset_index(drop=True)



# -----------------------------
# IO
# -----------------------------
def write_csv(df: pd.DataFrame, out_path: str) -> None:
    df.to_csv(out_path, index=False)


def main() -> None:
    cfg = Config()
    set_seeds(cfg.seed)
    ensure_out_dir(cfg.out_dir)

    date_dim = generate_date_dim(cfg)
    plans = generate_plans()
    customers = generate_customers(cfg)
    subscriptions = generate_subscriptions(cfg, customers=customers, plans=plans)
    transactions = generate_transactions(cfg, subscriptions=subscriptions, plans=plans)
    costs = generate_costs(cfg, transactions=transactions)



    write_csv(date_dim, os.path.join(cfg.out_dir, "date_dim.csv"))
    write_csv(plans, os.path.join(cfg.out_dir, "plans.csv"))
    write_csv(customers, os.path.join(cfg.out_dir, "customers.csv"))
    write_csv(subscriptions, os.path.join(cfg.out_dir, "subscriptions.csv"))
    write_csv(transactions, os.path.join(cfg.out_dir, "transactions.csv"))
    write_csv(costs, os.path.join(cfg.out_dir, "costs.csv"))

    print("Generated:")
    print(f"- {len(date_dim):,} rows: date_dim.csv")
    print(f"- {len(plans):,} rows: plans.csv")
    print(f"- {len(customers):,} rows: customers.csv")
    print(f"- {len(subscriptions):,} rows: subscriptions.csv")
    print(f"- {len(transactions):,} rows: transactions.csv")
    print(f"- {len(costs):,} rows: costs.csv")


if __name__ == "__main__":
    main()
