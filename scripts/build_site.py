"""Build the Corte 3 website (C3-01) from the same data as the report and the deck.

Usage: python scripts/build_site.py [output_dir]          (default: reports/site)
       python scripts/build_site.py --deploy              (build and publish to the gh-pages branch)

The page is site/index.html with the data embedded as JSON, so it works from
GitHub Pages and from a local file alike. Downloads are copied next to it.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import corte3_data as data  # noqa: E402
from finbank.models import recall_precision  # noqa: E402
from finbank.pilot import (DELINQUENCY_COSTS, OUT_OF_TIME_SEED, PILOT_REGION,  # noqa: E402
                           fit_delinquency_model)
from finbank.sample import generate_sample  # noqa: E402
from finbank.schema import DPD_COLUMN  # noqa: E402
from finbank.targets import delinquency_targets  # noqa: E402

ROOT = data.ROOT
TEMPLATE = ROOT / "site/index.html"
DOCS = ROOT / "docs/corte3"
DOWNLOADS = [f"{data.REPORT_NAME}.pdf", f"{data.DECK_NAME}.pdf",
             f"{data.DECK_NAME}.pptx", "Guion_Sustentacion.md"]
REPO = "https://github.com/OscarSantiagoMerino/DataForge-Consulting"


def delinquency_curve() -> list[dict]:
    """Recall, precision, net benefit and list size of the delinquency prototype by cut-off."""
    fitted = fit_delinquency_model()
    oot = generate_sample(5000, seed=OUT_OF_TIME_SEED)
    target = delinquency_targets(oot[DPD_COLUMN])["default_30d"]
    score = fitted.score(oot)
    observed = ~np.isnan(target)
    segment = oot["region"] == PILOT_REGION
    curve = []
    for cut in np.round(np.arange(0.02, 0.41, 0.01), 2):
        recall, precision = recall_precision(target[observed], score[observed], cut)
        curve.append({"cut": float(cut), "recall": round(recall, 4), "precision": round(precision, 4),
                      "benefit": round(DELINQUENCY_COSTS.net_benefit(target[observed], score[observed], cut)
                                       / 1e6, 3),
                      "listed": int((score[segment] >= cut).sum())})
    return curve


def churn_curve() -> list[dict]:
    """Same as corte3_data.churn_curve, plus the size of the retention list in the pilot segment."""
    from finbank.churn import CHURN_CATEGORICAL, CHURN_NUMERIC, CHURN_TARGET, generate_churn_sample
    from finbank.models import FeatureEncoder, LogisticModel
    from finbank.pilot import CHURN_COSTS, DEVELOPMENT_SEED
    dev = generate_churn_sample(4000, seed=DEVELOPMENT_SEED)
    oot = generate_churn_sample(4000, seed=OUT_OF_TIME_SEED)
    encoder = FeatureEncoder(CHURN_NUMERIC, CHURN_CATEGORICAL).fit(dev)
    model = LogisticModel(penalty=1.0).fit(encoder.transform(dev), dev[CHURN_TARGET])
    score = model.predict_proba(encoder.transform(oot))
    segment = oot["region"] == PILOT_REGION
    curve = []
    for cut in np.round(np.arange(0.04, 0.41, 0.01), 2):
        recall, precision = recall_precision(oot[CHURN_TARGET], score, cut)
        curve.append({"cut": float(cut), "recall": round(recall, 4), "precision": round(precision, 4),
                      "benefit": round(CHURN_COSTS.net_benefit(oot[CHURN_TARGET], score, cut) / 1e6, 3),
                      "listed": int((score[segment] >= cut).sum())})
    return curve


def payload() -> dict:
    m = data.compute()
    pm = m["pilot_metrics"]
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    items = {it["id"]: it for it in m["s6_items"]}
    prs = {g["id"]: g["pr"] for g in m["github"] if g["pr"]}
    return {
        "meta": {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "sha": sha,
                 "repo": REPO},
        "kpi": {"s6_done": m["s6_done"], "s6_committed": m["s6_committed"],
                "points_total": m["points_done_total"], "velocity_avg": m["velocity_avg_s1_s5"],
                "cost_dev": m["cost_deviation"], "actual_total": m["actual_total"],
                "base_total": m["base_total"], "reserve": data.RESERVE, "authorized": data.AUTHORIZED,
                "s2_actual": m["s2_cum_actual"], "s2_base": m["s2_cum_base"], "eac_s6": m["eac_at_s6_start"],
                "throughput": m["throughput"], "cycle_avg": m["cycle_avg"], "blocked_days": m["blocked_days"],
                "wip_max": m["wip_max"], "ew_flagged": m["ew_flagged"], "ew_total": m["ew_total"],
                "churn_flagged": m["churn_flagged"], "churn_total": m["churn_total"],
                "oot_sample": m["pilot_samples"]["auc_out_of_time_default_30d"],
                "oot_rate": m["pilot_rates"]["auc_out_of_time_default_30d"]},
        "pilot": pm,
        "sprints": [{k: s[k] for k in ("sprint", "weeks", "dates_scenario", "goal", "committed", "done",
                                       "goal_met", "label")} for s in m["sprints"]],
        "backlog": m["backlog"],
        "s6": [{**b, "issue": int(items[b["id"]]["github_issue"]), "pr": prs.get(b["id"], "")}
               for b in m["s6_backlog"]],
        "burndown": m["burndown"],
        "daily": m["daily"],
        "milestones": m["milestones"],
        "budget_sprint": m["budget_by_sprint"],
        "budget_item": m["budget_by_item"],
        "acceptance": m["acceptance"],
        "retro": m["retro"],
        "github": m["github"],
        "monitoring": m["monitoring"],
        "churn_curve": churn_curve(),
        "delinquency_curve": delinquency_curve(),
        "downloads": DOWNLOADS,
    }


def build(out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload(), ensure_ascii=False, default=float).replace("</", "<\\/")
    html = (TEMPLATE.read_text(encoding="utf-8")
            .replace("__REPORT_NAME__", data.REPORT_NAME)
            .replace("__DECK_NAME__", data.DECK_NAME)
            .replace("__GROUP_NUMBER__", str(data.GROUP_NUMBER))
            .replace("/*__DATA__*/null", blob))
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    files = out / "files"
    files.mkdir(exist_ok=True)
    for name in DOWNLOADS:
        shutil.copyfile(DOCS / name, files / name)
    return out / "index.html"


def deploy(out: Path) -> None:
    """Publish the built site as the only content of the gh-pages branch."""
    remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True,
                            text=True, check=True).stdout.strip()
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "pages"
        shutil.copytree(out, work)

        def git(*args):
            subprocess.run(["git", *args], cwd=work, check=True)

        git("init", "-q", "-b", "gh-pages")
        for key in ("user.name", "user.email"):
            value = subprocess.run(["git", "config", key], cwd=ROOT, capture_output=True, text=True).stdout.strip()
            git("config", key, value)
        git("add", "-A")
        git("commit", "-q", "-m", f"C3-01 Publish site built from {sha}")
        git("push", "-q", "-f", remote, "gh-pages")
    print(f"Published to gh-pages from {sha}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    target = Path(args[0]) if args else ROOT / "reports/site"
    page = build(target)
    print(f"Site built: {page}")
    if "--deploy" in sys.argv:
        deploy(target)
