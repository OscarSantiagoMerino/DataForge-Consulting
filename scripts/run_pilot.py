"""Sprint 6 increment (S6-01): controlled pilot with synthetic data and fixed seeds.

Usage: python scripts/run_pilot.py [output_dir]

Writes pilot_metrics.csv, early_warning_list.csv and churn_list.csv. The metrics
are prototype results on synthetic data; the validation on FinBank data and the
business acceptance remain pending.
"""
import csv
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finbank.pilot import PILOT_REGION, run_pilot  # noqa: E402


def write_csv(path: Path, rows: list[dict]) -> str:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def main(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run_pilot()
    print(f"1. Delinquency model: {len(result.variables_used)} variables from the feature dictionary")
    for row in result.metrics:
        status = "" if row["meets_target"] == "" else (" meets" if row["meets_target"] else " BELOW")
        target = f" (target {row['target']}{status})" if row["target"] != "" else ""
        print(f"   {row['model']:<11} {row['metric']:<42} {row['value']}{target}")
    flagged = sum(r["action"] != "seguimiento normal" for r in result.early_warning)
    churn_flagged = sum(r["action"] != "seguimiento normal" for r in result.churn_list)
    print(f"2. Controlled segment '{PILOT_REGION}': {len(result.early_warning)} credit clients, "
          f"{flagged} on the early warning list (cut-off {result.delinquency_threshold})")
    print(f"3. Preferential clients in the segment: {len(result.churn_list)}, "
          f"{churn_flagged} for retention (cut-off {result.churn_threshold})")
    hashes = {
        "pilot_metrics.csv": write_csv(output_dir / "pilot_metrics.csv", result.metrics),
        "early_warning_list.csv": write_csv(output_dir / "early_warning_list.csv",
                                            result.early_warning),
        "churn_list.csv": write_csv(output_dir / "churn_list.csv", result.churn_list),
    }
    for name, digest in hashes.items():
        print(f"   {name}: sha256 {digest}")
    print("Prototype results on synthetic data. FinBank validation and acceptance pending.")
    print(f"Outputs written to {output_dir}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("reports/pilot"))
