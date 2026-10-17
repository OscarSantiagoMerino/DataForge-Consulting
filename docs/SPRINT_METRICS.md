# Velocidad y burndown

Estas métricas describen el escenario académico. Los días relativos conservan su secuencia; las fechas de GitHub registran el trabajo técnico de octubre.

| Sprint | Compromiso | Cierre del caso | Cumplimiento |
|---|---:|---:|---:|
| S1 | 16 | 16 | 100 % |
| S2 | 20 | 15 | 75 % |

Media: `(16 + 15) / 2 = 15,5` puntos por sprint. El compromiso S2 aumentó `(20 / 16 - 1) × 100 = 25 %`. Dos sprints aportan una referencia inicial para planificar.

## Criterio de reconstrucción

La curva descuenta puntos al finalizar el día en que la bitácora consigna cierre o aceptación. Esta reconstrucción documental reemplaza las series anteriores y concilia las gráficas con los Dailies del caso. R-01 y T-05.3 son actividades de las historias, con cero puntos adicionales en esta cuenta.

- S1 D3: US-04, tres puntos; D5: US-03, cinco; D7: US-01, tres; D10: US-02, cinco.
- S2 D3: T-05.0, dos; D5: T-05.6, tres; D8: T-05.1 y T-05.4, siete; D10: T-05.2, tres.
- T-05.5 mantiene cinco puntos al cierre.

| Día | S1 pendientes | S2 pendientes |
|---:|---:|---:|
| 0 | 16 | 20 |
| 1 | 16 | 20 |
| 2 | 16 | 20 |
| 3 | 13 | 18 |
| 4 | 13 | 18 |
| 5 | 8 | 15 |
| 6 | 8 | 15 |
| 7 | 5 | 15 |
| 8 | 5 | 8 |
| 9 | 5 | 8 |
| 10 | 0 | 5 |

Ideal: `compromiso × (1 - día / 10)`. El [CSV](evidence/sprint_burndown.csv) conserva serie e ítems de cada descenso. Las gráficas reconstruyen el escenario. La actividad real del repositorio se comprueba con commits, PR y CI.
