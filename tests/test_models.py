import itertools

import numpy as np
import pytest

from finbank.models import (CostMatrix, FeatureEncoder, LogisticModel, auc, best_threshold,
                            recall_precision)


def test_auc_extremes_and_ties():
    y = np.array([0, 0, 1, 1])
    assert auc(y, np.array([0.1, 0.2, 0.8, 0.9])) == 1.0
    assert auc(y, np.array([0.9, 0.8, 0.2, 0.1])) == 0.0
    assert auc(y, np.array([0.5, 0.5, 0.5, 0.5])) == 0.5


def test_auc_matches_pairwise_definition():
    rng = np.random.default_rng(1)
    y = rng.binomial(1, 0.3, 60)
    score = np.round(rng.random(60), 1)  # rounding creates ties on purpose
    pos, neg = score[y == 1], score[y == 0]
    pairs = [1.0 if p > n else 0.5 if p == n else 0.0 for p, n in itertools.product(pos, neg)]
    assert auc(y, score) == pytest.approx(np.mean(pairs))


def test_auc_needs_both_classes():
    with pytest.raises(ValueError):
        auc(np.array([1, 1]), np.array([0.2, 0.4]))


def test_logistic_model_recovers_the_direction_of_effects():
    rng = np.random.default_rng(3)
    X = rng.normal(size=(3000, 2))
    y = (rng.random(3000) < 1 / (1 + np.exp(-(-1 + 2 * X[:, 0] - 1 * X[:, 1])))).astype(float)
    model = LogisticModel(penalty=0.1).fit(X, y)
    assert model.coef[1] == pytest.approx(2, abs=0.25)
    assert model.coef[2] == pytest.approx(-1, abs=0.25)
    assert auc(y, model.predict_proba(X)) > 0.8


def test_scoring_before_fitting_is_an_error():
    with pytest.raises(RuntimeError):
        LogisticModel().predict_proba(np.zeros((2, 2)))


def test_encoder_learns_only_from_the_development_cohort():
    dev = {"x": np.array([1.0, np.nan, 3.0]), "c": np.array(["a", "b", None], dtype=object)}
    later = {"x": np.array([np.nan, 100.0]), "c": np.array(["b", "a"], dtype=object)}
    encoder = FeatureEncoder(("x",), {"c": ("a", "b")}).fit(dev)
    assert encoder.medians["x"] == 2.0
    X = encoder.transform(later)
    assert X.shape == (2, 2)
    assert X[0, 0] == pytest.approx(0.0)  # missing value imputed with the development median
    assert X[:, 1].tolist() == [1.0, 0.0]  # one-hot for level "b", "a" is the reference
    assert encoder.names == ["x", "c=b"]


def test_recall_and_precision_at_a_cut_off():
    y = np.array([1, 1, 0, 0, 1])
    score = np.array([0.9, 0.2, 0.8, 0.1, 0.6])
    assert recall_precision(y, score, 0.5) == pytest.approx((2 / 3, 2 / 3))


def test_best_threshold_maximizes_net_benefit():
    y = np.array([1, 1, 0, 0, 0, 0])
    score = np.array([0.9, 0.6, 0.55, 0.3, 0.2, 0.1])
    costs = CostMatrix(benefit_true_positive=100, cost_contact=40)
    grid = np.array([0.15, 0.5, 0.58, 0.95])
    # 0.58 flags the two clients who default: 2 * 100 - 2 * 40 = 120, the best value.
    assert best_threshold(y, score, costs, grid) == 0.58


def test_minimum_recall_constrains_the_cost_optimum():
    y = np.array([1, 1, 0, 0, 1])
    score = np.array([0.9, 0.8, 0.7, 0.6, 0.3])
    costs = CostMatrix(benefit_true_positive=100, cost_contact=60)
    grid = np.array([0.2, 0.75])
    assert best_threshold(y, score, costs, grid) == 0.75
    assert best_threshold(y, score, costs, grid, min_recall=1.0) == 0.2
    with pytest.raises(ValueError):
        best_threshold(y, score, costs, np.array([0.95]), min_recall=0.5)
