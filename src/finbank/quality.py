"""Data quality report and feature dictionary (user story US-05)."""
import numpy as np

from finbank.schema import COMPLETENESS_THRESHOLD, SCHEMA, Variable


def is_missing(column: np.ndarray) -> np.ndarray:
    if column.dtype == object:
        return np.array([value is None for value in column], dtype=bool)
    return np.isnan(column)


def quality_report(table, schema: tuple[Variable, ...] = SCHEMA,
                   threshold: float = COMPLETENESS_THRESHOLD) -> list[dict]:
    """One row per candidate variable with its completeness and the keep/exclude decision."""
    report = []
    for variable in schema:
        column = table[variable.name]
        completeness = float(1 - is_missing(column).mean()) if len(column) else 0.0
        keep = completeness >= threshold
        report.append({
            "variable": variable.name,
            "type": "categorical" if variable.is_categorical else "numeric",
            "completeness": round(completeness, 4),
            "decision": "keep" if keep else "exclude",
            "reason": "" if keep else f"completeness below {threshold:.0%}",
        })
    return report


def feature_dictionary(report: list[dict], schema: tuple[Variable, ...] = SCHEMA) -> list[dict]:
    """Variables kept by the quality report, described for the business owner who validates them."""
    kept = {row["variable"]: row for row in report if row["decision"] == "keep"}
    return [
        {
            "variable": variable.name,
            "description": variable.description,
            "type": kept[variable.name]["type"],
            "valid_values": _valid_values(variable),
            "completeness": kept[variable.name]["completeness"],
            "business_owner": variable.owner,
        }
        for variable in schema
        if variable.name in kept
    ]


def _valid_values(variable: Variable) -> str:
    if variable.is_categorical:
        return " | ".join(variable.categories)
    low = "-inf" if variable.minimum is None else f"{variable.minimum:g}"
    high = "inf" if variable.maximum is None else f"{variable.maximum:g}"
    return f"[{low}, {high}]"
