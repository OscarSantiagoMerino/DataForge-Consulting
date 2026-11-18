# Corte 3 · Cierre del programa FinBank: índice de entregables y evidencias

Proyecto GMAC-FB-2026-01 · DataForge Consulting · Entrega académica: 18-nov-2026 · Sustentación: 20-nov-2026 (30 min + 5 de preguntas).

`GrupoX` es un marcador que se reemplaza cuando se confirme el número de grupo.

## Entregables

| Entregable | Archivo | Fuente editable |
|---|---|---|
| Informe Final de Gestión (PDF) | [Informe_Final_FinBank_GrupoX.pdf](Informe_Final_FinBank_GrupoX.pdf) | [informe/Informe_Final_FinBank_GrupoX.tex](informe/Informe_Final_FinBank_GrupoX.tex) + tablas en `informe/generated/` |
| Presentación de sustentación (PDF) | [Presentacion_FinBank_GrupoX.pdf](Presentacion_FinBank_GrupoX.pdf) | [Presentacion_FinBank_GrupoX.pptx](Presentacion_FinBank_GrupoX.pptx), con notas del orador |
| Guion por integrante, demo y preguntas | [Guion_Sustentacion.md](Guion_Sustentacion.md) | `scripts/corte3_slides.py` (misma especificación que el PPTX) |
| Runbook del piloto (S6-03) | [RUNBOOK.md](RUNBOOK.md) | — |
| Paquete de transferencia (S6-04) | [TRANSFERENCIA.md](TRANSFERENCIA.md) | — |
| Tablero reproducible | [TABLERO.md](TABLERO.md) | `python scripts/github_snapshot.py` |
| **Sitio web desplegado (C3-01)** | https://oscarsantiagomerino.github.io/DataForge-Consulting/ | [site/index.html](../../site/index.html) y `python scripts/build_site.py --deploy` |

## Evidencia reproducible

Un único conjunto de tablas alimenta el informe, la presentación y las gráficas:

| Tabla | Contenido | Rótulo |
|---|---|---|
| [data/sprints.csv](data/sprints.csv) | Objetivo, compromiso y terminado de S1–S6 | S1–S2 antecedente · S3–S5 reconstrucción · S6 simulación |
| [data/backlog.csv](data/backlog.csv) | Ítems con puntos, responsable, dependencia, objetivo, hito y día de Done | Ídem |
| [data/s6_items.csv](data/s6_items.csv) | Inicio, bloqueo y fin de cada historia de S6 (burndown, WIP, ciclo) | Simulación C3 |
| [data/s6_daily.csv](data/s6_daily.csv) | Dailies de S6 con cambios de plan, bloqueos, escalaciones, Review y Retro | Simulación C3 |
| [data/milestones.csv](data/milestones.csv) | M1–M6: semana base, semana del escenario, condición y evidencia | Ídem |
| [data/budget.csv](data/budget.csv) | Base y gasto por sprint y rubro (COP millones) | Ídem |
| [data/acceptance.csv](data/acceptance.csv) | Registro de aceptación: escenario frente a estado real y quién lo resuelve | Ídem |
| [data/retro_actions.csv](data/retro_actions.csv) | Acciones de mejora con responsable y seguimiento | Ídem |
| [data/github_log.csv](data/github_log.csv) | Bitácora issue → rama → PR → CI → revisión → merge, leída de GitHub | Verificable |

Salidas reales de ejecución (con commit y fecha) en [evidence/](evidence/): `tests.txt`, `pipeline.txt`, `pilot.txt`, `monitoring.txt`, `pilot_metrics.csv` y `monitoring_report.csv`. Gráficas en [figures/](figures/).

`tests/test_corte3_evidence.py` concilia las tablas entre sí y con el Charter: base + reserva = COP 180 M, rubros, cierre histórico de S2 (54,8 frente a 56,4), puntos frente a backlog, WIP ≤ 3 y que ninguna aceptación real figure como firmada.

## Reconstruir todo

```bash
pip install -r requirements.txt -r requirements-corte3.txt
python scripts/github_snapshot.py   # tablero y bitácora desde GitHub (requiere gh autenticado)
python scripts/build_corte3.py      # pruebas, demo, figuras, informe, PPTX, PDF y guion
```

El informe requiere `pdflatex`. La exportación del PPTX a PDF usa PowerPoint en Windows; en otro sistema se usa `--skip-pdf-export` y se exporta a mano.

## Historias del Sprint 6 en GitHub

| ID | Issue | PR | Rama |
|---|---|---|---|
| C3-00 | [#15](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/15) | [#16](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/16), cierre en el PR de S6-05 | `c3/s6/c3-00-gitignore-videos` |
| S6-01 | [#10](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/10) | [#17](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/17) | `c3/s6/s6-01-piloto` |
| S6-02 | [#11](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/11) | [#18](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/18) | `c3/s6/s6-02-monitoreo` |
| S6-03 | [#12](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/12) | [#19](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/19) | `c3/s6/s6-03-runbook` |
| S6-04 | [#13](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/13) | [#20](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/20) | `c3/s6/s6-04-transferencia` |
| S6-05 | [#14](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/14) | ver [TABLERO.md](TABLERO.md) | `c3/s6/s6-05-cierre` |

Los PR forman una cadena: cada rama contiene a la anterior. Se integran **en orden** con *Create a merge commit*, después de la aprobación de un integrante distinto del autor. El estado vigente (CI, aprobación, merge) está en [TABLERO.md](TABLERO.md).

## Lo que este paquete no afirma

- Que la sustentación ya ocurrió, o que el patrocinador, Finanzas o el oficial de protección de datos firmaron algo: son actos reales pendientes (ver `data/acceptance.csv`).
- Que los modelos cumplan O1/O2 con datos de FinBank: las métricas son del prototipo sobre datos sintéticos.
- Que un PR esté integrado antes de su merge en GitHub.
