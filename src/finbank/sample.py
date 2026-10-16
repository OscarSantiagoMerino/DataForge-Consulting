"""Anonymized synthetic sample of the FinBank credit portfolio.

Response to risk R1: profiling and validation must not wait for the warehouse
credential, so the team works on a sample with the agreed layout. No record
corresponds to a real client. A table is a dict of column name -> numpy array;
missing values are NaN in numeric columns and None in categorical ones.
"""
import numpy as np

from finbank.schema import DPD_COLUMN, ID_COLUMN, SCHEMA

Table = dict[str, np.ndarray]

# Share of missing values injected per variable. The four declared-by-client
# fields mirror what FinBank reported during the diagnostic conversations.
MISSING_RATE = {
    "monthly_income": 0.03,
    "employment_months": 0.06,
    "bureau_score": 0.04,
    "credit_utilization": 0.08,
    "savings_balance": 0.05,
    "digital_channel_share": 0.45,
    "education_level": 0.35,
    "dependents": 0.28,
    "housing_type": 0.40,
}
IMMATURE_SHARE = 0.06  # accounts too recent to have a 60 day observation


def generate_sample(n_clients: int = 5000, seed: int = 2026) -> Table:
    rng = np.random.default_rng(seed)
    n = n_clients
    variables = {v.name: v for v in SCHEMA}

    def pick(name, p=None):
        return rng.choice(np.array(variables[name].categories, dtype=object), size=n, p=p)

    monthly_income = np.round(rng.lognormal(mean=14.9, sigma=0.55, size=n), -3)
    loan_amount = np.round(monthly_income * rng.uniform(1, 12, n), -4)
    loan_term = rng.choice([12, 24, 36, 48, 60, 72], size=n)
    interest_rate = np.round(rng.uniform(0.12, 0.38, n), 4)
    installment = loan_amount * (1 + interest_rate * loan_term / 12) / loan_term
    bureau_score = np.clip(rng.normal(680, 95, n), 150, 950).round()
    prior_delinquencies = rng.poisson(0.4, n)
    utilization = rng.beta(2, 3, n).round(3)

    table: Table = {
        ID_COLUMN: np.array([f"C{i:06d}" for i in range(1, n + 1)], dtype=object),
        "age": rng.integers(18, 76, n).astype(float),
        "monthly_income": monthly_income,
        "employment_months": rng.gamma(2.0, 30.0, n).round().clip(0, 600),
        "employment_type": pick("employment_type", [0.62, 0.22, 0.10, 0.06]),
        "region": pick("region", [0.38, 0.27, 0.17, 0.12, 0.06]),
        "product_type": pick("product_type", [0.40, 0.32, 0.10, 0.18]),
        "loan_amount": loan_amount,
        "loan_term_months": loan_term.astype(float),
        "interest_rate": interest_rate,
        "installment_to_income": np.clip(installment / monthly_income, 0.01, 1.5).round(3),
        "bureau_score": bureau_score,
        "open_credit_lines": rng.poisson(3.2, n).astype(float),
        "bureau_inquiries_6m": rng.poisson(1.1, n).astype(float),
        "prior_delinquencies_24m": prior_delinquencies.astype(float),
        "credit_utilization": utilization,
        "months_as_client": rng.gamma(2.0, 24.0, n).round().clip(0, 600),
        "savings_balance": np.round(rng.lognormal(13.2, 1.1, n), -3),
        "has_payroll_deposit": rng.binomial(1, 0.35, n).astype(float),
        "digital_channel_share": rng.beta(3, 2, n).round(3),
        "education_level": pick("education_level", [0.34, 0.27, 0.30, 0.09]),
        "dependents": rng.poisson(1.2, n).clip(0, 15).astype(float),
        "housing_type": pick("housing_type", [0.36, 0.44, 0.20]),
    }

    # Delinquency behaviour. The event is rare by construction (risk R3).
    risk = (-3.1 - 0.011 * (bureau_score - 680) + 0.55 * prior_delinquencies
            + 1.4 * (utilization - 0.4) + 1.8 * (table["installment_to_income"] - 0.3)
            - 0.5 * table["has_payroll_deposit"])
    is_late = rng.random(n) < 1 / (1 + np.exp(-risk))
    days_late = np.where(is_late, rng.gamma(2.2, 22.0, n).round().clip(1, 90), 0.0)
    days_late[rng.random(n) < IMMATURE_SHARE] = np.nan
    table[DPD_COLUMN] = days_late

    for name, rate in MISSING_RATE.items():
        missing = rng.random(n) < rate
        column = table[name]
        column[missing] = None if variables[name].is_categorical else np.nan
    return table
