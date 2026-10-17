# Sprint Review y demostración de quince minutos

La [presentación](review/Presentacion_FinBank_Corte2.pptx) y el [guion editable](review/Speech_editable.md) mantienen quince diapositivas y 900 segundos. El guion reserva 150 segundos para la demo de Rafael y 60 para preguntas.

## Preparación

1. Instalar las dependencias del README y ejecutar `python scripts/demo_review.py --auto`.
2. Tener abiertos los CSV de `reports/demo/`, la bitácora XP, el PR #8 y el CI de main.
3. Ensayar con los tres integrantes y comprobar cambios de pantalla.
4. Mantener disponible [SPRINT_REVIEW_ACCEPTANCE.md](SPRINT_REVIEW_ACCEPTANCE.md) para registrar criterios y decisiones.

## Recorrido de la exposición

| Tiempo | Responsable | Diapositivas | Contenido |
|---|---|---|---|
| 00:00–02:10 | Daniel | 1–3 | Compromiso y continuidad del proyecto |
| 02:10–06:30 | Rafael | 4–6 | Incremento, calidad y demo de 150 s |
| 06:30–07:25 | Oscar | 7 | Prácticas XP y ejemplo TDD |
| 07:25–08:20 | Rafael | 8 | Diseño simple y refactor |
| 08:20–12:05 | Oscar | 9–12 | Capacidad, curvas conciliadas, bloqueo y retrospectivas |
| 12:05–14:00 | Daniel | 13–15 | Integración, aceptación y propuesta S3 |
| 14:00–15:00 | Equipo | 15 | Preguntas y decisiones |

## Demo desde la raíz del repositorio

```bash
python scripts/demo_review.py
```

El programa ejecuta las 16 pruebas, genera calidad/diccionario y comprueba el rechazo de score 1200 y columna cedula. Sus pausas permiten explicar cada paso. `--auto` elimina las pausas para preparar el entorno.

Abrir `reports/demo/quality_report.csv` y `feature_dictionary.csv`. Señalar las cuatro exclusiones y las 18 variables documentadas. Las tasas 5,85 % y 2,37 % se calculan sobre la muestra sintética.

Si falla el entorno, abrir los [resultados de preparación](evidence/outputs/) y el [registro](evidence/demo.txt), identificados como ejecución previa. El equipo conservará las observaciones del evento en el registro de aceptación.

## Evidencias que conviene mostrar

- Coautoría: commits 211d6c3 y b3bb92e.
- TDD: `python scripts/reproduce_tdd.py`, registros rojo/verde y prueba de loan_amount.
- Integración: PR #8, con aprobaciones y main como destino.
- CI: ejecución 38844935088 para 0b53f59; comprobar también los checks de cualquier revisión posterior.
- Gestión: CSV de burndown y Dailies del caso; registro C2 en SPRINT_BACKLOG.md.

## Decisiones al cierre

Registrar la aceptación por criterio, las observaciones del docente y los responsables de ajustes. Confirmar el foco de mora para S3 y el responsable del acceso a churn. US-06 y churn completos suman 18 puntos; la referencia de capacidad es 15–16, por lo que requieren priorización o división del alcance.
