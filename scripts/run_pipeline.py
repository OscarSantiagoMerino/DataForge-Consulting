"""Sprint 2 increment: sample -> validation -> quality report -> dictionary -> targets.

Usage: python scripts/run_pipeline.py [output_dir]
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finbank.quality import feature_dictionary, quality_report  # noqa: E402
from finbank.sample import generate_sample  # noqa: E402
from finbank.schema import COMPLETENESS_THRESHOLD, DPD_COLUMN  # noqa: E402
from finbank.targets import delinquency_targets, event_rate  # noqa: E402
from finbank.validation import assert_valid  # noqa: E402


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    table = generate_sample()
    assert_valid(table)
    print(f"1. Sample loaded and validated: {len(table[DPD_COLUMN]):,} clients, 0 rule violations")

    report = quality_report(table)
    excluded = [row for row in report if row["decision"] == "exclude"]
    write_csv(output_dir / "quality_report.csv", report)
    print(f"2. Quality report: {len(report)} candidate variables, "
          f"{len(excluded)} excluded below {COMPLETENESS_THRESHOLD:.0%} completeness")
    for row in excluded:
        print(f"     - {row['variable']}: {row['completeness']:.1%}")

    dictionary = feature_dictionary(report)
    write_csv(output_dir / "feature_dictionary.csv", dictionary)
    print(f"3. Feature dictionary v1: {len(dictionary)} variables ready for business validation")

    targets = delinquency_targets(table[DPD_COLUMN])
    for name, values in targets.items():
        print(f"4. Target {name}: event rate {event_rate(values):.2%}")
    print(f"Outputs written to {output_dir}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("reports"))
