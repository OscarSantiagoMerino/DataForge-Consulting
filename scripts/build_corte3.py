"""Build the Corte 3 deliverables from docs/corte3/data and the repository code.

Usage: python scripts/build_corte3.py [--skip-pdf-export]

Steps
1. Run the tests, the pipeline, the pilot and the monitoring demo; keep their
   real output in docs/corte3/evidence/.
2. Compute every figure and table once (scripts/corte3_data.py) and draw the charts.
3. Write the LaTeX tables and number macros, compile the final report.
4. Build the editable PPTX with speaker notes and export it to PDF with
   PowerPoint (Windows); write the speaking script.
5. Check page counts and render page previews to reports/preview/ for review.

Requires: requirements-corte3.txt and a LaTeX distribution with pdflatex.
"""
import argparse
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import corte3_data as data  # noqa: E402
from corte3_data import es, pct  # noqa: E402

ROOT = data.ROOT
OUT = ROOT / "docs/corte3"
EVIDENCE = OUT / "evidence"
REPORT_DIR = OUT / "informe"
GENERATED = REPORT_DIR / "generated"
REPORT_NAME = "Informe_Final_FinBank_GrupoX"
DECK_NAME = "Presentacion_FinBank_GrupoX"


# ---------------------------------------------------------------- evidence
def run(command: list[str]) -> str:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                            errors="replace")
    text = result.stdout + result.stderr
    if result.returncode:
        raise SystemExit(f"Command failed: {' '.join(command)}\n{text[-4000:]}")
    return text


def evidence() -> dict:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    sha = run(["git", "rev-parse", "--short", "HEAD"]).strip()
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = (f"# commit {sha} ({branch}) · {stamp} · Python {platform.python_version()} · "
              f"{platform.system()} {platform.release()}\n")
    py = sys.executable
    outputs = {
        "tests.txt": ("python -m pytest -v", [py, "-m", "pytest", "-v"]),
        "pipeline.txt": ("python scripts/run_pipeline.py reports/c3",
                         [py, "scripts/run_pipeline.py", "reports/c3"]),
        "pilot.txt": ("python scripts/run_pilot.py reports/c3", [py, "scripts/run_pilot.py", "reports/c3"]),
        "monitoring.txt": ("python scripts/run_monitoring.py reports/c3",
                           [py, "scripts/run_monitoring.py", "reports/c3"]),
    }
    texts = {}
    for name, (label, command) in outputs.items():
        text = run(command)
        texts[name] = text
        (EVIDENCE / name).write_text(f"{header}$ {label}\n{text}", encoding="utf-8")
    for name in ("pilot_metrics.csv", "monitoring_report.csv"):
        shutil.copyfile(ROOT / "reports/c3" / name, EVIDENCE / name)
    passed = re.search(r"(\d+) passed", texts["tests.txt"])
    return {"sha": sha, "branch": branch, "stamp": stamp, "tests_passed": int(passed.group(1)),
            "pilot_output": texts["pilot.txt"], "monitoring_output": texts["monitoring.txt"],
            "python": platform.python_version()}


# ---------------------------------------------------------------- LaTeX
def tex(value) -> str:
    text = str(value)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("{", r"\{"), ("}", r"\}"), ("_", r"\_\allowbreak{}"),
                 ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}"), ("→", r"$\rightarrow$"), ("≥", r"$\geq$"),
                 ("≤", r"$\leq$"), ("−", "-")):
        text = text.replace(a, b)
    return text


def table(rows: list[list], spec: str, header: list[str], size: str = r"\small") -> str:
    lines = [size, r"\begin{tabularx}{\linewidth}{" + spec + "}", r"\toprule",
             " & ".join(rf"\textbf{{{tex(h)}}}" for h in header) + r" \\", r"\midrule"]
    lines += [" & ".join(str(c) for c in row) + r" \\" for row in rows]
    lines += [r"\bottomrule", r"\end{tabularx}"]
    return "\n".join(lines) + "\n"


def write_latex(m: dict, ev: dict) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    pm = m["pilot_metrics"]
    mon = m["monitoring"]
    alert_week = next(r["week"] for r in mon if r["psi_top_variable_status"] == "alerta")
    flag_week = next(r["week"] for r in mon if r["retraining_flag"])
    macros = {
        "VelMedia": es(m["velocity_avg_s1_s5"]), "VelMediaTotal": es(m["velocity_avg_all"], 2),
        "PuntosTotal": m["points_done_total"], "SseisComp": m["s6_committed"], "SseisDone": m["s6_done"],
        "SseisPend": m["s6_committed"] - m["s6_done"], "Throughput": m["throughput"],
        "CicloMedio": es(m["cycle_avg"], 2), "DiasBloqueo": m["blocked_days"], "WIPMax": m["wip_max"],
        "BaseTotal": es(m["base_total"]), "GastoTotal": es(m["actual_total"]),
        "DesvCosto": tex(pct(m["cost_deviation"])), "DesvSdos": tex(pct(m["s2_deviation"])),
        "GastoSdos": es(m["s2_cum_actual"]), "BaseSdos": es(m["s2_cum_base"]),
        "EACSseis": es(m["eac_at_s6_start"]), "DesvScinco": tex(pct(m["deviation_at_s5"])),
        "NoEjecutado": es(m["unspent_envelope"]), "Reserva": es(data.RESERVE),
        "Autorizado": es(data.AUTHORIZED, 0),
        "AUCtreinta": es(pm["auc_out_of_time_default_30d"], 4),
        "AUCsesenta": es(pm["auc_out_of_time_default_60d"], 4),
        "AUCchurn": es(pm["auc_out_of_time_churn_3m"], 4),
        "RecallOp": es(pm["recall_at_operating_threshold"], 4),
        "RecallCosto": es(pm["recall_at_cost_only_threshold"], 4),
        "PrecOp": es(pm["precision_at_operating_threshold"], 4),
        "PrecCosto": es(pm["precision_at_cost_only_threshold"], 4),
        "CorteOp": es(pm["cutoff_operating_threshold"], 2), "CorteCosto": es(pm["cutoff_cost_only_threshold"], 2),
        "CorteMora": es(pm["cutoff_delinquency_threshold"], 2),
        "BenefOp": es(pm["net_benefit_cop_at_operating_threshold"] / 1e6, 2),
        "BenefCosto": es(pm["net_benefit_cop_at_cost_only_threshold"] / 1e6, 2),
        "BenefDif": es((pm["net_benefit_cop_at_cost_only_threshold"]
                        - pm["net_benefit_cop_at_operating_threshold"]) / 1e6, 2),
        "MuestraOOT": es(m["pilot_samples"]["auc_out_of_time_default_30d"], 0),
        "TasaMora": tex(pct(m["pilot_rates"]["auc_out_of_time_default_30d"])),
        "TasaChurn": tex(pct(m["pilot_rates"]["auc_out_of_time_churn_3m"])),
        "EWTotal": es(m["ew_total"], 0), "EWFlag": m["ew_flagged"],
        "ChurnTotal": es(m["churn_total"], 0), "ChurnFlag": m["churn_flagged"],
        "SemAlerta": alert_week, "SemReentreno": flag_week,
        "PSIbureau": es(mon[alert_week - 1]["psi_top_variable"], 3),
        "AUCbase": es(mon[0]["auc_baseline"], 3), "AUCsemReentreno": es(mon[flag_week - 1]["auc_30d"], 3),
        "Tests": ev["tests_passed"], "SHA": ev["sha"], "Rama": tex(ev["branch"]),
        "Generado": tex(ev["stamp"]), "PyVer": ev["python"],
    }
    (GENERATED / "macros.tex").write_text(
        "\n".join(rf"\newcommand{{\{k}}}{{{v}}}" for k, v in macros.items()) + "\n", encoding="utf-8")

    def write(name, content):
        (GENERATED / f"{name}.tex").write_text(content, encoding="utf-8")

    label_short = {"antecedente del escenario (Corte 2)": "Antecedente",
                   "reconstrucción del Corte 3": "Reconstrucción C3",
                   "simulación del Corte 3": "Simulación C3"}
    write("tab_sprints", table(
        [[s["sprint"], s["weeks"], tex(s["goal"]), s["committed"], s["done"],
          es(s["completion"] * 100, 0) + r"\,\%", s["goal_met"], label_short[s["label"]]]
         for s in m["sprints"]],
        r"l c X r r r l l", ["Sprint", "Sem.", "Objetivo del sprint", "Comp.", "Hecho", "Cumpl.",
                             "Meta", "Rótulo"], r"\footnotesize"))
    write("tab_trace", table(
        [[b["sprint"], b["id"], tex(b["item"]), b["points"], b["objective"], b["milestone"],
          tex(b["state"])] for b in m["backlog"] if b["sprint"] in ("S3", "S4", "S5")],
        r"l l X r l l l", ["Sprint", "ID", "Ítem", "Pts", "Obj.", "Hito", "Estado"], r"\footnotesize"))
    items = {it["id"]: it for it in m["s6_items"]}
    write("tab_backlog_s6", table(
        [[b["id"], tex(b["item"]), b["points"], tex(b["owner"]), tex(b["business_owner"]),
          tex(b["dependency"]), b["objective"], rf"\#{int(items[b['id']]['github_issue'])}",
          tex(b["state"])] for b in m["s6_backlog"]],
        r"l X r p{1.5cm} p{1.7cm} p{2.3cm} p{1.1cm} l p{1.9cm}",
        ["ID", "Historia", "Pts", "Resp.", "Negocio", "Dependencia", "Obj.", "Issue", "Estado (escenario)"],
        r"\scriptsize"))
    write("tab_daily", table(
        [[f"D{d['day']}", tex(d["date_scenario"]), tex(d["event_type"]), tex(d["item"]),
          tex(d["entry"])] for d in m["daily"]],
        r"l l l l X", ["Día", "Fecha (esc.)", "Tipo", "Ítem", "Registro (simulado)"], r"\scriptsize"))
    write("tab_burndown", table(
        [[b["day"], es(b["ideal"], 1), b["remaining"], tex(b["closed"].replace("|", ", ")) or "—",
          b["wip"], b["blocked"]] for b in m["burndown"]],
        r"r r r X r r", ["Día", "Ideal", "Pendiente", "Ítems que cumplen la DoD ese día", "WIP", "Bloq."],
        r"\footnotesize"))
    ct = m["cycle_times"]
    write("tab_flow", table(
        [["Velocidad S6 (puntos que cumplen la DoD)", f"{m['s6_done']} de {m['s6_committed']}",
          "Suma de puntos de ítems Done al cierre"],
         ["Velocidad media S1--S5", es(m["velocity_avg_s1_s5"]), "Base de la capacidad de S6"],
         ["Throughput S6 (ítems terminados)", m["throughput"], "Conteo de ítems Done"],
         ["Tiempo de ciclo medio", f"{es(m['cycle_avg'], 2)} días",
          tex(", ".join(f"{k}: {v}" for k, v in ct.items()))],
         ["Días bloqueados", m["blocked_days"], "S6-01, D3--D5 (ambiente de TI)"],
         ["WIP máximo en In Progress", f"{m['wip_max']} (límite 3)", "Día 7"],
         ["Cambios de alcance", "1 (fuera del sprint)", "US-10 al Product Backlog (R6)"]],
        r"l l X", ["Métrica", "Valor", "Cálculo / nota"], r"\footnotesize"))
    write("tab_milestones", table(
        [[ms["id"], tex(ms["milestone"]), ms["objective"], ms["base_week"], ms["scenario_week"],
          (f"+{ms['deviation']}" if ms["deviation"] > 0 else "0"), tex(ms["condition"]),
          tex(ms["evidence"])] for ms in m["milestones"]],
        r"l p{2.6cm} l r r r X X", ["Hito", "Nombre", "Obj.", "Base", "Esc.", "Desv.", "Condición",
                                     "Evidencia"], r"\scriptsize"))
    write("tab_budget_sprint", table(
        [[b["sprint"], es(b["base"]), es(b["actual"]), es(b["cum_base"]), es(b["cum_actual"]),
          tex(pct(b["deviation"])), label_short[b["label"]]] for b in m["budget_by_sprint"]]
        + [[r"\textbf{Total}", rf"\textbf{{{es(m['base_total'])}}}", rf"\textbf{{{es(m['actual_total'])}}}",
            "", "", rf"\textbf{{{tex(pct(m['cost_deviation']))}}}", ""]],
        r"l r r r r r X", ["Sprint", "Base", "Gasto", "Base acum.", "Gasto acum.", "Desv. acum.", "Rótulo"],
        r"\footnotesize"))
    write("tab_budget_item", table(
        [[tex(b["item"]), es(b["base"]), es(b["actual"]), tex(pct(b["deviation"], 1))]
         for b in m["budget_by_item"]]
        + [["Reserva de contingencia (no asignada a sprints)", es(data.RESERVE), "0,0",
            "No liberada"],
           [r"\textbf{Total autorizado}", rf"\textbf{{{es(data.AUTHORIZED)}}}",
            rf"\textbf{{{es(m['actual_total'])}}}",
            rf"\textbf{{No ejecutado: {es(m['unspent_envelope'])}}}"]],
        r"X r r r", ["Rubro del Charter (COP millones)", "Base", "Gasto", "Desviación"], r"\footnotesize"))
    write("tab_retro", table(
        [[r["sprint"], tex(r["action"]), r["owner"], tex(r["follow_up"]), tex(r["state"])]
         for r in m["retro"]],
        r"l X l l p{3.2cm}", ["De", "Acción de mejora", "Resp.", "Seguimiento", "Estado"], r"\footnotesize"))
    write("tab_acceptance", table(
        [[tex(a["item"]), tex(a["criterion"]), tex(a["scenario_state"]), tex(a["real_state"]),
          tex(a["who_resolves"])] for a in m["acceptance"]],
        r"l X p{2.6cm} p{3.1cm} p{2.6cm}",
        ["Ítem", "Criterio", "Escenario", "Estado real", "Quién lo resuelve"], r"\scriptsize"))
    write("tab_acceptance_s6", table(
        [[tex(a["item"]), tex(a["criterion"]), tex(a["scenario_state"]), tex(a["technical_evidence"])]
         for a in m["acceptance"] if a["scope"] == "Historia"],
        r"l X p{3cm} X", ["Historia", "Criterio de aceptación", "Escenario", "Evidencia técnica"],
        r"\scriptsize"))
    write("tab_objectives", table(
        [[tex(a["item"]), tex(a["criterion"]), tex(a["scenario_state"]), tex(a["real_state"])]
         for a in m["acceptance"] if a["scope"] == "Objetivo"],
        r"l X X p{3.4cm}", ["Obj.", "Medida de éxito (Charter)", "Resultado en el escenario / prototipo",
                            "Estado real"], r"\footnotesize"))
    gh_rows = []
    for g in m["github"]:
        gh_rows.append([g["id"], rf"\href{{{g['issue_url']}}}{{\#{g['issue']}}}", tex(g["board_column"]),
                        rf"\href{{{g['pr_url']}}}{{\#{g['pr']}}}" if g["pr"] else "—",
                        rf"\texttt{{{tex(g['branch'])}}}", tex(g["ci"].lower() or "—"),
                        tex(g["approved_by"] or "pendiente"), tex(g["merge_sha"] or "pendiente")])
    write("tab_github", table(
        gh_rows, r"l l l l X l l l",
        ["ID", "Issue", "Columna", "PR", "Rama", "CI", "Aprobación", "Merge"], r"\scriptsize"))
    rows = []
    names = {"auc_out_of_time_default_30d": "AUC fuera de tiempo, mora 30 d",
             "auc_out_of_time_default_60d": "AUC fuera de tiempo, mora 60 d",
             "auc_out_of_time_churn_3m": "AUC fuera de tiempo, churn 3 meses",
             "recall_at_operating_threshold": "Recall churn, umbral operativo",
             "precision_at_operating_threshold": "Precisión churn, umbral operativo",
             "net_benefit_cop_at_operating_threshold": "Beneficio neto churn, umbral operativo (COP)",
             "recall_at_cost_only_threshold": "Recall churn, umbral de solo costo",
             "precision_at_cost_only_threshold": "Precisión churn, umbral de solo costo",
             "net_benefit_cop_at_cost_only_threshold": "Beneficio neto churn, umbral de solo costo (COP)",
             "cutoff_operating_threshold": "Umbral operativo churn (mayor beneficio con recall ≥ 0,60)",
             "cutoff_cost_only_threshold": "Umbral churn de solo costo",
             "cutoff_delinquency_threshold": "Umbral de mora (máximo beneficio)"}
    for row in m["pilot"].metrics:
        value = row["value"]
        if "net_benefit" in row["metric"]:
            shown = es(value, 0)
        elif "cutoff" in row["metric"]:
            shown = es(value, 2)
        else:
            shown = es(value, 4)
        target = "" if row["target"] == "" else ("≥ " + es(row["target"], 2))
        rows.append([tex(names.get(row["metric"], row["metric"])), shown, tex(target),
                     es(row["sample"], 0)])
    write("tab_pilot", table(rows, r"X r l r", ["Métrica (prototipo, datos sintéticos)", "Valor",
                                                "Meta", "n"], r"\footnotesize"))
    write("tab_monitoring", table(
        [[r["week"], es(r["psi_score"], 3), tex(r["psi_score_status"]), tex(r["top_variable"]),
          es(r["psi_top_variable"], 3), es(r["auc_30d"], 3), es(r["auc_drop"], 3),
          "sí" if r["retraining_flag"] else "no"] for r in mon],
        r"r r l X r r r l", ["Sem.", "PSI score", "Estado", "Variable con mayor PSI", "PSI var.",
                             "AUC 30 d", "Caída", "Reentrenar"], r"\footnotesize"))


def compile_report() -> Path:
    engine = shutil.which("pdflatex")
    if engine is None:
        raise SystemExit("pdflatex not found: install MiKTeX or TeX Live")
    build = ROOT / "reports/latex-c3"
    build.mkdir(parents=True, exist_ok=True)
    source = REPORT_DIR / f"{REPORT_NAME}.tex"
    command = [engine, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
               f"-output-directory={build}", source.name]
    for _ in range(2):
        result = subprocess.run(command, cwd=REPORT_DIR, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        if result.returncode:
            raise SystemExit(result.stdout[-6000:])
    log = (build / f"{REPORT_NAME}.log").read_text(encoding="utf-8", errors="replace")
    overfull = [float(v) for v in re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", log)]
    if any(v > 2 for v in overfull):
        print(f"WARNING overfull boxes (pt): {[v for v in overfull if v > 2]}")
    target = OUT / f"{REPORT_NAME}.pdf"
    shutil.copyfile(build / f"{REPORT_NAME}.pdf", target)
    return target


# ---------------------------------------------------------------- checks
def preview(pdf: Path, prefix: str) -> int:
    import pymupdf
    folder = ROOT / "reports/preview"
    folder.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf)
    for page in doc:
        page.get_pixmap(dpi=70).save(folder / f"{prefix}_{page.number + 1:02d}.png")
    return doc.page_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-pdf-export", action="store_true",
                        help="build the PPTX but do not export it to PDF with PowerPoint")
    args = parser.parse_args()
    ev = evidence()
    print(f"1. Evidence: {ev['tests_passed']} tests passed at {ev['sha']}")
    m = data.compute()
    data.figures(m)
    print(f"2. Figures: {len(list(data.FIGURES.glob('*.png')))} charts in {data.FIGURES.relative_to(ROOT)}")
    write_latex(m, ev)
    report = compile_report()
    print(f"3. Report: {report.relative_to(ROOT)} ({preview(report, 'informe')} pages)")
    import corte3_slides
    deck = corte3_slides.build(m, ev, OUT / f"{DECK_NAME}.pptx")
    guion = corte3_slides.write_script(m, OUT / "Guion_Sustentacion.md")
    print(f"4. Deck: {deck.relative_to(ROOT)}; script: {guion.relative_to(ROOT)}")
    if not args.skip_pdf_export:
        pdf = corte3_slides.export_pdf(deck, OUT / f"{DECK_NAME}.pdf")
        print(f"   PDF: {pdf.relative_to(ROOT)} ({preview(pdf, 'presentacion')} pages)")
    print("Previews in reports/preview/")


if __name__ == "__main__":
    main()
