"""Controlled pilot (S6-01): weekly early warning list and churn list.

Flow: development cohort -> quality report -> feature dictionary -> fitted
models -> cut-offs from the cost matrix -> out-of-time cohort -> metrics ->
lists for the controlled segment. Everything runs on synthetic data with fixed
seeds, so two runs give the same files.
"""
import hashlib
import os
from dataclasses import dataclass

import numpy as np

from finbank.churn import CHURN_CATEGORICAL, CHURN_NUMERIC, CHURN_TARGET, generate_churn_sample
from finbank.models import (CostMatrix, FeatureEncoder, LogisticModel, auc, best_threshold,
                            recall_precision)
from finbank.quality import feature_dictionary, quality_report
from finbank.sample import generate_sample
from finbank.schema import DPD_COLUMN, ID_COLUMN, SCHEMA
from finbank.targets import delinquency_targets

DEVELOPMENT_SEED = 2026
OUT_OF_TIME_SEED = 2027  # independent synthetic draw that plays the role of the later cohort
PILOT_REGION = "andina"  # controlled segment agreed for the pilot in the scenario

# Scenario parameters for O3, in COP per client. They are inputs for the
# Finance review, not amounts approved by FinBank.
DELINQUENCY_COSTS = CostMatrix(benefit_true_positive=360_000, cost_contact=25_000)
CHURN_COSTS = CostMatrix(benefit_true_positive=315_000, cost_contact=60_000)

# Charter success measures.
TARGET_AUC = 0.75
TARGET_RECALL = 0.60

PSEUDONYM_SALT_ENV = "FINBANK_PSEUDONYM_SALT"
DEMO_SALT = "demo-salt-not-for-production"


def pseudonymize(client_id: str, salt: str | None = None) -> str:
    """Irreversible identifier for the lists that leave the analytics area (Ley 1581, risk R5)."""
    salt = salt if salt is not None else os.environ.get(PSEUDONYM_SALT_ENV, DEMO_SALT)
    return hashlib.sha256(f"{salt}|{client_id}".encode("utf-8")).hexdigest()[:16]


def deciles(score: np.ndarray) -> np.ndarray:
    """1 = highest risk decile, 10 = lowest."""
    order = np.argsort(-np.asarray(score), kind="mergesort")
    ranks = np.empty(len(score), dtype=int)
    ranks[order] = np.arange(len(score))
    return (ranks * 10 // len(score)) + 1


@dataclass
class PilotResult:
    metrics: list[dict]
    early_warning: list[dict]
    churn_list: list[dict]
    delinquency_threshold: float
    churn_threshold: float
    variables_used: list[str]


def _delinquency_encoder(dev_table) -> tuple[FeatureEncoder, list[str]]:
    kept = [row["variable"] for row in feature_dictionary(quality_report(dev_table))]
    by_name = {v.name: v for v in SCHEMA}
    numeric = tuple(n for n in kept if not by_name[n].is_categorical)
    categorical = {n: by_name[n].categories for n in kept if by_name[n].is_categorical}
    return FeatureEncoder(numeric, categorical).fit(dev_table), kept


def _observed(table, target: np.ndarray):
    mask = ~np.isnan(target)
    return {k: v[mask] for k, v in table.items()}, target[mask]


def run_pilot(n_clients: int = 5000, n_preferential: int = 4000,
              salt: str | None = None) -> PilotResult:
    # Delinquency model at 30 days (O1). The 60 day target is scored with the same model.
    dev = generate_sample(n_clients, seed=DEVELOPMENT_SEED)
    oot = generate_sample(n_clients, seed=OUT_OF_TIME_SEED)
    encoder, kept = _delinquency_encoder(dev)
    dev_targets = delinquency_targets(dev[DPD_COLUMN])
    dev_obs, y_dev = _observed(dev, dev_targets["default_30d"])
    model = LogisticModel(penalty=1.0).fit(encoder.transform(dev_obs), y_dev)
    p_dev = model.predict_proba(encoder.transform(dev_obs))
    threshold = best_threshold(y_dev, p_dev, DELINQUENCY_COSTS)

    metrics = []
    oot_targets = delinquency_targets(oot[DPD_COLUMN])
    for horizon in ("default_30d", "default_60d"):
        oot_obs, y_oot = _observed(oot, oot_targets[horizon])
        p_oot = model.predict_proba(encoder.transform(oot_obs))
        value = auc(y_oot, p_oot)
        metrics.append({"model": "delinquency", "metric": f"auc_out_of_time_{horizon}",
                        "value": round(value, 4), "target": TARGET_AUC,
                        "meets_target": value >= TARGET_AUC, "sample": len(y_oot),
                        "event_rate": round(float(y_oot.mean()), 4)})

    # Churn model with a three month horizon (O2).
    churn_dev = generate_churn_sample(n_preferential, seed=DEVELOPMENT_SEED)
    churn_oot = generate_churn_sample(n_preferential, seed=OUT_OF_TIME_SEED)
    churn_encoder = FeatureEncoder(CHURN_NUMERIC, CHURN_CATEGORICAL).fit(churn_dev)
    churn_model = LogisticModel(penalty=1.0).fit(churn_encoder.transform(churn_dev),
                                                 churn_dev[CHURN_TARGET])
    y_churn_dev = churn_dev[CHURN_TARGET]
    pc_dev = churn_model.predict_proba(churn_encoder.transform(churn_dev))
    # O3 alone (maximum net benefit) versus the decision rule that also honours O2.
    cost_only_threshold = best_threshold(y_churn_dev, pc_dev, CHURN_COSTS)
    churn_threshold = best_threshold(y_churn_dev, pc_dev, CHURN_COSTS, min_recall=TARGET_RECALL)
    pc_oot = churn_model.predict_proba(churn_encoder.transform(churn_oot))
    y_churn_oot = churn_oot[CHURN_TARGET]
    churn_rate = round(float(y_churn_oot.mean()), 4)
    metrics.append({"model": "churn", "metric": "auc_out_of_time_churn_3m",
                    "value": round(auc(y_churn_oot, pc_oot), 4), "target": "",
                    "meets_target": "", "sample": len(pc_oot), "event_rate": churn_rate})
    for label, cut in (("operating_threshold", churn_threshold),
                       ("cost_only_threshold", cost_only_threshold)):
        recall, precision = recall_precision(y_churn_oot, pc_oot, cut)
        benefit = CHURN_COSTS.net_benefit(y_churn_oot, pc_oot, cut)
        metrics += [
            {"model": "churn", "metric": f"cutoff_{label}", "value": cut, "target": "",
             "meets_target": "", "sample": len(pc_oot), "event_rate": churn_rate},
            {"model": "churn", "metric": f"recall_at_{label}", "value": round(recall, 4),
             "target": TARGET_RECALL, "meets_target": recall >= TARGET_RECALL,
             "sample": len(pc_oot), "event_rate": churn_rate},
            {"model": "churn", "metric": f"precision_at_{label}", "value": round(precision, 4),
             "target": "", "meets_target": "", "sample": len(pc_oot), "event_rate": churn_rate},
            {"model": "churn", "metric": f"net_benefit_cop_at_{label}", "value": round(benefit),
             "target": "", "meets_target": "", "sample": len(pc_oot), "event_rate": churn_rate},
        ]
    metrics.append({"model": "delinquency", "metric": "cutoff_delinquency_threshold",
                    "value": threshold, "target": "", "meets_target": "",
                    "sample": len(y_dev), "event_rate": round(float(y_dev.mean()), 4)})

    # Lists for the controlled segment of the out-of-time cohort (the "current week").
    segment = oot["region"] == PILOT_REGION
    p_segment = model.predict_proba(encoder.transform({k: v[segment] for k, v in oot.items()}))
    early_warning = _build_list(oot[ID_COLUMN][segment], p_segment, threshold, salt,
                                "contactar esta semana (Cobranza)")
    churn_segment = churn_oot["region"] == PILOT_REGION
    churn_list = _build_list(churn_oot[ID_COLUMN][churn_segment], pc_oot[churn_segment],
                             churn_threshold, salt, "oferta de retencion (Retencion)")
    return PilotResult(metrics, early_warning, churn_list, threshold, churn_threshold, kept)


def _build_list(ids, score, threshold, salt, action) -> list[dict]:
    decile = deciles(score)
    rows = [
        {"client_key": pseudonymize(str(i), salt), "probability": round(float(p), 4),
         "decile": int(d), "action": action if p >= threshold else "seguimiento normal"}
        for i, p, d in zip(ids, score, decile)
    ]
    return sorted(rows, key=lambda row: (-row["probability"], row["client_key"]))
