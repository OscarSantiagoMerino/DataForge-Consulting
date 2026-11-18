import numpy as np
import pytest

from finbank.churn import CHURN_TARGET, generate_churn_sample
from finbank.pilot import TARGET_AUC, TARGET_RECALL, deciles, pseudonymize, run_pilot
from finbank.validation import PII_COLUMNS

LIST_COLUMNS = {"client_key", "probability", "decile", "action"}


@pytest.fixture(scope="module")
def pilot():
    return run_pilot()


def metric(result, name):
    return next(row["value"] for row in result.metrics if row["metric"] == name)


def test_pseudonym_is_stable_salted_and_hides_the_identifier():
    key = pseudonymize("C000123", salt="s1")
    assert key == pseudonymize("C000123", salt="s1")
    assert key != pseudonymize("C000123", salt="s2")
    assert "C000123" not in key and len(key) == 16


def test_deciles_run_from_highest_to_lowest_risk():
    d = deciles(np.linspace(1, 0, 100))
    assert d[0] == 1 and d[-1] == 10
    assert np.bincount(d)[1:].tolist() == [10] * 10


def test_churn_sample_has_a_rare_event_and_a_later_cohort_shift():
    base = generate_churn_sample(3000, seed=5)
    shifted = generate_churn_sample(3000, seed=5, shift=1.0)
    assert 0.03 < base[CHURN_TARGET].mean() < 0.20
    assert shifted["complaints_6m"].mean() > base["complaints_6m"].mean()


def test_lists_carry_no_personal_data_and_only_pseudonymous_keys(pilot):
    for rows in (pilot.early_warning, pilot.churn_list):
        assert rows and all(set(row) == LIST_COLUMNS for row in rows)
        assert not LIST_COLUMNS & PII_COLUMNS
        keys = [row["client_key"] for row in rows]
        assert all(len(k) == 16 and set(k) <= set("0123456789abcdef") for k in keys)
        assert len(set(keys)) == len(keys)


def test_lists_are_sorted_and_flag_clients_above_the_cut_off(pilot):
    probabilities = [row["probability"] for row in pilot.early_warning]
    assert probabilities == sorted(probabilities, reverse=True)
    flagged = [row for row in pilot.early_warning if row["action"] != "seguimiento normal"]
    assert flagged and min(r["probability"] for r in flagged) >= pilot.delinquency_threshold


def test_prototype_metrics_against_the_charter_measures(pilot):
    # Regression check of the prototype on synthetic data, not a FinBank validation.
    assert metric(pilot, "auc_out_of_time_default_30d") >= TARGET_AUC
    assert metric(pilot, "recall_at_operating_threshold") >= TARGET_RECALL
    assert metric(pilot, "recall_at_cost_only_threshold") < TARGET_RECALL
    assert (metric(pilot, "net_benefit_cop_at_cost_only_threshold")
            > metric(pilot, "net_benefit_cop_at_operating_threshold"))


def test_two_runs_give_identical_outputs(pilot):
    again = run_pilot()
    assert again.metrics == pilot.metrics
    assert again.early_warning == pilot.early_warning
    assert again.churn_list == pilot.churn_list


def test_metric_names_are_unique(pilot):
    names = [row["metric"] for row in pilot.metrics]
    assert len(names) == len(set(names))
