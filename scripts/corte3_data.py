"""Single source for the Corte 3 figures and tables.

Everything the audience sees (report tables, slide tables, charts) is computed
here from docs/corte3/data/*.csv and from the code of the repository (pilot and
monitoring), so the report and the deck cannot disagree.
"""
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finbank.churn import (CHURN_CATEGORICAL, CHURN_NUMERIC, CHURN_TARGET,  # noqa: E402
                           generate_churn_sample)
from finbank.models import FeatureEncoder, LogisticModel, recall_precision  # noqa: E402
from finbank.monitoring import simulate_weeks  # noqa: E402
from finbank.pilot import (CHURN_COSTS, DEVELOPMENT_SEED, OUT_OF_TIME_SEED,  # noqa: E402
                           fit_delinquency_model, run_pilot)

DATA = ROOT / "docs/corte3/data"
FIGURES = ROOT / "docs/corte3/figures"

AUTHORIZED = 180.0  # COP millions, Charter section 6
RESERVE = 10.8
TOLERANCE = 0.05
SPRINT_DAYS = 10

COLORS = {"navy": "#1F3A5F", "teal": "#2A9D8F", "amber": "#E9A23B", "red": "#C8553D",
          "gray": "#6B7280", "light": "#E5E7EB", "ink": "#111827"}


def read(name: str) -> list[dict]:
    with (DATA / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def num(value: str) -> float | None:
    return float(value) if value not in ("", None) else None


def es(value: float, decimals: int = 1) -> str:
    """Spanish number format: thousands with '.', decimals with ','."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: float, decimals: int = 2) -> str:
    return f"{es(value * 100, decimals)} %"


# ---------------------------------------------------------------- metrics
def compute() -> dict:
    m: dict = {}
    sprints = read("sprints.csv")
    for s in sprints:
        s["committed"] = int(s["committed"])
        s["done"] = int(s["done"])
        s["completion"] = s["done"] / s["committed"]
    m["sprints"] = sprints
    first5 = [s["done"] for s in sprints[:5]]
    m["velocity_avg_s1_s5"] = sum(first5) / 5
    m["velocity_avg_all"] = sum(s["done"] for s in sprints) / len(sprints)
    m["points_done_total"] = sum(s["done"] for s in sprints)

    backlog = read("backlog.csv")
    m["backlog"] = backlog
    m["s6_backlog"] = [b for b in backlog if b["sprint"] == "S6"]

    # Sprint 6 burndown and flow, from the item timeline.
    items = read("s6_items.csv")
    for it in items:
        for key in ("points", "start_day", "blocked_from", "blocked_to", "done_day", "github_issue"):
            it[key] = num(it[key])
    committed = sum(it["points"] for it in items)
    m["s6_items"] = items
    m["s6_committed"] = int(committed)
    burndown = []
    for day in range(SPRINT_DAYS + 1):
        done = sum(it["points"] for it in items if it["done_day"] is not None and it["done_day"] <= day)
        closed = [it["id"] for it in items if it["done_day"] == day]

        def blocked(it):
            return (it["blocked_from"] is not None and it["blocked_from"] <= day
                    and (it["blocked_to"] is None or day <= it["blocked_to"]))

        in_progress = [it["id"] for it in items if it["start_day"] <= day
                       and (it["done_day"] is None or day < it["done_day"]) and not blocked(it)]
        blocked_now = [it["id"] for it in items if it["start_day"] <= day and blocked(it)
                       and (it["done_day"] is None or day < it["done_day"])]
        burndown.append({"day": day, "remaining": int(committed - done),
                         "ideal": round(committed * (1 - day / SPRINT_DAYS), 2),
                         "closed": "|".join(closed), "wip": len(in_progress) if day else 0,
                         "blocked": len(blocked_now) if day else 0})
    m["burndown"] = burndown
    m["s6_done"] = int(committed - burndown[-1]["remaining"])
    done_items = [it for it in items if it["done_day"] is not None]
    m["throughput"] = len(done_items)
    m["cycle_times"] = {it["id"]: int(it["done_day"] - it["start_day"] + 1) for it in done_items}
    m["cycle_avg"] = sum(m["cycle_times"].values()) / len(done_items)
    m["blocked_days"] = sum(int(it["blocked_to"] - it["blocked_from"] + 1) for it in items
                            if it["blocked_from"] is not None and it["blocked_to"] is not None)
    m["wip_max"] = max(b["wip"] for b in burndown)
    m["daily"] = read("s6_daily.csv")

    # Milestones.
    milestones = read("milestones.csv")
    for ms in milestones:
        ms["base_week"] = int(ms["base_week"])
        ms["scenario_week"] = int(ms["scenario_week"])
        ms["deviation"] = ms["scenario_week"] - ms["base_week"]
    m["milestones"] = milestones

    # Budget.
    rows = read("budget.csv")
    for r in rows:
        r["base"] = float(r["base_cop_m"])
        r["actual"] = float(r["actual_cop_m"])
    order = [s["sprint"] for s in sprints]
    by_sprint, cum_base, cum_actual = [], 0.0, 0.0
    for sp in order:
        base = round(sum(r["base"] for r in rows if r["sprint"] == sp), 2)
        actual = round(sum(r["actual"] for r in rows if r["sprint"] == sp), 2)
        cum_base, cum_actual = round(cum_base + base, 2), round(cum_actual + actual, 2)
        by_sprint.append({"sprint": sp, "base": base, "actual": actual, "cum_base": cum_base,
                          "cum_actual": cum_actual, "deviation": (cum_actual - cum_base) / cum_base,
                          "label": next(r["label"] for r in rows if r["sprint"] == sp)})
    m["budget_by_sprint"] = by_sprint
    items_order = list(dict.fromkeys(r["item"] for r in rows))
    m["budget_by_item"] = [
        {"item": it, "base": round(sum(r["base"] for r in rows if r["item"] == it), 2),
         "actual": round(sum(r["actual"] for r in rows if r["item"] == it), 2)}
        for it in items_order
    ]
    for it in m["budget_by_item"]:
        it["deviation"] = (it["actual"] - it["base"]) / it["base"]
    m["base_total"] = by_sprint[-1]["cum_base"]
    m["actual_total"] = by_sprint[-1]["cum_actual"]
    m["cost_deviation"] = (m["actual_total"] - m["base_total"]) / m["base_total"]
    s2 = by_sprint[1]
    m["s2_cum_base"], m["s2_cum_actual"], m["s2_deviation"] = s2["cum_base"], s2["cum_actual"], s2["deviation"]
    s5 = by_sprint[4]
    m["eac_at_s6_start"] = round(s5["cum_actual"] + by_sprint[5]["base"], 2)
    m["deviation_at_s5"] = s5["deviation"]
    m["unspent_envelope"] = round(AUTHORIZED - m["actual_total"], 2)
    assert abs(m["base_total"] + RESERVE - AUTHORIZED) < 1e-6, "base + reserve must equal the Charter"
    final = next(ms for ms in milestones if ms["id"] == "M6")
    m["schedule_deviation_weeks"] = final["deviation"]
    m["schedule_deviation"] = final["deviation"] / 12

    m["acceptance"] = read("acceptance.csv")
    m["retro"] = read("retro_actions.csv")
    github = DATA / "github_log.csv"
    m["github"] = read("github_log.csv") if github.exists() else []

    # Code results (prototype on synthetic data).
    pilot = run_pilot()
    m["pilot"] = pilot
    m["pilot_metrics"] = {row["metric"]: row["value"] for row in pilot.metrics}
    m["pilot_samples"] = {row["metric"]: row["sample"] for row in pilot.metrics}
    m["pilot_rates"] = {row["metric"]: row["event_rate"] for row in pilot.metrics}
    m["ew_total"] = len(pilot.early_warning)
    m["ew_flagged"] = sum(r["action"] != "seguimiento normal" for r in pilot.early_warning)
    m["churn_total"] = len(pilot.churn_list)
    m["churn_flagged"] = sum(r["action"] != "seguimiento normal" for r in pilot.churn_list)
    m["monitoring"] = simulate_weeks(fit_delinquency_model())
    m["churn_curve"] = churn_curve()
    return m


def churn_curve() -> list[dict]:
    """Recall and net benefit of the churn prototype on the out-of-time cohort by cut-off."""
    dev = generate_churn_sample(4000, seed=DEVELOPMENT_SEED)
    oot = generate_churn_sample(4000, seed=OUT_OF_TIME_SEED)
    encoder = FeatureEncoder(CHURN_NUMERIC, CHURN_CATEGORICAL).fit(dev)
    model = LogisticModel(penalty=1.0).fit(encoder.transform(dev), dev[CHURN_TARGET])
    score = model.predict_proba(encoder.transform(oot))
    curve = []
    for cut in np.round(np.arange(0.04, 0.41, 0.01), 2):
        recall, precision = recall_precision(oot[CHURN_TARGET], score, cut)
        curve.append({"cut": float(cut), "recall": recall, "precision": precision,
                      "benefit": CHURN_COSTS.net_benefit(oot[CHURN_TARGET], score, cut) / 1e6})
    return curve


# ---------------------------------------------------------------- figures
def figures(m: dict) -> dict[str, Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": COLORS["gray"], "axes.labelcolor": COLORS["ink"],
                         "xtick.color": COLORS["ink"], "ytick.color": COLORS["ink"],
                         "axes.titleweight": "bold", "axes.titlesize": 12,
                         "svg.hashsalt": "corte3", "pdf.fonttype": 42})
    FIGURES.mkdir(parents=True, exist_ok=True)
    out: dict[str, Path] = {}

    def save(fig, name):
        path = FIGURES / f"{name}.png"
        fig.savefig(path, dpi=200, bbox_inches="tight", metadata={"Software": None})
        plt.close(fig)
        out[name] = path

    # 1. Burndown S6.
    bd = m["burndown"]
    days = [b["day"] for b in bd]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.axvspan(2.5, 5.5, color=COLORS["red"], alpha=0.08, lw=0)
    ax.text(4, 3.2, "S6-01 bloqueada\n(ambiente de TI, D3–D5)", ha="center",
            va="top", fontsize=9, color=COLORS["red"])
    ax.plot(days, [b["ideal"] for b in bd], ls="--", color=COLORS["gray"], label="Ideal")
    ax.step(days, [b["remaining"] for b in bd], where="post", color=COLORS["navy"], lw=2.4,
            label="Observado (escenario)")
    for b in bd:
        if b["closed"]:
            ax.annotate(b["closed"].replace("|", ", "), (b["day"], b["remaining"]),
                        textcoords="offset points", xytext=(4, 6), fontsize=8.5, color=COLORS["navy"])
    last = bd[-1]
    ax.annotate(f"{last['remaining']} pts pendientes\n(S6-04: firma del acta)", (10, last["remaining"]),
                textcoords="offset points", xytext=(-190, 60), fontsize=9, color=COLORS["red"],
                arrowprops={"arrowstyle": "->", "color": COLORS["red"]})
    ax.set_xticks(days)
    ax.set_xlabel("Día hábil del Sprint 6 (19–30 oct 2026, escenario)")
    ax.set_ylabel("Puntos pendientes")
    ax.set_ylim(0, m["s6_committed"] + 1.5)
    ax.set_title(f"Burndown S6: {m['s6_done']} de {m['s6_committed']} puntos cumplen la DoD")
    ax.legend(frameon=False, loc="upper right")
    save(fig, "burndown_s6")

    # 2. Velocity.
    sp = m["sprints"]
    x = np.arange(len(sp))
    fig, ax = plt.subplots(figsize=(8, 4.0))
    ax.bar(x - 0.2, [s["committed"] for s in sp], 0.4, color=COLORS["light"], label="Compromiso")
    bars = ax.bar(x + 0.2, [s["done"] for s in sp], 0.4, color=COLORS["teal"], label="Terminado (DoD)")
    for rect, s in zip(bars, sp):
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.3, str(s["done"]),
                ha="center", fontsize=9)
    ax.axhline(m["velocity_avg_s1_s5"], color=COLORS["amber"], ls=":", lw=1.8,
               label=f"Media S1–S5 = {es(m['velocity_avg_s1_s5'])}")
    ax.set_xticks(x, [f"{s['sprint']}\n{'C2' if i < 2 else 'C3'}" for i, s in enumerate(sp)])
    ax.set_ylabel("Puntos de historia")
    ax.set_ylim(0, 25)
    ax.set_title("Velocidad por sprint: compromiso frente a terminado")
    ax.legend(frameon=False, loc="upper left", ncol=3, fontsize=9)
    save(fig, "velocity")

    # 3. Budget cumulative.
    bs = m["budget_by_sprint"]
    x = np.arange(len(bs) + 1)
    base = [0] + [b["cum_base"] for b in bs]
    actual = [0] + [b["cum_actual"] for b in bs]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.fill_between(x, [v * (1 - TOLERANCE) for v in base], [v * (1 + TOLERANCE) for v in base],
                    color=COLORS["teal"], alpha=0.12, lw=0, label="Tolerancia ±5 % (Charter)")
    ax.plot(x, base, color=COLORS["gray"], ls="--", marker="o", ms=4, label="Base aprobada acumulada")
    ax.plot(x, actual, color=COLORS["navy"], lw=2.4, marker="o", ms=5, label="Gasto acumulado")
    ax.axhline(AUTHORIZED, color=COLORS["red"], lw=1.2)
    ax.text(0.1, AUTHORIZED + 2, f"Total autorizado COP {es(AUTHORIZED, 0)} M "
            f"(incluye reserva {es(RESERVE)} M, no liberada)", fontsize=9, color=COLORS["red"])
    ax.annotate(f"S2: {es(m['s2_cum_actual'])} frente a {es(m['s2_cum_base'])}",
                (2, m["s2_cum_actual"]), textcoords="offset points", xytext=(10, -22), fontsize=9)
    ax.annotate(f"Cierre: {es(m['actual_total'])} frente a {es(m['base_total'])} "
                f"({pct(m['cost_deviation'])})", (6, m["actual_total"]),
                textcoords="offset points", xytext=(-250, -10), fontsize=9,
                arrowprops={"arrowstyle": "->", "color": COLORS["navy"]})
    ax.set_xticks(x, ["Inicio"] + [b["sprint"] for b in bs])
    ax.set_ylabel("COP millones")
    ax.set_ylim(0, 200)
    ax.set_title("Presupuesto: gasto acumulado frente a la línea base del Charter")
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    save(fig, "budget_cumulative")

    # 4. Milestones.
    ms = m["milestones"]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for i, row in enumerate(reversed(ms)):
        color = COLORS["red"] if row["deviation"] > 0 else COLORS["teal"]
        ax.plot([row["base_week"], row["scenario_week"]], [i, i], color=color, lw=3, alpha=0.6)
        ax.scatter(row["base_week"], i, s=60, color="white", edgecolor=COLORS["gray"], zorder=3)
        ax.scatter(row["scenario_week"], i, s=70, color=color, zorder=4)
        dev = f"+{row['deviation']} sem" if row["deviation"] > 0 else "a tiempo"
        if row["condition"].startswith("Condicionada"):
            dev, color = "a tiempo, condicionada", COLORS["amber"]
        ax.text(max(row["base_week"], row["scenario_week"]) + 0.3, i, dev, va="center",
                fontsize=9, color=color)
    ax.set_yticks(range(len(ms)), [f"{r['id']} {r['milestone']}" for r in reversed(ms)], fontsize=9)
    ax.set_xticks(range(0, 13, 2))
    ax.set_xlim(0, 15.5)
    ax.set_xlabel("Semana del proyecto (○ base del Charter, ● escenario)")
    ax.set_title("Hitos M1–M6: semana base frente a semana del escenario")
    ax.grid(axis="x", color=COLORS["light"])
    save(fig, "milestones")

    # 5. Churn trade-off.
    cv = m["churn_curve"]
    pm = m["pilot_metrics"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    cuts = [c["cut"] for c in cv]
    ax.plot(cuts, [c["recall"] for c in cv], color=COLORS["navy"], lw=2.2, label="Recall (eje izq.)")
    ax.axhline(0.60, color=COLORS["navy"], ls=":", lw=1.2)
    ax.text(0.40, 0.615, "meta O2: recall ≥ 0,60", ha="right", fontsize=9, color=COLORS["navy"])
    ax.set_ylabel("Recall fuera de tiempo")
    ax.set_xlabel("Umbral de probabilidad de churn")
    ax.set_ylim(0, 1)
    ax2 = ax.twinx()
    ax2.plot(cuts, [c["benefit"] for c in cv], color=COLORS["amber"], lw=2.2,
             label="Beneficio neto, COP M (eje der.)")
    ax2.set_ylabel("Beneficio neto (COP millones)")
    ax2.spines["top"].set_visible(False)
    for cut, label, color in ((pm["cutoff_operating_threshold"], "operativo", COLORS["teal"]),
                              (pm["cutoff_cost_only_threshold"], "solo costo", COLORS["red"])):
        ax.axvline(cut, color=color, lw=1.4)
        ax.text(cut + 0.004, 0.05, f"{label}\n{es(cut, 2)}", fontsize=9, color=color)
    lines = ax.get_lines()[:1] + ax2.get_lines()
    ax.legend(lines, [ln.get_label() for ln in lines], frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=9)
    ax.set_title("Churn: cumplir O2 cuesta beneficio neto (prototipo sintético)")
    save(fig, "churn_tradeoff")

    # 6. Monitoring.
    mon = m["monitoring"]
    weeks = [r["week"] for r in mon]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
    a1.bar(weeks, [r["psi_top_variable"] for r in mon], color=COLORS["light"], label="PSI variable con mayor cambio")
    a1.plot(weeks, [r["psi_score"] for r in mon], color=COLORS["navy"], marker="o", label="PSI del score")
    a1.axhline(0.10, color=COLORS["amber"], ls=":", lw=1.2)
    a1.axhline(0.25, color=COLORS["red"], ls=":", lw=1.2)
    a1.text(0.6, 0.26, "alerta 0,25", fontsize=8, color=COLORS["red"])
    a1.text(0.6, 0.11, "vigilar 0,10", fontsize=8, color="#8a5a00")
    a1.set_xlabel("Semana simulada")
    a1.set_title("Estabilidad (PSI)")
    a1.legend(frameon=False, fontsize=8, loc="upper left")
    a1.set_ylim(0, 0.5)
    a2.plot(weeks, [r["auc_30d"] for r in mon], color=COLORS["navy"], marker="o", label="AUC 30 d")
    base_auc = mon[0]["auc_baseline"]
    a2.axhline(base_auc, color=COLORS["gray"], ls="--", lw=1)
    a2.axhline(base_auc - 0.05, color=COLORS["red"], ls=":", lw=1.2)
    a2.text(0.8, base_auc - 0.045, "base − 0,05", fontsize=8, color=COLORS["red"])
    for r in mon:
        if r["retraining_flag"]:
            a2.scatter(r["week"], r["auc_30d"], s=120, facecolor="none", edgecolor=COLORS["red"], lw=2)
    flag_week = next(r["week"] for r in mon if r["retraining_flag"])
    a2.text(flag_week, mon[flag_week - 1]["auc_30d"] - 0.035, "reentrenar", ha="center",
            fontsize=8.5, color=COLORS["red"])
    a2.set_ylim(0.55, 0.85)
    a2.set_xlabel("Semana simulada")
    a2.set_title("Desempeño (AUC)")
    fig.suptitle("Monitoreo: cambio inyectado en la semana 4 (datos sintéticos)", fontsize=11,
                 fontweight="bold", y=1.03)
    fig.tight_layout()
    save(fig, "monitoring")
    return out
