import numpy as np
import pytest

from finbank.validation import Violation, assert_valid, validate


def test_sample_respects_every_rule(sample):
    assert validate(sample) == []


def test_bureau_score_outside_range_is_reported(sample):
    sample["bureau_score"][:3] = [1200, 99, 951]
    violations = validate(sample)
    assert Violation("above_maximum", "bureau_score", 2) in violations
    assert Violation("below_minimum", "bureau_score", 1) in violations


def test_missing_values_are_not_range_violations(sample):
    sample["bureau_score"][:50] = np.nan
    assert validate(sample) == []


def test_duplicated_and_null_identifiers_are_reported(sample):
    sample["client_id"][1] = sample["client_id"][0]
    sample["client_id"][2] = None
    violations = validate(sample)
    assert Violation("duplicated_identifier", "client_id", 1) in violations
    assert Violation("null_identifier", "client_id", 1) in violations


def test_unknown_category_is_reported(sample):
    sample["product_type"][0] = "mortgage"
    assert validate(sample) == [Violation("unknown_category", "product_type", 1)]


def test_numeric_variable_loaded_as_text_is_reported(sample):
    sample["age"] = sample["age"].astype(str).astype(object)
    assert Violation("not_numeric", "age", 2000) in validate(sample)


def test_personal_data_column_is_rejected(sample):
    sample["cedula"] = np.arange(2000, dtype=float)
    with pytest.raises(ValueError, match="personal_data_column"):
        assert_valid(sample)


def test_missing_column_is_reported(sample):
    del sample["loan_amount"]
    assert validate(sample) == [Violation("missing_column", "loan_amount", 0)]
