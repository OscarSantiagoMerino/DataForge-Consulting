import numpy as np
import pytest

from finbank import monitoring
from finbank.monitoring import psi, psi_status, retraining_flags, simulate_weeks
from finbank.pilot import fit_delinquency_model


def test_psi_is_near_zero_for_the_same_population_and_grows_with_a_shift():
    rng = np.random.default_rng(0)
    reference = rng.normal(0, 1, 5000)
    assert psi(reference, rng.normal(0, 1, 5000)) < 0.02
    assert psi(reference, rng.normal(0.5, 1, 5000)) > 0.10
    assert psi(reference, rng.normal(1.0, 1, 5000)) > 0.25


def test_psi_ignores_missing_values():
    reference = np.array([1.0, 2.0, 3.0, 4.0, np.nan] * 200)
    assert psi(reference, reference) == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("value,status", [(0.05, "estable"), (0.10, "vigilar"),
                                          (0.2499, "vigilar"), (0.25, "alerta")])
def test_psi_status_bands(value, status):
    assert psi_status(value) == status


def test_one_bad_week_does_not_trigger_retraining():
    assert retraining_flags([0.79, 0.72, 0.79, 0.78], baseline=0.80) == [False] * 4


def test_two_consecutive_drops_trigger_retraining():
    assert retraining_flags([0.79, 0.74, 0.73, 0.70], baseline=0.80) == [False, False, True, True]


def test_a_drop_of_exactly_the_limit_is_tolerated():
    assert retraining_flags([0.75, 0.75], baseline=0.80) == [False, False]


def test_two_recall_drops_trigger_retraining_with_stable_auc(monkeypatch):
    fitted = fit_delinquency_model()
    recall_values = iter([0.80, 0.74, 0.75, 0.74, 0.73])

    def recall_at_operating_threshold(target, scores, threshold):
        assert threshold == fitted.threshold
        return next(recall_values), 0.20

    monkeypatch.setattr(monitoring, "auc", lambda target, scores: 0.80)
    monkeypatch.setattr(monitoring, "recall_precision", recall_at_operating_threshold)
    rows = simulate_weeks(fitted, weeks=4)

    assert [row["recall_baseline"] for row in rows] == [0.80] * 4
    assert [row["recall_drop"] for row in rows] == [0.06, 0.05, 0.06, 0.07]
    assert [row["retraining_flag"] for row in rows] == [False, False, False, True]


@pytest.fixture(scope="module")
def weeks():
    return simulate_weeks(fit_delinquency_model())


def test_monitoring_demo_is_quiet_before_the_injected_change(weeks):
    for row in weeks[:3]:
        assert row["psi_score_status"] == "estable"
        assert not row["retraining_flag"]


def test_monitoring_demo_detects_the_change_when_it_happens(weeks):
    week4 = weeks[3]
    assert week4["top_variable"] == "bureau_score"
    assert week4["psi_top_variable_status"] == "alerta"
    assert not week4["retraining_flag"]  # one week of drop only
    assert weeks[4]["retraining_flag"]  # second consecutive week
