"""Integrity rules a table must satisfy before it feeds a quality report or a model."""
from dataclasses import dataclass

import numpy as np

from finbank.schema import ID_COLUMN, SCHEMA, Variable

# Ley 1581 de 2012: personal data is anonymized before it leaves the bank (risk R5).
PII_COLUMNS = frozenset(
    {"name", "full_name", "national_id", "cedula", "phone", "email", "address", "birth_date"}
)


@dataclass(frozen=True)
class Violation:
    rule: str
    column: str
    rows: int


def is_missing(column: np.ndarray) -> np.ndarray:
    if column.dtype == object:
        return np.array([value is None for value in column], dtype=bool)
    return np.isnan(column)


def validate(table, schema: tuple[Variable, ...] = SCHEMA) -> list[Violation]:
    """Return every rule broken by the table. An empty list means the table is valid."""
    violations = _check_identifier(table) + _check_no_pii(table)
    for variable in schema:
        if variable.name not in table:
            violations.append(Violation("missing_column", variable.name, 0))
        else:
            violations += _check_variable(table[variable.name], variable)
    return violations


def assert_valid(table, schema: tuple[Variable, ...] = SCHEMA) -> None:
    violations = validate(table, schema)
    if violations:
        detail = "; ".join(f"{v.rule}[{v.column}]={v.rows}" for v in violations)
        raise ValueError(f"Table failed validation: {detail}")


def _check_identifier(table) -> list[Violation]:
    if ID_COLUMN not in table:
        return [Violation("missing_column", ID_COLUMN, 0)]
    ids = table[ID_COLUMN]
    violations = []
    nulls = int(is_missing(ids).sum())
    if nulls:
        violations.append(Violation("null_identifier", ID_COLUMN, nulls))
    present = ids[~is_missing(ids)]
    duplicated = len(present) - len(set(present))
    if duplicated:
        violations.append(Violation("duplicated_identifier", ID_COLUMN, duplicated))
    return violations


def _check_no_pii(table) -> list[Violation]:
    return [
        Violation("personal_data_column", name, len(table[name]))
        for name in table
        if name.lower() in PII_COLUMNS
    ]


def _check_variable(column: np.ndarray, variable: Variable) -> list[Violation]:
    present = column[~is_missing(column)]
    if variable.is_categorical:
        unknown = sum(value not in variable.categories for value in present)
        return [Violation("unknown_category", variable.name, unknown)] if unknown else []
    if column.dtype == object:
        return [Violation("not_numeric", variable.name, len(present))]
    violations = []
    if variable.minimum is not None:
        below = int((present < variable.minimum).sum())
        if below:
            violations.append(Violation("below_minimum", variable.name, below))
    if variable.maximum is not None:
        above = int((present > variable.maximum).sum())
        if above:
            violations.append(Violation("above_maximum", variable.name, above))
    return violations
