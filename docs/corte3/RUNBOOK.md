# Runbook del piloto · FinBank · Programa de Analítica Predictiva

Historia S6-03 ([#12](https://github.com/OscarSantiagoMerino/DataForge-Consulting/issues/12)). Documento operativo para el analista de Riesgo de FinBank que ejecuta el piloto después del cierre de DataForge.

> **Alcance.** El piloto corre sobre un segmento controlado (región andina) y, en este repositorio, con datos sintéticos y semillas fijas. Para usarlo con datos de FinBank se reemplazan los generadores `generate_sample` y `generate_churn_sample` por el extracto anonimizado con el mismo layout. Ese cambio requiere la validación de TI y del oficial de protección de datos (sección 6).

## 1. Roles

| Rol (FinBank) | Responsabilidad en el piloto |
|---|---|
| Analista de Riesgo (operador) | Ejecuta los pasos 2–4 cada lunes, revisa los controles y publica las listas. |
| VP de Riesgo y Analítica | Dueña de los modelos. Decide el reentrenamiento y los cambios de umbral. |
| Gerencia de Cobranza | Recibe la lista de alerta temprana y registra el resultado de la gestión. |
| Gerencia de Retención | Recibe la lista de churn y ejecuta las ofertas, que son responsabilidad de FinBank según el Charter. |
| TI e infraestructura | Mantiene el ambiente del piloto y el acceso al extracto. |
| Oficial de protección de datos | Custodia la sal de seudonimización y audita las salidas (Ley 1581). |
| Finanzas | Aprueba la matriz de costos y los umbrales (O3). |

## 2. Preparación (una vez)

```bash
git clone https://github.com/OscarSantiagoMerino/DataForge-Consulting.git
cd DataForge-Consulting
python -m venv .venv
.venv/Scripts/activate        # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
pytest -q                     # debe terminar en "passed", sin fallos
```

Requisito: Python 3.11 o superior. La variable de entorno `FINBANK_PSEUDONYM_SALT` debe contener la sal entregada por el oficial de protección de datos. Sin ella el piloto usa una sal de demostración que **no** sirve para producción. La sal nunca se escribe en el repositorio ni en este documento.

## 3. Ejecución semanal (lunes, antes de las 10:00)

| Paso | Comando | Resultado esperado |
|---|---|---|
| 1. Pruebas | `pytest -q` | Todas en verde. Si alguna falla, **no** se publican listas (sección 5, caso A). |
| 2. Calidad del extracto | `python scripts/run_pipeline.py reports/semana` | 0 violaciones de reglas, reporte de calidad y diccionario. |
| 3. Piloto | `python scripts/run_pilot.py reports/semana` | `early_warning_list.csv`, `churn_list.csv` y `pilot_metrics.csv`. |
| 4. Monitoreo | `python scripts/run_monitoring.py reports/semana` | `monitoring_report.csv` con PSI, AUC y la marca de reentrenamiento. |
| 5. Publicación | Copia de las dos listas a la carpeta compartida de Cobranza y de Retención | Solo las columnas `client_key`, `probability`, `decile` y `action`. |

Las listas usan `client_key`, un identificador seudonimizado. La correspondencia con el cliente real se resuelve dentro de la infraestructura del banco, con la misma sal, y nunca en archivos compartidos.

## 4. Controles que el operador revisa

| Control | Fuente | Umbral | Lectura |
|---|---|---|---|
| Estabilidad del score | `psi_score` | < 0,10 estable · 0,10–0,25 vigilar · ≥ 0,25 alerta | La población que se puntúa se parece a la de desarrollo. |
| Estabilidad por variable | `top_variable`, `psi_top_variable` | Mismas bandas | Indica qué variable explica el cambio. |
| Desempeño | `auc_30d`, `auc_drop` | Caída > 0,05 frente a la base | Se mide cuando maduran los 30 días de la cohorte. |
| Reentrenamiento | `retraining_flag` | 2 semanas consecutivas con caída > 0,05 | Marca de la propuesta (diapositiva 4). |
| Volumen de la lista | Filas con acción distinta de «seguimiento normal» | ±30 % frente al promedio de 4 semanas | Un salto suele indicar un problema de extracto antes que un cambio de riesgo. |

## 5. Qué hacer ante cada caso

| Caso | Acción | Responsable | Plazo |
|---|---|---|---|
| A. Falla una prueba o una regla de validación | No publicar. Abrir incidente con la salida del comando. Revisar el extracto con TI. | Analista de Riesgo → TI | Mismo día |
| B. PSI en «vigilar» | Publicar y anotar la variable en la bitácora semanal. | Analista de Riesgo | Mismo día |
| C. PSI en «alerta» en el score o en una variable | Publicar con nota de advertencia. Revisar con la VP si la causa es de datos o de población. | Analista de Riesgo + VP de Riesgo | 2 días hábiles |
| D. `retraining_flag = True` | Congelar cambios de umbral. Reentrenar con la cohorte reciente, validar fuera de tiempo (AUC ≥ 0,75 / recall ≥ 0,60) y presentar en el comité de la VP antes de reemplazar el modelo. | VP de Riesgo (decide), Analista (ejecuta) | 10 días hábiles |
| E. Volumen fuera de ±30 % | Verificar el conteo del extracto y la fecha de corte antes de publicar. | Analista de Riesgo + TI | Mismo día |
| F. Solicitud de nuevas variables o segmentos | Registrar en el Product Backlog. No se cambia el modelo en operación sin pasar por la Definition of Done. | VP de Riesgo | Siguiente revisión |
| G. Sospecha de exposición de datos personales | Detener la publicación y notificar al oficial de protección de datos. | Cualquier rol | Inmediato |

## 6. Cambiar los datos sintéticos por el extracto de FinBank

1. TI entrega el extracto anonimizado con las 22 variables del esquema (`src/finbank/schema.py`) y el layout de churn (`src/finbank/churn.py`).
2. Se carga como un diccionario de columnas y se valida con `assert_valid` (paso 2). Las variables bajo el 80 % de completitud se excluyen automáticamente (riesgo R2).
3. Se reentrenan los dos modelos y se repite la validación fuera de tiempo **con datos reales**. Solo entonces O1 y O2 quedan acreditados para FinBank. Hoy están acreditados únicamente en el prototipo sintético.
4. Finanzas confirma la matriz de costos (`DELINQUENCY_COSTS`, `CHURN_COSTS` en `src/finbank/pilot.py`), que hoy son parámetros del escenario.

## 7. Recuperación

- Toda salida se regenera desde el repositorio. No hay estado oculto: borrar `reports/` y volver a ejecutar los pasos 1–4 produce los mismos archivos con el mismo extracto.
- Para volver a una versión anterior del modelo se usa el commit etiquetado en `main` (`git checkout <sha>`) y se repiten los pasos.
- Los hashes SHA-256 que imprime `run_pilot.py` permiten comprobar que la lista publicada corresponde a la ejecución registrada.
