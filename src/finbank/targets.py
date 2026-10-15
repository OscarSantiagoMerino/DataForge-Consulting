"""Delinquency target definition at 30 and 60 days (task T-05.4, objective O1)."""
import numpy as np

from finbank.schema import DPD_COLUMN

HORIZONS = (30, 60)


def delinquency_targets(max_days_past_due: np.ndarray) -> dict[str, np.ndarray]:
    """default_30d and default_60d: 1 if the client reached that many days past due.

    Accounts without an observation (too recent) keep NaN and are left out of
    training instead of being counted as good clients.
    """
    dpd = np.asarray(max_days_past_due, dtype=float)
    observed = ~np.isnan(dpd)
    if (dpd[observed] < 0).any():
        raise ValueError(f"{DPD_COLUMN} cannot be negative")
    return {
        f"default_{days}d": np.where(observed, (dpd >= days).astype(float), np.nan)
        for days in HORIZONS
    }


def event_rate(target: np.ndarray) -> float:
    return float(np.nanmean(target))
