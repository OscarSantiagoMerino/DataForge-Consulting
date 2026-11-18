"""Weekly monitoring of the pilot models (S6-02, objective O4).

Two controls, both from the monitoring plan in the proposal:
- Stability: population stability index (PSI) of the score and of each numeric
  variable against the development cohort. < 0.10 stable, 0.10-0.25 watch,
  >= 0.25 alert.
- Performance: the model is flagged for retraining when AUC (or recall) falls
  more than 0.05 below its baseline for 2 consecutive weeks.
"""
import numpy as np

from finbank.models import auc
from finbank.sample import generate_sample
from finbank.schema import DPD_COLUMN
from finbank.targets import delinquency_targets

PSI_WATCH = 0.10
PSI_ALERT = 0.25
MAX_DROP = 0.05
CONSECUTIVE_WEEKS = 2


def psi(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    """Population stability index with bins at the reference deciles."""
    reference = np.asarray(reference, dtype=float)
    current = np.asarray(current, dtype=float)
    reference = reference[~np.isnan(reference)]
    current = current[~np.isnan(current)]
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    expected = np.histogram(reference, edges)[0] / len(reference)
    actual = np.histogram(current, edges)[0] / len(current)
    expected = np.clip(expected, 1e-4, None)
    actual = np.clip(actual, 1e-4, None)
    return float(np.sum((actual - expected) * np.log(actual / expected)))


def psi_status(value: float) -> str:
    if value >= PSI_ALERT:
        return "alerta"
    if value >= PSI_WATCH:
        return "vigilar"
    return "estable"


def retraining_flags(weekly_metric: list[float], baseline: float, max_drop: float = MAX_DROP,
                     consecutive: int = CONSECUTIVE_WEEKS) -> list[bool]:
    """True from the week in which the drop has lasted `consecutive` weeks in a row."""
    flags, streak = [], 0
    for value in weekly_metric:
        drop = round(baseline - value, 6)  # avoid 0.80 - 0.75 > 0.05 from float error
        streak = streak + 1 if drop > max_drop else 0
        flags.append(streak >= consecutive)
    return flags


def simulate_weeks(fitted, weeks: int = 6, shift_from: int = 4, n_clients: int = 3000,
                   seed: int = 3000) -> list[dict]:
    """Weekly cohorts for the monitoring demo.

    From week `shift_from` the population changes: bureau scores fall 60 points
    (covariate drift) and part of the outcomes stop following the old pattern
    (concept drift). Both changes are synthetic and only test the controls.
    """
    reference = generate_sample(5000, seed=2026)
    reference_scores = fitted.development_scores
    baseline_auc = auc(fitted.development_target, reference_scores)
    numeric = [n for n in fitted.encoder.numeric]
    rows = []
    for week in range(1, weeks + 1):
        rng = np.random.default_rng(seed + week)
        table = generate_sample(n_clients, seed=seed + week)
        target = delinquency_targets(table[DPD_COLUMN])["default_30d"]
        if week >= shift_from:
            table["bureau_score"] = np.clip(table["bureau_score"] - 60, 150, 950)
            observed = ~np.isnan(target)
            noisy = observed & (rng.random(len(target)) < 0.45)
            target[noisy] = (rng.random(int(noisy.sum())) < np.nanmean(target)).astype(float)
        scores = fitted.score(table)
        mask = ~np.isnan(target)
        variable_psi = {n: psi(reference[n], table[n]) for n in numeric}
        top = max(variable_psi, key=variable_psi.get)
        score_psi = psi(reference_scores, scores)
        rows.append({
            "week": week,
            "clients": n_clients,
            "psi_score": round(score_psi, 4),
            "psi_score_status": psi_status(score_psi),
            "top_variable": top,
            "psi_top_variable": round(variable_psi[top], 4),
            "psi_top_variable_status": psi_status(variable_psi[top]),
            "auc_30d": round(auc(target[mask], scores[mask]), 4),
            "auc_baseline": round(baseline_auc, 4),
        })
    flags = retraining_flags([r["auc_30d"] for r in rows], baseline_auc)
    for row, flag in zip(rows, flags):
        row["auc_drop"] = round(row["auc_baseline"] - row["auc_30d"], 4)
        row["retraining_flag"] = flag
    return rows
