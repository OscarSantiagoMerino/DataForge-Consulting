# Tablero del Corte 3 (vista reproducible)

Generado desde GitHub con `python scripts/github_snapshot.py` el 2026-11-19 03:35 UTC.
La cuenta no tiene el permiso `project` del token, así que el tablero se lleva con etiquetas `estado:*` sobre las issues y el milestone [Corte 3 · S6](https://github.com/OscarSantiagoMerino/DataForge-Consulting/milestone/1).

**Reglas de movimiento.** Backlog → Ready cuando cumple la Definition of Ready (criterios, estimación, responsable de negocio, sin dependencia externa pendiente). Ready → In Progress si hay cupo (WIP máximo 3). In Progress → Blocked con la causa y el responsable en un comentario; el Scrum Master escala en 24 horas. In Progress → Review al abrir el PR con CI. Review → Done solo cuando el PR está fusionado y la DoD se cumple, incluida la validación del responsable de negocio. La aceptación real del negocio se registra aparte (`data/acceptance.csv`).

## Backlog (0)
- —

## Ready (0)
- —

## In-Progress (0)
- —

## Blocked (1)
- [#13](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/13) [C3][S6][S6-04] Paquete de transferencia y capacitación (O4)

## Review (5)
- [#11](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/11) [C3][S6][S6-02] Monitoreo de desempeño y drift de los modelos
- [#12](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/12) [C3][S6][S6-03] Runbook de operación del piloto
- [#14](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/14) [C3][S6][S6-05] Balance final de cronograma y presupuesto frente al Charter
- [#15](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/15) [C3][S6][C3-00] Paquete de entregables del Corte 3
- [#22](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/22) [C3][S6][C3-01] Sitio web desplegado del cierre (GitHub Pages)

## Done (1)
- [#10](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/10) [C3][S6][S6-01] Piloto controlado con lista semanal de alerta temprana

WIP actual en In Progress: 0 de 3.

## Pull requests del Corte 3

| PR | Rama | Estado | CI (último SHA) | Aprobado por | Revisión pedida a | Merge |
|---|---|---|---|---|---|---|
| [#16](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/16) | `c3/s6/c3-00-gitignore-videos` | MERGED | success (`8668de9`) | Ch0comilo | correoalejandro | f0429f2 |
| [#17](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/17) | `c3/s6/s6-01-piloto` | MERGED | success (`e6bb357`) | Ch0comilo | — | 8bd9e3e |
| [#18](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/18) | `c3/s6/s6-02-monitoreo` | MERGED | success (`a355b9a`) | correoalejandro | — | cc95ed4 |
| [#19](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/19) | `c3/s6/s6-03-runbook` | MERGED | success (`71250a5`) | correoalejandro | Ch0comilo | 9570e93 |
| [#20](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/20) | `c3/s6/s6-04-transferencia` | MERGED | success (`3fb7559`) | correoalejandro | Ch0comilo | 4d079a7 |
| [#21](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/21) | `c3/s6/s6-05-cierre` | OPEN | success (`1cf1ae6`) | — | Ch0comilo,correoalejandro | — |
| [#23](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/23) | `c3/s6/c3-01-sitio-web` | OPEN | success (`29e625c`) | — | Ch0comilo,correoalejandro | — |
