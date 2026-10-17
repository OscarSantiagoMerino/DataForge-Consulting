# Bitácora XP del Corte 2

Proyecto GMAC-FB-2026-01. Actualización: 16 de octubre de 2026, hora de Colombia.

La bitácora vincula las prácticas del caso FinBank con el código y GitHub. P1/P2 y los días S1/S2 corresponden al escenario académico. Los commits de implementación se registraron el 13 de octubre; las revisiones e integraciones, el 14 y 15 de octubre de 2026.

## 01 Programación en parejas

| Sesión | Día del caso | Conductor declarado | Navegador declarado | Decisión revisada | Commit vigente |
|---|---|---|---|---|---|
| P1 | S2 D3 | Rafael | Daniel | Conservar faltantes; rechazar una columna `cedula` | [211d6c3](https://github.com/OscarSantiagoMerino/DataForge-Consulting/commit/211d6c3668000ff490287b5df8e8ddbe32a5a986) |
| P2 | S2 D7 | Oscar | Rafael | Conservar NaN en las etiquetas de cuentas sin observación | [b3bb92e](https://github.com/OscarSantiagoMerino/DataForge-Consulting/commit/b3bb92e724dfb272993b3df6a1dfdc214189daaa) |

Los commits incluyen `Co-authored-by:`. En P1 figuran Rafael y Daniel; en P2, Rafael. La bitácora describe la rotación de conductor; el historial conserva la coautoría registrada. La consigna admite estos commits como alternativa a fotos o capturas de las sesiones.

## 02 Pruebas y TDD

| Archivo | Pruebas | Cobertura |
|---|---:|---|
| `tests/test_validation.py` | 8 | Rangos, nulos, categorías, tipos, identificador, columnas personales y requeridas |
| `tests/test_quality.py` | 4 | Completitud, exclusión justificada, umbral inclusivo y diccionario |
| `tests/test_targets.py` | 4 | Fronteras 29/30 y 59/60, faltantes, negativos y coherencia de etiquetas |

La ejecución actual está en [evidence/tests.txt](evidence/tests.txt). `python scripts/reproduce_tdd.py` reproduce el siguiente caso:

| Paso | Revisión | Resultado |
|---|---|---|
| Rojo | [c90a325](https://github.com/OscarSantiagoMerino/DataForge-Consulting/commit/c90a325) | 1 falla y 11 pasan: la ausencia de `loan_amount` queda sin detectar |
| Verde/refactor | [d9d2b52](https://github.com/OscarSantiagoMerino/DataForge-Consulting/commit/d9d2b5287d0f9d6974956b28a5255d207884192e) | 12 pasan: se informa la columna ausente |
| Incremento completo | [PR #8](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/8) | 16 pasan |

Los [registros históricos](evidence/tdd/) se generan en copias temporales y conservan la rama activa.

## 03 Integración continua y propiedad colectiva

El [workflow CI](../.github/workflows/ci.yml) instala Python 3.11 y ejecuta pruebas y pipeline. Se activa en PR y push a main. La [ejecución tras #8](https://github.com/OscarSantiagoMerino/DataForge-Consulting/actions/runs/38844935088) terminó correctamente. La consulta de la rama confirmó su protección.

Los PR #2–#7 se revisaron como cambios encadenados entre ramas. El PR #8 llevó el conjunto a main. Los ocho están integrados.

| PR | Contenido | Cuenta creadora real | Aprobación registrada | Destino original |
|---|---|---|---|---|
| [#1](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/1) | Estructura, CI y DoD | OscarSantiagoMerino | Ch0comilo (Daniel) | main |
| [#2](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/2) | Muestra y esquema | OscarSantiagoMerino | correoalejandro (Rafael) | Rama de #1 |
| [#3](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/3) | Reglas y pruebas | OscarSantiagoMerino | correoalejandro (Rafael) | Rama de #2 |
| [#4](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/4) | Calidad y diccionario | OscarSantiagoMerino | correoalejandro (Rafael) | Rama de #3 |
| [#5](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/5) | Refactor R-01 | OscarSantiagoMerino | correoalejandro (Rafael) | Rama de #4 |
| [#6](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/6) | Targets y pipeline | OscarSantiagoMerino | correoalejandro (Rafael) | Rama de #5 |
| [#7](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/7) | Reportes y bitácora | OscarSantiagoMerino | correoalejandro (Rafael) | Rama de #6 |
| [#8](https://github.com/OscarSantiagoMerino/DataForge-Consulting/pull/8) | Consolidación del incremento | correoalejandro | OscarSantiagoMerino y Ch0comilo | main |

La revisión de #8 pidió incorporar su integración final a esta bitácora. La tabla registra la actividad de las cuentas; las sesiones documentan la contribución técnica declarada.

Rafael participó en las implementaciones de #3 y #6 y también las aprobó. Para siguientes cambios se establece revisión por un integrante ajeno a la implementación. La revisión del conjunto por Daniel en #8 aporta una lectura adicional.

Los [metadatos consultados](evidence/github_state.json) conservan fechas, ramas y aprobaciones. La aprobación técnica se incorpora al [registro de aceptación](SPRINT_REVIEW_ACCEPTANCE.md) durante la Review.

## 04 Diseño simple y refactorización

R-01 centraliza los límites en `schema.py`. La validación y el diccionario consultan esa fuente compartida.

| Aspecto | Antes | Después |
|---|---|---|
| Implementación | [validation_before.py](refactoring/validation_before.py) | [validation.py](../src/finbank/validation.py) |
| Variables cubiertas | 5 | 22 mediante el esquema |
| Líneas físicas | 99 | 84 |
| Lugares donde se mantiene un límite | 2 | 1 |
| Incorporación de una variable | Nuevo bloque | Entrada en el esquema |

La función recorre `SCHEMA`, comprueba cada columna y llama a `_check_variable`. Las pruebas de reglas previas y de columna faltante protegen el refactor. El beneficio comprobado es reducir duplicación y ampliar las variables cubiertas. El efecto sobre mantenimiento podrá evaluarse con futuros cambios de negocio.
