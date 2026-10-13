"""Single source of truth for the candidate variables of the delinquency model.

Validation rules, the quality report and the feature dictionary are all derived
from SCHEMA, so a bound or a description is written exactly once.
"""
from dataclasses import dataclass

ID_COLUMN = "client_id"
DPD_COLUMN = "max_days_past_due"

# Agreed with FinBank in Sprint 2 (risk R2): variables below this share of
# non-missing values are excluded and the exclusion is documented.
COMPLETENESS_THRESHOLD = 0.80


@dataclass(frozen=True)
class Variable:
    name: str
    description: str
    owner: str
    minimum: float | None = None
    maximum: float | None = None
    categories: tuple[str, ...] | None = None

    @property
    def is_categorical(self) -> bool:
        return self.categories is not None


RISK = "Risk and Analytics"
COLLECTIONS = "Collections"

SCHEMA: tuple[Variable, ...] = (
    Variable("age", "Age of the client at origination, in years", RISK, 18, 90),
    Variable("monthly_income", "Verified monthly income, COP", RISK, 0, None),
    Variable("employment_months", "Months in current employment", RISK, 0, 600),
    Variable("employment_type", "Type of employment contract", RISK,
             categories=("employee", "self_employed", "pensioner", "other")),
    Variable("region", "Region of the originating branch", COLLECTIONS,
             categories=("bogota", "andina", "caribe", "pacifica", "orinoquia")),
    Variable("product_type", "Credit product", RISK,
             categories=("consumer", "credit_card", "vehicle", "payroll_loan")),
    Variable("loan_amount", "Amount disbursed, COP", RISK, 0, None),
    Variable("loan_term_months", "Contractual term, in months", RISK, 1, 120),
    Variable("interest_rate", "Annual effective rate, as a fraction", RISK, 0, 0.60),
    Variable("installment_to_income", "Monthly installment over monthly income", RISK, 0, 1.5),
    Variable("bureau_score", "Credit bureau score at origination", RISK, 150, 950),
    Variable("open_credit_lines", "Open credit lines in the bureau", RISK, 0, 60),
    Variable("bureau_inquiries_6m", "Bureau inquiries in the last 6 months", RISK, 0, 50),
    Variable("prior_delinquencies_24m", "Delinquency events in the last 24 months", COLLECTIONS, 0, 24),
    Variable("credit_utilization", "Used share of revolving credit limits", RISK, 0, 1),
    Variable("months_as_client", "Months since the first product with FinBank", RISK, 0, 600),
    Variable("savings_balance", "Average savings balance, last 3 months, COP", RISK, 0, None),
    Variable("has_payroll_deposit", "1 if salary is deposited at FinBank", COLLECTIONS, 0, 1),
    Variable("digital_channel_share", "Share of transactions made in digital channels", RISK, 0, 1),
    Variable("education_level", "Highest education level declared", RISK,
             categories=("secondary", "technical", "university", "postgraduate")),
    Variable("dependents", "Number of economic dependents declared", RISK, 0, 15),
    Variable("housing_type", "Housing tenure declared", RISK,
             categories=("owned", "rented", "family")),
)
