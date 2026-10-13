import numpy as np

from finbank.quality import feature_dictionary, quality_report
from finbank.schema import SCHEMA

EXCLUDED = {"digital_channel_share", "education_level", "dependents", "housing_type"}


def test_report_has_one_row_per_candidate_variable(sample):
    report = quality_report(sample)
    assert [row["variable"] for row in report] == [v.name for v in SCHEMA]


def test_variables_below_threshold_are_excluded_with_a_reason(sample):
    report = quality_report(sample)
    excluded = {row["variable"] for row in report if row["decision"] == "exclude"}
    assert excluded == EXCLUDED
    assert all(row["reason"] for row in report if row["decision"] == "exclude")


def test_threshold_is_inclusive():
    variable = SCHEMA[0]
    table = {variable.name: np.array([30.0, 40.0, 50.0, 60.0, np.nan])}
    report = quality_report(table, schema=(variable,), threshold=0.80)
    assert report[0]["completeness"] == 0.8
    assert report[0]["decision"] == "keep"


def test_dictionary_holds_the_18_variables_kept(sample):
    dictionary = feature_dictionary(quality_report(sample))
    names = {row["variable"] for row in dictionary}
    assert len(dictionary) == 18
    assert names.isdisjoint(EXCLUDED)
    assert all(row["description"] and row["business_owner"] for row in dictionary)
