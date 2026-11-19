"""Reconciliation of the Corte 3 evidence tables (docs/corte3/data).

The report and the deck are generated from these CSV files; these checks keep
them consistent with each other and with the Charter baseline.
"""
import csv
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[1] / "docs/corte3/data"


def read(name):
    with (DATA / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_every_csv_row_has_the_header_width():
    for path in DATA.glob("*.csv"):
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        assert all(len(row) == len(rows[0]) for row in rows), path.name


def test_budget_base_plus_reserve_equals_the_charter_authorization():
    base = sum(float(r["base_cop_m"]) for r in read("budget.csv"))
    assert base + 10.8 == pytest.approx(180.0)


def test_budget_base_by_item_matches_the_charter_allocation():
    charter = {"Gestión y gobierno": 27.0, "Ingeniería de datos": 45.0, "Modelado predictivo": 54.0,
               "Validación y documentación": 25.2, "Piloto, capacitación y transferencia": 18.0}
    rows = read("budget.csv")
    for item, amount in charter.items():
        assert sum(float(r["base_cop_m"]) for r in rows if r["item"] == item) == pytest.approx(amount)


def test_sprint_2_close_matches_the_historical_figures():
    rows = [r for r in read("budget.csv") if r["sprint"] in ("S1", "S2")]
    assert sum(float(r["actual_cop_m"]) for r in rows) == pytest.approx(54.8)
    assert sum(float(r["base_cop_m"]) for r in rows) == pytest.approx(56.4)


def test_final_cost_deviation_is_within_the_charter_limit():
    rows = read("budget.csv")
    base = sum(float(r["base_cop_m"]) for r in rows)
    actual = sum(float(r["actual_cop_m"]) for r in rows)
    assert abs(actual - base) / base <= 0.05


def test_sprint_points_match_the_backlog():
    backlog = read("backlog.csv")
    for sprint in read("sprints.csv"):
        items = [b for b in backlog if b["sprint"] == sprint["sprint"]]
        assert sum(int(b["points"]) for b in items) == int(sprint["committed"]), sprint["sprint"]
        assert sum(int(b["points"]) for b in items if b["state"] == "Done") == int(sprint["done"])


def test_history_of_s1_and_s2_is_preserved():
    sprints = {s["sprint"]: s for s in read("sprints.csv")}
    assert (sprints["S1"]["committed"], sprints["S1"]["done"]) == ("16", "16")
    assert (sprints["S2"]["committed"], sprints["S2"]["done"]) == ("20", "15")


def test_sprint_6_commitment_does_not_exceed_the_average_velocity():
    sprints = read("sprints.csv")
    average = sum(int(s["done"]) for s in sprints[:5]) / 5
    assert int(sprints[5]["committed"]) <= average


def test_sprint_6_timeline_agrees_with_the_backlog():
    backlog = {b["id"]: b for b in read("backlog.csv") if b["sprint"] == "S6"}
    for item in read("s6_items.csv"):
        row = backlog[item["id"]]
        assert int(item["points"]) == int(row["points"])
        assert (item["done_day"] or "") == row["done_day"]
        assert (row["state"] == "Done") == bool(item["done_day"])


def test_wip_limit_is_respected_in_sprint_6():
    items = read("s6_items.csv")
    for day in range(1, 11):
        active = 0
        for it in items:
            start, done = int(it["start_day"]), int(it["done_day"]) if it["done_day"] else 99
            blocked_from = int(it["blocked_from"]) if it["blocked_from"] else 99
            blocked_to = int(it["blocked_to"]) if it["blocked_to"] else 99
            if start <= day < done and not blocked_from <= day <= blocked_to:
                active += 1
        assert active <= 3, f"day {day}"


def test_every_daily_entry_is_labelled_as_simulated():
    assert {d["label"] for d in read("s6_daily.csv")} == {"simulado"}


def test_milestones_follow_the_charter_weeks():
    base = {m["id"]: int(m["base_week"]) for m in read("milestones.csv")}
    assert base == {"M1": 2, "M2": 4, "M3": 6, "M4": 8, "M5": 10, "M6": 12}


def test_real_acceptance_is_never_recorded_as_done():
    for row in read("acceptance.csv"):
        assert "firmad" not in row["real_state"].lower()
        assert not row["real_state"].lower().startswith("aceptad")
