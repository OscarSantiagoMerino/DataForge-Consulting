"""Integrity rules a table must satisfy before it feeds a quality report or a model."""
from dataclasses import dataclass

import numpy as np

PII_COLUMNS = frozenset(
    {"name", "full_name", "national_id", "cedula", "phone", "email", "address", "birth_date"}
)


@dataclass(frozen=True)
class Violation:
    rule: str
    column: str
    rows: int


def validate(table) -> list[Violation]:
    violations = []

    ids = table["client_id"]
    null_ids = np.array([value is None for value in ids], dtype=bool)
    if null_ids.sum() > 0:
        violations.append(Violation("null_identifier", "client_id", int(null_ids.sum())))
    present_ids = ids[~null_ids]
    if len(present_ids) != len(set(present_ids)):
        violations.append(
            Violation("duplicated_identifier", "client_id", len(present_ids) - len(set(present_ids))))

    for name in table:
        if name.lower() in PII_COLUMNS:
            violations.append(Violation("personal_data_column", name, len(table[name])))

    age = table["age"]
    if age.dtype == object:
        violations.append(Violation("not_numeric", "age", len(age)))
    else:
        age = age[~np.isnan(age)]
        if (age < 18).sum() > 0:
            violations.append(Violation("below_minimum", "age", int((age < 18).sum())))
        if (age > 90).sum() > 0:
            violations.append(Violation("above_maximum", "age", int((age > 90).sum())))

    score = table["bureau_score"]
    if score.dtype == object:
        violations.append(Violation("not_numeric", "bureau_score", len(score)))
    else:
        score = score[~np.isnan(score)]
        if (score < 150).sum() > 0:
            violations.append(Violation("below_minimum", "bureau_score", int((score < 150).sum())))
        if (score > 950).sum() > 0:
            violations.append(Violation("above_maximum", "bureau_score", int((score > 950).sum())))

    utilization = table["credit_utilization"]
    if utilization.dtype == object:
        violations.append(Violation("not_numeric", "credit_utilization", len(utilization)))
    else:
        utilization = utilization[~np.isnan(utilization)]
        if (utilization < 0).sum() > 0:
            violations.append(
                Violation("below_minimum", "credit_utilization", int((utilization < 0).sum())))
        if (utilization > 1).sum() > 0:
            violations.append(
                Violation("above_maximum", "credit_utilization", int((utilization > 1).sum())))

    burden = table["installment_to_income"]
    if burden.dtype == object:
        violations.append(Violation("not_numeric", "installment_to_income", len(burden)))
    else:
        burden = burden[~np.isnan(burden)]
        if (burden < 0).sum() > 0:
            violations.append(
                Violation("below_minimum", "installment_to_income", int((burden < 0).sum())))
        if (burden > 1.5).sum() > 0:
            violations.append(
                Violation("above_maximum", "installment_to_income", int((burden > 1.5).sum())))

    products = table["product_type"]
    unknown = 0
    for value in products:
        if value is not None and value not in ("consumer", "credit_card", "vehicle", "payroll_loan"):
            unknown += 1
    if unknown > 0:
        violations.append(Violation("unknown_category", "product_type", unknown))

    return violations


def assert_valid(table) -> None:
    violations = validate(table)
    if violations:
        detail = "; ".join(f"{v.rule}[{v.column}]={v.rows}" for v in violations)
        raise ValueError(f"Table failed validation: {detail}")
