"""Prototype scoring models for the pilot (S6-01, objectives O1-O3).

The models are fitted on synthetic data with a fixed seed. Their metrics are
prototype results that show the method works end to end; they are not a
validation on FinBank data, which stays pending until the real extract is used.
Only numpy is required, so the same code runs in CI.
"""
from dataclasses import dataclass, field

import numpy as np

from finbank.validation import is_missing

Table = dict[str, np.ndarray]


@dataclass
class FeatureEncoder:
    """Median imputation and standardization for numeric columns, one-hot for categories.

    Statistics are learned on the development cohort only and reused, unchanged,
    on any later cohort, so the out-of-time sample never leaks into training.
    """
    numeric: tuple[str, ...]
    categorical: dict[str, tuple[str, ...]] = field(default_factory=dict)
    medians: dict[str, float] = field(default_factory=dict)
    means: dict[str, float] = field(default_factory=dict)
    scales: dict[str, float] = field(default_factory=dict)

    def fit(self, table: Table) -> "FeatureEncoder":
        for name in self.numeric:
            column = np.asarray(table[name], dtype=float)
            median = float(np.nanmedian(column))
            filled = np.where(np.isnan(column), median, column)
            self.medians[name] = median
            self.means[name] = float(filled.mean())
            self.scales[name] = float(filled.std()) or 1.0
        return self

    @property
    def names(self) -> list[str]:
        names = list(self.numeric)
        for name, levels in self.categorical.items():
            names += [f"{name}={level}" for level in levels[1:]]  # first level is the reference
        return names

    def transform(self, table: Table) -> np.ndarray:
        columns = []
        for name in self.numeric:
            column = np.asarray(table[name], dtype=float)
            column = np.where(np.isnan(column), self.medians[name], column)
            columns.append((column - self.means[name]) / self.scales[name])
        for name, levels in self.categorical.items():
            values = table[name]
            missing = is_missing(values)
            for level in levels[1:]:
                columns.append(np.array([(not m) and v == level for v, m in zip(values, missing)],
                                        dtype=float))
        return np.column_stack(columns)


@dataclass
class LogisticModel:
    """L2-penalized logistic regression fitted by Newton-Raphson (IRLS)."""
    penalty: float = 1.0
    max_iter: int = 50
    tol: float = 1e-8
    coef: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LogisticModel":
        X1 = np.column_stack([np.ones(len(X)), X])
        y = np.asarray(y, dtype=float)
        beta = np.zeros(X1.shape[1])
        ridge = np.full(X1.shape[1], self.penalty)
        ridge[0] = 0.0  # the intercept is not penalized
        for _ in range(self.max_iter):
            p = _sigmoid(X1 @ beta)
            gradient = X1.T @ (y - p) - ridge * beta
            hessian = (X1 * (p * (1 - p))[:, None]).T @ X1 + np.diag(ridge)
            step = np.linalg.solve(hessian, gradient)
            beta += step
            if np.max(np.abs(step)) < self.tol:
                break
        self.coef = beta
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.coef is None:
            raise RuntimeError("fit the model before scoring")
        return _sigmoid(self.coef[0] + X @ self.coef[1:])


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -35, 35)))


def auc(y: np.ndarray, score: np.ndarray) -> float:
    """Area under the ROC curve via the Mann-Whitney statistic, with average ranks for ties."""
    y = np.asarray(y, dtype=float)
    score = np.asarray(score, dtype=float)
    positives = int(y.sum())
    negatives = len(y) - positives
    if positives == 0 or negatives == 0:
        raise ValueError("AUC needs both classes")
    order = np.argsort(score, kind="mergesort")
    ranks = np.empty(len(score))
    sorted_scores = score[order]
    i = 0
    while i < len(score):
        j = i
        while j + 1 < len(score) and sorted_scores[j + 1] == sorted_scores[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return float((ranks[y == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))


def recall_precision(y: np.ndarray, score: np.ndarray, threshold: float) -> tuple[float, float]:
    y = np.asarray(y, dtype=bool)
    flagged = np.asarray(score) >= threshold
    true_pos = int((flagged & y).sum())
    recall = true_pos / max(int(y.sum()), 1)
    precision = true_pos / max(int(flagged.sum()), 1)
    return recall, precision


@dataclass(frozen=True)
class CostMatrix:
    """Value of acting on a flagged client (O3).

    benefit_true_positive: expected loss avoided when a client who would have
    defaulted (or churned) is contacted. cost_contact: cost of each contact,
    paid for true and false positives alike. Amounts in COP per client.
    """
    benefit_true_positive: float
    cost_contact: float

    def net_benefit(self, y: np.ndarray, score: np.ndarray, threshold: float) -> float:
        y = np.asarray(y, dtype=bool)
        flagged = np.asarray(score) >= threshold
        return float((flagged & y).sum() * self.benefit_true_positive
                     - flagged.sum() * self.cost_contact)


def best_threshold(y: np.ndarray, score: np.ndarray, costs: CostMatrix,
                   grid: np.ndarray | None = None, min_recall: float | None = None) -> float:
    """Cut-off that maximizes net monetary benefit on the development cohort.

    With min_recall, only cut-offs that keep at least that recall are eligible:
    the decision rule when a Charter measure (O2) constrains the cost optimum (O3).
    """
    grid = np.round(np.arange(0.01, 0.91, 0.01), 2) if grid is None else grid
    if min_recall is not None:
        grid = np.array([t for t in grid if recall_precision(y, score, t)[0] >= min_recall])
        if len(grid) == 0:
            raise ValueError(f"no cut-off reaches a recall of {min_recall}")
    benefits = [costs.net_benefit(y, score, t) for t in grid]
    return float(grid[int(np.argmax(benefits))])
