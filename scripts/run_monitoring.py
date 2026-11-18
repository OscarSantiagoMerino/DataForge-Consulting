"""Sprint 6 increment (S6-02): weekly monitoring of the pilot model.

Usage: python scripts/run_monitoring.py [output_dir]

Six synthetic weeks; a population change is injected from week 4 to show that
the stability alert and the retraining trigger work as the runbook describes.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finbank.monitoring import MAX_DROP, PSI_ALERT, PSI_WATCH, simulate_weeks  # noqa: E402
from finbank.pilot import fit_delinquency_model  # noqa: E402


def main(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = simulate_weeks(fit_delinquency_model())
    print(f"PSI: < {PSI_WATCH} stable, {PSI_WATCH}-{PSI_ALERT} watch, >= {PSI_ALERT} alert. "
          f"Retraining: AUC down more than {MAX_DROP} for 2 consecutive weeks.")
    print("week  psi_score  status    top variable (psi)              auc_30d  drop    retrain")
    for r in rows:
        print(f"{r['week']:>4}  {r['psi_score']:>9}  {r['psi_score_status']:<8}  "
              f"{r['top_variable'] + ' (' + str(r['psi_top_variable']) + ')':<30}  "
              f"{r['auc_30d']:>7}  {r['auc_drop']:>6}  {'YES' if r['retraining_flag'] else 'no'}")
    path = output_dir / "monitoring_report.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    first_alert = next((r["week"] for r in rows if r["psi_top_variable_status"] == "alerta"), None)
    first_flag = next((r["week"] for r in rows if r["retraining_flag"]), None)
    print(f"First stability alert: week {first_alert}. Retraining flag: week {first_flag}.")
    print(f"Report written to {path}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("reports/monitoring"))
