"""Synthetic churn history of the preferential segment (T-05.5, US-08, objective O2).

The real churn extract depended on the IT credential that blocked T-05.5 in
Sprint 2. This generator reproduces the agreed layout so the churn prototype
and the pilot can run from the repository. No record corresponds to a real
client. churn_3m is 1 if the client cancelled a credit product within the
three months after the observation date.
"""
import numpy as np

from finbank.schema import ID_COLUMN

Table = dict[str, np.ndarray]

CHURN_NUMERIC = (
    "months_as_client",
    "products_held",
    "digital_channel_share",
    "balance_trend_3m",
    "complaints_6m",
    "rate_gap_vs_market",
    "has_payroll_deposit",
    "age",
)
CHURN_CATEGORICAL = {"region": ("bogota", "andina", "caribe", "pacifica", "orinoquia")}
CHURN_TARGET = "churn_3m"


def generate_churn_sample(n_clients: int = 4000, seed: int = 2026, shift: float = 0.0) -> Table:
    """shift moves the population (more complaints, worse rate gap) to emulate a later cohort."""
    rng = np.random.default_rng(seed)
    n = n_clients
    months = rng.gamma(2.5, 26.0, n).round().clip(3, 480)
    products = rng.poisson(2.1, n).clip(1, 8).astype(float)
    digital = rng.beta(3, 2, n).round(3)
    trend = np.round(rng.normal(0.0, 0.18, n) - 0.04 * shift, 3)
    complaints = rng.poisson(0.35 + 0.25 * shift, n).astype(float)
    rate_gap = np.round(rng.normal(0.010 + 0.006 * shift, 0.02, n), 4)
    payroll = rng.binomial(1, 0.45, n).astype(float)
    age = rng.integers(25, 76, n).astype(float)
    region = rng.choice(np.array(CHURN_CATEGORICAL["region"], dtype=object), size=n,
                        p=[0.40, 0.26, 0.16, 0.12, 0.06])

    risk = (-2.6 - 0.006 * (months - 60) - 0.35 * (products - 2) - 3.2 * trend
            + 0.55 * complaints + 28.0 * rate_gap - 0.6 * payroll + 0.4 * (digital - 0.6))
    churn = (rng.random(n) < 1 / (1 + np.exp(-risk))).astype(float)

    return {
        ID_COLUMN: np.array([f"P{seed % 1000:03d}{i:06d}" for i in range(1, n + 1)], dtype=object),
        "months_as_client": months,
        "products_held": products,
        "digital_channel_share": digital,
        "balance_trend_3m": trend,
        "complaints_6m": complaints,
        "rate_gap_vs_market": rate_gap,
        "has_payroll_deposit": payroll,
        "age": age,
        "region": region,
        CHURN_TARGET: churn,
    }
