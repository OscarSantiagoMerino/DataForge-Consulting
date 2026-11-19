# FinBank — Entrega del Corte 2

DataForge Consulting · GMAC · Escuela Colombiana de Ingeniería Julio Garavito

Daniel Felipe Martínez Hernández, Rafael Alejandro Baracaldo Doikov y Oscar Santiago Merino Suárez.

El incremento prepara datos para el modelo de mora de FinBank. Genera una muestra sintética de 5.000 registros, valida las entradas, calcula la completitud de 22 variables, documenta las 18 conservadas y construye etiquetas de mora a 30 y 60 días. La batería de 16 pruebas comprueba reglas de integridad y casos de borde.

La entrega corresponde a los Sprints 1 y 2 del caso académico. Las cifras de gestión provienen del escenario de FinBank; las pruebas, los commits, las revisiones y la integración en GitHub tienen evidencia ejecutable. El entrenamiento de modelos y la evaluación financiera pertenecen a las etapas siguientes.

## Archivos para entregar

| Producto | Archivo y evidencia | Peso dentro del corte |
|---|---|---:|
| A. Reporte de Sprints | [Reporte_Sprints_Corte2.pdf](docs/report/Reporte_Sprints_Corte2.pdf), versión vigente de tres páginas con el diseño de referencia | 40 % |
| B. Repositorio y prácticas XP | Este repositorio público y la [bitácora XP](docs/XP_LOG.md) | 30 % |
| C. Sprint Review | [Presentación](docs/review/Presentacion_FinBank_Corte2.pptx), [guion](docs/review/Speech_FinBank_Corte2.pdf) y [demo](docs/SPRINT_REVIEW_DEMO.md) | 30 % |

El corte representa el 30 % de la nota definitiva. La [consigna conservada en texto](docs/requirements/C2_Proyecto.txt) permite contrastar esta matriz con el enunciado. El [Charter](docs/context/Project_Charter_FinBank.pdf) y la [propuesta del Corte 1](docs/context/Propuesta_FinBank_v3.pdf) documentan el alcance original.

## Requisitos y solución

| Requisito de C2 | Solución implementada | Evidencia | Estado |
|---|---|---|---|
| Reporte ejecutivo de 3–4 páginas | Tres páginas con ocho apartados, cierre de S1/S2 y comparación C1/C2 | [PDF vigente](docs/report/Reporte_Sprints_Corte2.pdf) | Preparado |
| Backlog priorizado, objetivos y puntos | Ítems, criterios y estados de gestión y técnicos separados | [Backlog C2](docs/SPRINT_BACKLOG.md) | Documentado |
| Velocidad estimada frente a real | S1: 16/16; S2: 15/20; media: 15,5 puntos | PDF, sección 3; [métricas](docs/SPRINT_METRICS.md) | Calculado sobre el escenario |
| Burndown | Curvas reconstruidas con el día de cierre registrado para cada ítem | [CSV diario](docs/evidence/sprint_burndown.csv); [método](docs/SPRINT_METRICS.md) | Conciliado con los Dailies del caso |
| Daily Scrums | Hecho, siguiente paso e impedimento en los días relevantes | [Bitácora](docs/DAILY_RETROSPECTIVES.md) | Escenario documentado; reuniones reales por acreditar |
| Retrospectivas Start/Stop/Continue | Actas de S1 y S2, responsables y seguimiento | [Actas](docs/DAILY_RETROSPECTIVES.md#retrospectivas) | Documentadas |
| Pairing, mínimo dos sesiones | P1 Rafael/Daniel; P2 Oscar/Rafael; cambio de conductor y commits coautorados | [XP 01](docs/XP_LOG.md#01-programación-en-parejas) | Coautoría disponible |
| Mínimo tres pruebas automatizadas | 16 pruebas: ocho de validación, cuatro de calidad y cuatro de targets | [tests/](tests); [ejecución](docs/evidence/tests.txt) | 16 pasan |
| TDD | Una prueba falla antes del refactor y pasa después | [XP 02](docs/XP_LOG.md#02-pruebas-y-tdd); [registro](docs/evidence/tdd/summary.json) | Rojo/verde reproducible |
| Git público, ramas y PR aprobados e integrados | #1–#7 para componentes; #8 consolida en main | [XP 03](docs/XP_LOG.md#03-integración-continua-y-propiedad-colectiva); [PR #8](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/8) | Ocho PR integrados |
| Integración continua | Actions ejecuta pruebas y pipeline en PR y push a main | [Workflow](.github/workflows/ci.yml); [CI del incremento](https://github.com/OscarSantiagoMerino/DataForge-Consulting/actions/runs/38844935088) | Main verificada |
| Diseño simple y refactor antes/después | Una función usa el esquema compartido por validación y diccionario | [Antes](docs/refactoring/validation_before.py); [después](src/finbank/validation.py); [XP 04](docs/XP_LOG.md#04-diseño-simple-y-refactorización) | Implementado |
| Demo de quince minutos | Guion de 900 segundos con 150 de demo y 60 de preguntas | [Guion](docs/review/Speech_editable.md); [ejecución](scripts/demo_review.py) | Preparada; sustentación pendiente |
| Historias que cumplen DoD | Ejecución, documentación, tests y revisión; aceptación por criterios preparada | [Registro de aceptación](docs/SPRINT_REVIEW_ACCEPTANCE.md) | Cierre técnico verificado; aceptación y Review pendientes |
| Lecciones y plan de mejora | US-06 priorizada en 13 puntos, dependencia de churn y decisión sobre M4 | PDF, secciones 5, 7 y 8; [acciones](docs/DAILY_RETROSPECTIVES.md#acciones-de-seguimiento) | Propuesta para el próximo Planning |

Los registros Scrum describen el caso del curso. Para acreditar reuniones reales se requieren sus registros originales o la validación del alcance del simulacro por el docente. El equipo completará el registro de aceptación durante la Sprint Review.

## Ejecutar el incremento

Requiere Python 3.11 o posterior. Desde la raíz del repositorio:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
python scripts/run_pipeline.py
```

La muestra usa la semilla 2026. Resultado predeterminado:

```text
5.000 registros sintéticos; 0 violaciones en la muestra
22 variables candidatas; 4 excluidas con completitud inferior al 80 %
18 variables en el diccionario
default_30d: 5,85 %; default_60d: 2,37 %
```

Las tasas usan 4.681 observaciones disponibles. Hay 319 cuentas con observación faltante que conservan su etiqueta vacía. `reports/quality_report.csv` guarda las decisiones y `reports/feature_dictionary.csv` documenta descripción, tipo, valores válidos, completitud y dueño de cada variable. Las etiquetas se calculan en memoria.

```bash
python scripts/demo_review.py
# Preparar el entorno sin pausas:
python scripts/demo_review.py --auto
# Reproducir el ejemplo histórico de TDD:
python scripts/reproduce_tdd.py
```

## Organización y trazabilidad

| Componente | Ítem | Función |
|---|---|---|
| `src/finbank/schema.py` | T-05.2 | Define las 22 variables y sus reglas |
| `src/finbank/sample.py` | T-05.0 | Genera la muestra sintética reproducible |
| `src/finbank/validation.py` | T-05.6 / R-01 | Comprueba rangos, categorías, identificadores y columnas personales conocidas |
| `src/finbank/quality.py` | T-05.1 / T-05.2 | Calcula completitud y prepara el diccionario |
| `src/finbank/targets.py` | T-05.4 | Construye etiquetas por umbral de mora |
| `scripts/run_pipeline.py` | Incremento S2 | Ejecuta el proceso y escribe los CSV |

El [Trello del Corte 1](https://trello.com/b/cUNjbYqu/dataforge-finbank-predictive-analytics-program) conserva una fotografía del día 9 de S2. La referencia vigente de C2 es [SPRINT_BACKLOG.md](docs/SPRINT_BACKLOG.md). Las capturas anteriores sirven como antecedentes.

Rafael actúa como Product Owner, Oscar como Scrum Master y los tres como Developers. Daniel mantiene el liderazgo y el reporte del Charter. La bitácora XP distingue contribución técnica, cuenta creadora del PR y aprobación registrada.

## Alcance pendiente y aceptación

El siguiente incremento debe definir ventanas temporales, persistir el dataset de entrenamiento y evaluar el modelo base de mora frente al AUC objetivo de 0,75. Churn requiere resolver el acceso y completar su historia de datos. Los modelos, los umbrales económicos y el piloto siguen el calendario del Charter.

El control de columnas personales cubre nombres conocidos. La revisión de protección de datos corresponde al proceso de aceptación del caso. Las decisiones financieras se evaluarán cuando existan modelos y resultados de negocio.

El PDF vigente está en `docs/report/Reporte_Sprints_Corte2.pdf`. Los reportes anteriores quedan en `docs/archive/`. La [lista de entrega](docs/DELIVERY_CHECKLIST.md) distingue los archivos preparados de los actos que el equipo realizará en la sustentación.

## Reconstruir el reporte

```bash
python -m pip install -r requirements-delivery.txt
python scripts/build_report.py
python scripts/build_review_notes.py
```

El reporte usa la [fuente LaTeX](docs/report/Reporte_Sprints_Corte2.tex) y conserva el diseño del PDF de referencia: tipografía Latin Modern, ocho apartados numerados, tablas con líneas horizontales y tres gráficos de métricas. Requiere una distribución LaTeX con `pdflatex`, `lmodern`, `babel-spanish` y `pgfplots`, como MiKTeX o TeX Live. El constructor comprueba que el resultado tenga tres páginas y que el texto respete los márgenes. El guion usa ReportLab. Estas dependencias se mantienen separadas de las necesarias para ejecutar el incremento.
