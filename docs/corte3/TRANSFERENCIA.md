# Paquete de transferencia · Objetivo O4

Historia S6-04 ([#13](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/13)). El Charter define O4 como la transferencia del marco de gestión (tablero, backlog, Definition of Done y plan de monitoreo) y fija como medida de éxito la aceptación del paquete por el patrocinador en la semana 12.

> **Convención.** Las marcas **[escenario]** corresponden a hechos simulados del caso académico. Las marcas **[real]** corresponden a actos que solo ocurren con las personas reales: firma del patrocinador, auditoría del oficial de protección de datos y aprobaciones en GitHub. Un acto [escenario] no sustituye a uno [real].

## 1. Inventario

| # | Componente | Ubicación | Responsable que lo recibe (FinBank) | Estado |
|---|---|---|---|---|
| 1 | Tablero del programa (columnas Backlog, Ready, In Progress, Blocked, Review y Done; WIP ≤ 3 en In Progress) | Issues con etiquetas `estado:*` y milestone [Corte 3 · S6](https://github.com/OscarSantiagoMerino/DataForge-Consulting/milestone/1). Vista reproducible en `docs/corte3/TABLERO.md`. Tablero Trello del Corte 1 como antecedente. | VP de Riesgo y Analítica | Entregado |
| 2 | Product Backlog y registro de aceptación | `docs/corte3/data/backlog.csv`, `docs/corte3/data/acceptance.csv` | VP de Riesgo (dueña del producto tras la salida) | Entregado |
| 3 | Definition of Done y Definition of Ready | Sección 3 de este documento | VP de Riesgo | Entregado |
| 4 | Modelos de mora (30/60 d) y churn (3 meses), prototipo | `src/finbank/models.py`, `src/finbank/pilot.py` | VP de Riesgo | Entregado como prototipo sintético. Falta validarlo con datos reales. |
| 5 | Reglas de decisión y matriz de costos | `src/finbank/pilot.py` (`DELINQUENCY_COSTS`, `CHURN_COSTS`, umbrales) | Finanzas | Aprobación de Finanzas [escenario] en la Review de S5. Aprobación [real] pendiente. |
| 6 | Plan de monitoreo | `src/finbank/monitoring.py` y `docs/corte3/RUNBOOK.md`, sección 4 | Analista de Riesgo | Entregado |
| 7 | Runbook | `docs/corte3/RUNBOOK.md` | Analista de Riesgo · TI | Entregado |
| 8 | Pipeline de datos y pruebas | `src/finbank/`, `tests/`, `.github/workflows/ci.yml` | TI | Entregado. CI en verde en cada PR. |
| 9 | Informe final y presentación | `docs/corte3/` | Patrocinador | Ver PR de cierre (C3-00) |

## 2. Capacitación de analistas

| Sesión | Duración | Contenido | Ejercicio | Evidencia |
|---|---|---|---|---|
| 1. Operación semanal | 90 min | Runbook, pasos 1–5. Lectura de las listas. | Ejecutar el piloto en un clon limpio y obtener los mismos hashes que la ejecución de referencia. | Registro de asistentes por rol [escenario: S6 D8, 3 analistas de Riesgo y 1 de TI] |
| 2. Monitoreo y decisiones | 60 min | PSI, disparador de reentrenamiento y casos A–G. | Leer `monitoring_report.csv` de la demo y decidir qué hacer en las semanas 4 y 5. | Respuestas del ejercicio [escenario] |
| 3. Marco de gestión | 60 min | Tablero, backlog, DoD, Sprint Review y cómo entra un pedido nuevo (R6). | Registrar US-10 (explicaciones por cliente) en el backlog con criterios Dado/Cuando/Entonces. | Issue de backlog creada por FinBank [real, pendiente] |

## 3. Definition of Ready y Definition of Done vigentes

**Definition of Ready** (desde S3, acción de la retrospectiva de S2): la historia tiene criterios observables, estimación, responsable de negocio y **ninguna dependencia externa sin conceder**.

**Definition of Done** (Charter, sección 9, ampliada en el Corte 2):
1. Reproducible desde el repositorio.
2. Documentada en la plantilla acordada.
3. Pruebas en verde en CI.
4. PR aprobado por un integrante distinto del autor.
5. Validada por el responsable de negocio frente al proceso operativo.
6. Demostrada en la Sprint Review.

## 4. Auditoría de protección de datos (riesgo R5)

El Charter prevé la revisión del oficial de protección de datos en S1 y una auditoría en S6.

| Control | Resultado | Ámbito |
|---|---|---|
| Las listas no contienen nombre, documento, teléfono, correo ni dirección | Cumple: prueba `test_lists_carry_no_personal_data_and_only_pseudonymous_keys` | Técnico, verificable |
| El identificador de las listas es seudonimizado e irreversible sin la sal | Cumple: SHA-256 con sal fuera del repositorio | Técnico, verificable |
| La sal está bajo custodia del oficial de protección de datos y se rota | **Hallazgo [escenario, S6 D10]:** el piloto usaba la sal de demostración. El oficial exige una sal propia, custodiada por él, antes de firmar. | Escenario |
| El repositorio público no contiene grabaciones ni insumos privados | Cumple: `.gitignore` excluye videos (PR #16) | Técnico, verificable |

## 5. Acta de entrega

| Campo | Valor |
|---|---|
| Proyecto | GMAC-FB-2026-01 · Programa de Analítica Predictiva |
| Paquete | Componentes 1–9 del inventario |
| Condición previa | Cierre de la auditoría del oficial de protección de datos (hallazgo de la sal) |
| Decisión del patrocinador [escenario, Review de S6] | **Cierre con transferencia condicionada.** Se aceptan los entregables de M3–M5 y el piloto. La firma del acta queda sujeta al cierre del hallazgo de la sal en 5 días hábiles, sin costo adicional y sin liberar la reserva. |
| Firma del patrocinador [real] | **Pendiente.** No se simula. |
| Firma del oficial de protección de datos [real] | **Pendiente.** No se simula. |

Mientras el acta no esté firmada, S6-04 permanece fuera de Done en el escenario y sus 3 puntos aparecen como pendientes en el burndown.
