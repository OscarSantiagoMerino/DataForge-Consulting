# FinBank Predictive Analytics Program

[![CI](https://github.com/OscarSantiagoMerino/DataForge-Consulting/actions/workflows/ci.yml/badge.svg)](https://github.com/OscarSantiagoMerino/DataForge-Consulting/actions/workflows/ci.yml)

Project GMAC-FB-2026-01. DataForge Consulting for FinBank S.A., Vice Presidency of Risk
and Analytics. Second term: Sprints 1 and 2 run with Scrum and XP.

This repository holds the increment delivered at the end of Sprint 2: the data
foundation for the delinquency model at 30 and 60 days (objective O1 of the Charter).

## What it does

```
anonymized sample -> validation rules -> quality report -> feature dictionary v1 -> targets 30/60
```

| Module | Backlog item | Purpose |
|---|---|---|
| `src/finbank/schema.py` | T-05.2 | The 22 candidate variables, with description, valid values and business owner |
| `src/finbank/sample.py` | T-05.0 | Anonymized synthetic sample with the agreed layout (response to risk R1) |
| `src/finbank/validation.py` | T-05.6 | Integrity rules: ranges, categories, identifiers, no personal data (Ley 1581) |
| `src/finbank/quality.py` | T-05.1, T-05.2 | Completeness per variable, exclusion below 80% (risk R2), feature dictionary |
| `src/finbank/targets.py` | T-05.4 | `default_30d` and `default_60d` |

The sample is synthetic. No record corresponds to a real client.

## Run it

```bash
python -m venv .venv
.venv/Scripts/activate        # Linux and macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest -v
python scripts/run_pipeline.py
```

Expected output of the pipeline:

```
1. Sample loaded and validated: 5,000 clients, 0 rule violations
2. Quality report: 22 candidate variables, 4 excluded below 80% completeness
     - digital_channel_share: 54.7%
     - education_level: 65.3%
     - dependents: 72.1%
     - housing_type: 60.9%
3. Feature dictionary v1: 18 variables ready for business validation
4. Target default_30d: event rate 5.85%
4. Target default_60d: event rate 2.37%
```

The quality report and the dictionary are written to `reports/` as CSV.

## How we work

- `main` is protected. One branch per backlog item, one pull request, approval by a member
  who did not write the change, CI green before merging.
- Rules are written as failing tests first.
- Business rules are written in pairs. The commit carries `Co-authored-by:`.
- Definition of Done: reproducible from this repository, documented, tests green in CI,
  pull request approved by a peer, validated by the business owner, shown in the Sprint Review.

## Team

Daniel Felipe Martínez Hernández, Rafael Alejandro Baracaldo Doikov (Product Owner),
Oscar Santiago Merino Suárez (Scrum Master). Escuela Colombiana de Ingeniería Julio Garavito, GMAC.
