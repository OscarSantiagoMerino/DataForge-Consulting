# Backlog y cierre del Corte 2

Actualización: 16 de octubre de 2026. Este registro es la referencia de C2. El [Trello de C1](https://trello.com/b/cUNjbYqu/dataforge-finbank-predictive-analytics-program) conserva el día 9 de S2.

El orden de las tablas indica prioridad. Los días de cierre describen el escenario académico; la última columna identifica la evidencia actual. La aceptación del incremento está en [SPRINT_REVIEW_ACCEPTANCE.md](SPRINT_REVIEW_ACCEPTANCE.md).

## Sprint 1

Objetivo: establecer gobierno, acceso y perfilamiento. Compromiso y cierre del caso: 16 puntos.

| Prioridad | Ítem | Puntos | Criterio de cierre del caso | Día | Evidencia actual |
|---:|---|---:|---|---|---|
| 1 | US-01 Charter | 3 | Revisión por patrocinador | D7 | [Charter C1](context/Project_Charter_FinBank.pdf); autorización del escenario |
| 2 | US-02 Acuerdo de acceso | 5 | Acuerdo y condiciones de anonimización | D10 | Cierre declarado en el caso; firma real por acreditar |
| 3 | US-03 Perfilamiento | 5 | Perfilamiento sobre muestra de apoyo | D5 | Muestra y controles reproducibles; cifras de cartera del caso |
| 4 | US-04 Tablero, repo y DoD | 3 | Tablero y condiciones compartidas | D3 | Trello, README y PR #1 |

## Sprint 2

Objetivo: preparar la base de mora y churn. Compromiso: 20 puntos. Cierre del caso: 15; quedan cinco de churn.

| Prioridad | Ítem | Puntos | Criterio verificable | Día del caso | Estado técnico actual |
|---:|---|---:|---|---|---|
| 1 | T-05.0 Muestra y layout | 2 | Muestra reproducible de 22 variables | D3 | Implementado e integrado por #8 |
| 2 | T-05.6 Validaciones | 3 | Rangos, categorías, identificadores y columnas requeridas | D5 | Ocho pruebas de validación pasan |
| 3 | T-05.1 Calidad | 4 | Completitud y exclusión justificada al 80 % | D8 | CSV integrado; contenido aprobado en #4 |
| 4 | T-05.4 Targets | 3 | Etiquetas 30/60 con fronteras y faltantes controlados | D8 | Cuatro pruebas de targets pasan |
| 5 | T-05.2 Diccionario | 3 | 18 variables con descripción, tipo, valores y dueño | D10 | CSV reproducible; contenido aprobado en #4; aceptación del incremento pendiente |
| 6 | T-05.5 Historial churn | 5 | Acceso habilitado y extracto revisable | Pendiente | Dependencia abierta del caso; Product Backlog |

T-05.3, validación de negocio del tablero original, se conserva como actividad de aceptación del diccionario. Su esfuerzo está incluido en T-05.2 para evitar duplicar puntos. R-01 pertenece al trabajo de validación y conserva sus pruebas y PR.

## Preparación de Sprint 3

| Orden propuesto | Ítem | Puntos | Condición |
|---:|---|---:|---|
| 1 | US-06 Modelo base de mora | 13 | Ventanas temporales, validación separada y AUC objetivo de 0,75 |
| 2 | T-05.5 Historial churn | 5 | Acceso resuelto y negociación de sustitución o división de alcance |
| 3 | US-07 Alertas tempranas | 5 | Propuesta de traslado a S4, sujeta a priorización |

La capacidad de referencia es 15–16 puntos. Mora y churn completos suman 18. PO y Developers acordarán alcance antes de S3; el patrocinador revisará el efecto sobre M4.
