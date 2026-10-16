import numpy as np
import pytest

from finbank.targets import delinquency_targets, event_rate


def test_targets_at_the_boundaries():
    targets = delinquency_targets(np.array([0, 29, 30, 59, 60, 90]))
    assert targets["default_30d"].tolist() == [0, 0, 1, 1, 1, 1]
    assert targets["default_60d"].tolist() == [0, 0, 0, 0, 1, 1]


def test_unobserved_accounts_stay_missing():
    targets = delinquency_targets(np.array([np.nan, 45.0]))
    assert np.isnan(targets["default_30d"][0])
    assert np.isnan(targets["default_60d"][0])
    assert event_rate(targets["default_30d"]) == 1.0


def test_negative_days_past_due_are_rejected():
    with pytest.raises(ValueError):
        delinquency_targets(np.array([-1.0, 10.0]))


def test_default_at_60_implies_default_at_30(sample):
    targets = delinquency_targets(sample["max_days_past_due"])
    at_60 = targets["default_60d"] == 1
    assert (targets["default_30d"][at_60] == 1).all()
    assert 0 < event_rate(targets["default_60d"]) < event_rate(targets["default_30d"]) < 0.20
