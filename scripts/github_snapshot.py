"""Snapshot of the Corte 3 board and GitHub log, read from GitHub with the gh CLI.

Usage: python scripts/github_snapshot.py

Writes docs/corte3/data/github_log.csv and docs/corte3/TABLERO.md. Every number,
link and state comes from GitHub at the moment of the run; rerun it to refresh.
"""
import csv
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "OscarSantiagoMerino/DataForge-Consulting"
COLUMNS = ["estado:backlog", "estado:ready", "estado:in-progress", "estado:blocked",
           "estado:review", "estado:done"]
WIP_LIMIT = 3


def gh(*args) -> list | dict:
    out = subprocess.run(["gh", *args, "--repo", REPO], capture_output=True, text=True,
                         encoding="utf-8", check=True).stdout
    return json.loads(out)


def item_id(title: str) -> str:
    # Titles follow "[C3][S6][ID] name"
    parts = title.split("]")
    return parts[2].lstrip("[") if len(parts) > 3 else title


def main() -> None:
    issues = gh("issue", "list", "--state", "all", "--label", "C3", "--limit", "50", "--json",
                "number,title,state,labels,url,closedAt")
    prs = gh("pr", "list", "--state", "all", "--label", "C3", "--limit", "50", "--json",
             "number,title,state,headRefName,baseRefName,url,mergedAt,mergeCommit,body,"
             "reviews,reviewRequests,statusCheckRollup,headRefOid")
    issues.sort(key=lambda i: i["number"])
    prs.sort(key=lambda p: p["number"])

    rows = []
    for issue in issues:
        labels = [label["name"] for label in issue["labels"]]
        status = next((c for c in COLUMNS if c in labels), "sin estado")
        pattern = re.compile(rf"\b(?:Refs|Closes|Fixes)\s+#{issue['number']}\b", re.IGNORECASE)
        linked = [p for p in prs if pattern.search(p["body"] or "")]
        for pr in linked or [None]:
            checks = pr and [c.get("conclusion") or c.get("status") for c in pr["statusCheckRollup"]]
            approvals = pr and [r["author"]["login"] for r in pr["reviews"] if r["state"] == "APPROVED"]
            requested = pr and [r.get("login") or r.get("name") for r in pr["reviewRequests"]]
            rows.append({
                "id": item_id(issue["title"]),
                "issue": issue["number"],
                "issue_state": issue["state"],
                "board_column": status.replace("estado:", ""),
                "branch": pr["headRefName"] if pr else "",
                "pr": pr["number"] if pr else "",
                "pr_state": pr["state"] if pr else "",
                "head_sha": pr["headRefOid"][:7] if pr else "",
                "ci": ",".join(c or "" for c in checks) if pr else "",
                "approved_by": ",".join(approvals) if pr else "",
                "review_requested": ",".join(r for r in requested if r) if pr else "",
                "merged_at": (pr["mergedAt"] or "") if pr else "",
                "merge_sha": (pr["mergeCommit"] or {}).get("oid", "")[:7] if pr else "",
                "issue_url": issue["url"],
                "pr_url": pr["url"] if pr else "",
            })

    data = ROOT / "docs/corte3/data"
    with (data / "github_log.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Tablero del Corte 3 (vista reproducible)",
        "",
        f"Generado desde GitHub con `python scripts/github_snapshot.py` el {stamp}.",
        "Esta vista usa las etiquetas `estado:*` de las issues del milestone "
        f"[Corte 3 · S6](https://github.com/{REPO}/milestone/1). "
        "Las tarjetas del [Project de FinBank](https://github.com/users/OscarSantiagoMerino/projects/1) "
        "se actualizan en GitHub Projects.",
        "",
        "**Reglas de movimiento.** Backlog → Ready cuando cumple la Definition of Ready "
        "(criterios, estimación, responsable de negocio, sin dependencia externa pendiente). "
        f"Ready → In Progress si hay cupo (WIP máximo {WIP_LIMIT}). In Progress → Blocked con la "
        "causa y el responsable en un comentario; el Scrum Master escala en 24 horas. "
        "In Progress → Review al abrir el PR con CI. Review → Done solo cuando el PR está "
        "fusionado y la DoD se cumple, incluida la validación del responsable de negocio. "
        "La aceptación real del negocio se registra aparte (`data/acceptance.csv`).",
        "",
    ]
    for column in COLUMNS:
        members = [i for i in issues if column in [label["name"] for label in i["labels"]]]
        lines.append(f"## {column.replace('estado:', '').title()} ({len(members)})")
        lines += [f"- [#{i['number']}]({i['url']}) {i['title']}" for i in members] or ["- —"]
        lines.append("")
    in_progress = sum("estado:in-progress" in [label["name"] for label in i["labels"]] for i in issues)
    lines.append(f"WIP actual en In Progress: {in_progress} de {WIP_LIMIT}.")
    lines += ["", "## Pull requests del Corte 3", "",
              "| PR | Rama | Estado | CI (último SHA) | Aprobado por | Revisión pedida a | Merge |",
              "|---|---|---|---|---|---|---|"]
    for pr in prs:
        checks = ",".join((c.get("conclusion") or c.get("status") or "").lower()
                          for c in pr["statusCheckRollup"]) or "—"
        approvals = ",".join(r["author"]["login"] for r in pr["reviews"]
                             if r["state"] == "APPROVED") or "—"
        requested = ",".join(r.get("login") or r.get("name") or "" for r in pr["reviewRequests"]) or "—"
        merged = (pr["mergeCommit"] or {}).get("oid", "")[:7] if pr["mergedAt"] else "—"
        lines.append(f"| [#{pr['number']}]({pr['url']}) | `{pr['headRefName']}` | {pr['state']} | "
                     f"{checks} (`{pr['headRefOid'][:7]}`) | {approvals} | {requested} | {merged} |")
    (ROOT / "docs/corte3/TABLERO.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(issues)} issues, {len(prs)} PRs -> github_log.csv, TABLERO.md ({stamp})")


if __name__ == "__main__":
    main()
