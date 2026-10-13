# Sprint Review and operational demo (15 minutes)

Audience: FinBank sponsor (the professor). Have a terminal open in the repository root
with the virtual environment active, and the GitHub repository open in a browser.

| Min | Who | What | On screen |
|---|---|---|---|
| 0–2 | Rafael (Product Owner) | Sprint Goals of S1 and S2, what was committed and what closed: 16 of 16 and 15 of 20 points | Report, section 2 |
| 2–7 | Daniel | Live demo of the increment, steps below | Terminal |
| 7–9 | Oscar (Scrum Master) | Velocity and burndown; the blocked churn extract and how it was handled at the Daily Scrum | Report, section 3 |
| 9–11 | Oscar | XP evidence: one pairing commit, one pull request with review and green CI, refactoring R-01 before and after | GitHub, `docs/XP_LOG.md` |
| 11–13 | Rafael | Differences in the workflow against the first term | Report, section 7 |
| 13–15 | Daniel | Lessons learned, improvement plan, forecast for Sprint 3 and the decision asked from the sponsor | Report, sections 5 and 8 |

## Live demo (minutes 2 to 7)

Each step shows a backlog item that meets the Definition of Done.

1. **Tests green** (T-05.6). Run `pytest -v`. Sixteen rules pass.
2. **A rule catches bad data.** Run the block below. The pipeline refuses a table with a
   bureau score out of range and with a personal data column.

   ```bash
   python -c "import sys; sys.path.insert(0,'src'); from finbank.sample import generate_sample; from finbank.validation import validate; t=generate_sample(); t['bureau_score'][0]=1200; t['cedula']=t['age'].copy(); print(*validate(t), sep='\n')"
   ```

3. **Quality report, dictionary and targets** (T-05.1, T-05.2, T-05.4). Run
   `python scripts/run_pipeline.py`. Point at: 22 candidates, 4 excluded with their
   completeness, 18 variables in the dictionary, event rates of 5.85% and 2.37%.
4. **The output the business validated.** Open `reports/feature_dictionary.csv`: each
   variable has a description, valid values and a business owner.
5. **Not done.** T-05.5, churn history extract, is not shown because it is not Done. It
   returned to the Product Backlog.

## Lessons learned to defend

- The team delivered the same 15 to 16 points in both sprints. Sprint 2 fell short because
  20 points were committed and 5 of them depended on a credential owned by IT.
- A blocker that exceeds a risk response has to reach the sponsor the day it appears.
- Rules written as tests found two decisions the business had to take, on missing values
  and on unobserved accounts, before any model was trained.

## Improvement plan

1. Commit at most the average velocity, 16 points in Sprint 3.
2. Definition of Ready: an item with an ungranted external dependency does not enter a sprint.
3. The Scrum Master escalates impediments within 24 hours.
4. Two pairing sessions per sprint, rotating the driver.

## Decision asked from the sponsor

Sprint 3 takes the delinquency model (US-06, 13 points). The early warning list (US-07)
moves to Sprint 4, which then holds 23 points against a capacity of 16, so milestone M4
in week 8 is at risk. Options: release the IT credential this week, or accept moving M4.
