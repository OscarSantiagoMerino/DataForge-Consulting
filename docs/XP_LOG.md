# XP log (Bitácora de prácticas XP)

Project GMAC-FB-2026-01, FinBank S.A. DataForge Consulting, second term.

The sprint days below belong to the simulated engagement (Sprint 1: 10–21 Aug 2026,
Sprint 2: 24 Aug–4 Sep 2026). Commits and pull requests carry the real dates on which
the team did the work.

## 01. Pair programming

Rule: anything that encodes a business rule is written by two people, one driving and
one navigating, and the driver changes from one session to the next. The commit of a
pairing session ends with a `Co-authored-by:` line for the navigator.

| Session | Sprint day | Driver | Navigator | Item | What the navigator changed | Evidence |
|---|---|---|---|---|---|---|
| P1 | S2 D3 | Rafael | Daniel | T-05.6 validation rules | Missing values must not count as range violations; a `cedula` column must fail the run (Ley 1581) | [`ec8dc1a`](https://github.com/OscarSantiagoMerino/DataForge-Consulting/commit/ec8dc1a0171a5771467ff20b4054472fe340ccde) |
| P2 | S2 D7 | Oscar | Rafael | T-05.4 delinquency targets | Accounts too recent to be observed stay missing instead of counting as good clients | [`831eabc`](https://github.com/OscarSantiagoMerino/DataForge-Consulting/commit/831eabc083275433025180bff0090518d95cd48d) |

Commit message format for a session:

```
T-05.4 Delinquency targets at 30 and 60 days

Co-authored-by: Rafael Alejandro Baracaldo Doikov <correoalejandro97@gmail.com>
```

## 02. Test-driven development

Rule: the test that describes the rule is committed first and fails; the code that
makes it pass is committed after. An item is not Done with a red test.

| Test file | Tests | Rules covered |
|---|---|---|
| `tests/test_validation.py` | 8 | Ranges (bureau score 150–950 and the rest of the schema), categories, numeric types, unique and non-null identifier, no personal data columns, missing columns |
| `tests/test_quality.py` | 4 | One row per candidate variable, exclusion below 80% completeness with a written reason, inclusive threshold, 18 variables in the dictionary |
| `tests/test_targets.py` | 4 | Boundaries at 29/30 and 59/60 days, unobserved accounts stay missing, negative days rejected, default at 60 implies default at 30 |

Execution report, `pytest -v`, Python 3.11.9:

```
tests/test_quality.py::test_report_has_one_row_per_candidate_variable PASSED
tests/test_quality.py::test_variables_below_threshold_are_excluded_with_a_reason PASSED
tests/test_quality.py::test_threshold_is_inclusive PASSED
tests/test_quality.py::test_dictionary_holds_the_18_variables_kept PASSED
tests/test_targets.py::test_targets_at_the_boundaries PASSED
tests/test_targets.py::test_unobserved_accounts_stay_missing PASSED
tests/test_targets.py::test_negative_days_past_due_are_rejected PASSED
tests/test_targets.py::test_default_at_60_implies_default_at_30 PASSED
tests/test_validation.py::test_sample_respects_every_rule PASSED
tests/test_validation.py::test_bureau_score_outside_range_is_reported PASSED
tests/test_validation.py::test_missing_values_are_not_range_violations PASSED
tests/test_validation.py::test_duplicated_and_null_identifiers_are_reported PASSED
tests/test_validation.py::test_unknown_category_is_reported PASSED
tests/test_validation.py::test_numeric_variable_loaded_as_text_is_reported PASSED
tests/test_validation.py::test_personal_data_column_is_rejected PASSED
tests/test_validation.py::test_missing_column_is_reported PASSED
============================= 16 passed in 0.26s ==============================
```

CI runs on `main` and on every pull request: [GitHub Actions, workflow CI](https://github.com/OscarSantiagoMerino/DataForge-Consulting/actions/workflows/ci.yml).

## 03. Continuous integration and collective ownership

Rule: nothing lives only on a personal computer. One branch per item, a pull request
into `main`, approval by a member who did not write it, and the CI workflow
(`.github/workflows/ci.yml`) green before merging. `main` is protected: no direct pushes.

| PR | Branch | Item | Author | Reviewer | Link |
|---|---|---|---|---|---|
| 1 | `chore/ci-and-skeleton` | US-04 repository, CI, Definition of Done | Oscar | Daniel | [#1](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/1) |
| 2 | `feature/t050-sample-and-schema` | T-05.0 extraction layout and anonymized sample | Rafael | Oscar | [#2](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/2) |
| 3 | `feature/t056-validation-rules` | T-05.6 validation rules, tests first (pairing P1) | Rafael + Daniel | Oscar | [#3](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/3) |
| 4 | `feature/t051-quality-report` | T-05.1 quality report and T-05.2 feature dictionary | Daniel | Rafael | [#4](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/4) |
| 5 | `refactor/r01-schema-driven-validation` | R-01, see practice 04 | Oscar | Rafael | [#5](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/5) |
| 6 | `feature/t054-delinquency-targets` | T-05.4 targets (pairing P2) and pipeline script | Oscar + Rafael | Daniel | [#6](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/6) |
| 7 | `docs/sprint-report-and-xp-log` | Sprint report, Sprint Review script and this log | Daniel | Oscar | [#7](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/7) |

Each member is author of at least one pull request and reviewer of at least one written
by someone else, so every module has been read by two people.

## 04. Simple design and refactoring

### R-01. Validation rules read their bounds from the schema

**Before** (`docs/refactoring/validation_before.py`, merged in PR 3). The first iteration
validated the five variables collections asked about first. Each variable had its own
block, and each block repeated a bound that was already written in `schema.py` for the
feature dictionary:

```python
score = table["bureau_score"]
if score.dtype == object:
    violations.append(Violation("not_numeric", "bureau_score", len(score)))
else:
    score = score[~np.isnan(score)]
    if (score < 150).sum() > 0:
        violations.append(Violation("below_minimum", "bureau_score", int((score < 150).sum())))
    if (score > 950).sum() > 0:
        violations.append(Violation("above_maximum", "bureau_score", int((score > 950).sum())))
# ...the same block again for age, credit_utilization and installment_to_income
```

Problem found at the Daily Scrum of S2 D5: covering the 22 candidate variables meant 17
more copies, and a bound changed by the business would have to be edited in two files.

**After** (`src/finbank/validation.py`, PR 5). One function checks any variable, and the
bounds come from the schema that also feeds the dictionary:

```python
for variable in schema:
    if variable.name not in table:
        violations.append(Violation("missing_column", variable.name, 0))
    else:
        violations += _check_variable(table[variable.name], variable)
```

| | Before | After |
|---|---|---|
| Lines in the module | 99 | 84 |
| Variables validated | 5 | 22 |
| Places where a bound is written | 2 | 1 |
| Cost of adding a variable | A new block of about 10 lines | One line in `schema.py` |
| Tests passing | 7 | 8 (the 7 unchanged, plus `test_missing_column_is_reported`) |

Behaviour did not change for the five original variables: the seven tests written for the
first iteration pass on both versions without being edited.
