# Guion de sustentación · Corte 3

Duración: **30,0 min de presentación + 5 min de preguntas**. Coincide con la consigna del Corte 3. Generado por `scripts/build_corte3.py` desde la misma especificación que el PPTX: las notas del orador repiten este texto.

| # | Diapositiva | Quién | Min | Acumulado |
|---:|---|---|---:|---:|
| 1 | Portada | Daniel | 0,5 | 0,5 |
| 2 | FinBank se enteraba tarde de sus problemas | Daniel | 1,5 | 2,0 |
| 3 | Recomendamos cerrar el proyecto: solo falta una firma | Daniel | 2,0 | 4,0 |
| 4 | S6 ajustó el compromiso a la velocidad anterior | Oscar | 2,0 | 6,0 |
| 5 | El tablero hace visible cada bloqueo y cada aceptación | Oscar | 2,0 | 8,0 |
| 6 | S6-01: una historia trazable de punta a punta | Rafael | 2,5 | 10,5 |
| 7 | Sprint 6: 15 puntos comprometidos según la velocidad demostrada | Rafael | 1,5 | 12,0 |
| 8 | Burndown: 12 de 15 puntos, y el faltante no es de capacidad | Oscar | 2,0 | 14,0 |
| 9 | Los impedimentos vinieron de fuera; la respuesta, de nuestras reglas | Oscar | 1,5 | 15,5 |
| 10 | El piloto produce la lista semanal con un AUC de 0,80 | Rafael | 1,5 | 17,0 |
| 11 | Churn: cumplir O2 cuesta beneficio y la decisión es de Finanzas | Rafael | 2,0 | 19,0 |
| 12 | Demo: del repositorio a la lista en un comando | Rafael | 2,5 | 21,5 |
| 13 | El monitoreo detectó el cambio en la semana 4 | Oscar | 1,5 | 23,0 |
| 14 | Hitos: el final en la semana 12; dos desplazamientos absorbidos | Daniel | 1,5 | 24,5 |
| 15 | Presupuesto: 169,0 frente a 169,2 millones, sin tocar la reserva | Daniel | 2,0 | 26,5 |
| 16 | Lo que aprendimos como equipo y como líderes | Oscar | 2,0 | 28,5 |
| 17 | Recomendamos cerrar; estos pendientes tienen dueño | Daniel | 1,5 | 30,0 |
| 18 | Preguntas | Todos | 5,0 |  |
| 19 | B1 · Evidencia de GitHub | Oscar | resp. |  |
| 20 | B2 · Salida del monitoreo | Rafael | resp. |  |
| 21 | B3 · Presupuesto por sprint | Daniel | resp. |  |

Tiempo por integrante: Daniel 9,0 min, Oscar 11,0 min, Rafael 10,0 min.

## Texto por diapositiva

**1. Portada**, Daniel, 0,5 min

Buenos días. Somos DataForge Consulting, Grupo 1. FinBank quiere anticipar la mora y la cancelación de créditos para que Cobranza y Retención puedan actuar a tiempo. Presentaremos el piloto sobre datos sintéticos y el balance de las doce semanas. Luego revisaremos qué debe ocurrir para que FinBank pueda operar el programa. Transición: empiezo por el caso.

**2. FinBank se enteraba tarde de sus problemas**, Daniel, 1,5 min

FinBank es un banco con 125.000 clientes y una cartera de crédito de 420.000 millones de pesos. DataForge Consulting es la consultora que contrató; es un caso académico simulado. El problema: el banco veía la mora cuando el pago ya se había perdido y la salida de un cliente cuando ya se había ido. Eso pone en riesgo unos 77.000 millones, cerca del 18 % de la cartera. Nos pidió tres cosas: anticipar los atrasos, anticipar las salidas y dejar un método de trabajo. Las reglas: 12 semanas, 6 sprints y 180 millones. Hoy veremos cómo trabajamos, qué logramos, cuánto costó y qué decisión necesitamos. Transición: empiezo por esa decisión.

**3. Recomendamos cerrar el proyecto: solo falta una firma**, Daniel, 2,0 min

Recomendamos cerrar el proyecto. Terminamos 12 de los 15 puntos del último sprint; lo que falta depende de la firma del acta, que espera la auditoría de protección de datos. Gastamos 169,0 de 169,2 millones, sin usar la reserva, y llegamos a tiempo a la semana 12, después de recuperar dos retrasos. El modelo de mora acierta 8 de cada 10 veces al comparar dos clientes por riesgo, y la meta era 7,5; lo probamos con datos simulados, no con datos reales del banco. Por eso le pedimos a FinBank tres cosas: aprobar el cierre sujeto a la firma, decidir si prefiere detectar al menos 6 de cada 10 clientes que se van aunque el beneficio estimado baje 8,5 millones, y programar la prueba con datos reales. Transición: Oscar cuenta cómo trabajamos estas doce semanas.

**4. S6 ajustó el compromiso a la velocidad anterior**, Oscar, 2,0 min

S1 y S2 vienen del Corte 2. En S2 comprometimos 20 y cerramos 15 porque el extracto de churn dependía de una credencial de TI. De ahí salió la Definition of Ready. Por eso la credencial, que llegó el día 2 de S3, no entró a ese sprint. S4 cerró 13 porque la validación de churn necesitaba tres meses de observación. S3, S4 y S5 comprometieron 16 puntos frente a medias previas de 15,5, 15,7 y 15,0. S6 comprometió 15 frente a 15,2 y cumplió el límite. Transición: así se veía el tablero.

**5. El tablero hace visible cada bloqueo y cada aceptación**, Oscar, 2,0 min

Seis columnas con reglas escritas. WIP máximo de 3. Un bloqueo se escribe con su causa y se escala en 24 horas. Algo importante: separamos tres estados que se suelen confundir: integrado en GitHub, Done del escenario y aceptado por el negocio. Transición: Rafael sigue una historia de punta a punta.

**6. S6-01: una historia trazable de punta a punta**, Rafael, 2,5 min

La lista semanal nació como US-07 en el pronóstico de S3 y se convirtió en S6-01. Entró a Ready con 5 puntos y criterios Dado/Cuando/Entonces, se trabajó en pairing y se bloqueó tres días por el ambiente de TI. La issue #10 quedó cerrada y el PR #17 está integrado. Las 33 pruebas del PR corresponden al piloto. La validación con datos reales queda pendiente. Transición: veamos el sprint completo.

**7. Sprint 6: 15 puntos comprometidos según la velocidad demostrada**, Rafael, 1,5 min

El objetivo era doble: el piloto operando y el paquete listo para la firma. Cinco historias. La única que no cumple la DoD es S6-04, y la marcamos así. El pedido nuevo de Retención no entró: está en el Product Backlog. Transición: Oscar muestra el burndown.

**8. Burndown: 12 de 15 puntos, y el faltante no es de capacidad**, Oscar, 2,0 min

Los puntos bajan solo cuando el ítem cumple la DoD. La curva queda plana tres días por el bloqueo y se recupera desde el día 6. Velocidad, throughput, tiempo de ciclo y WIP son métricas distintas y por eso las mostramos por separado. Transición: ¿qué nos frenó?

**9. Los impedimentos vinieron de fuera; la respuesta, de nuestras reglas**, Oscar, 1,5 min

Cuatro eventos. El de TI en S2 cambió el plan del proyecto. El de S6 no movió el hito. La auditoría es la lección principal: llegó el último día. Transición: Rafael, los resultados.

**10. El piloto produce la lista semanal con un AUC de 0,80**, Rafael, 1,5 min

Subrayo que es un prototipo sobre datos sintéticos con semilla fija. Prueba que el método funciona de punta a punta y deja todo listo para cambiar el generador por el extracto. No presentamos ninguna cifra que el código no produzca. Transición: el hallazgo más interesante fue el de churn.

**11. Churn: cumplir O2 cuesta beneficio y la decisión es de Finanzas**, Rafael, 2,0 min

El umbral que maximiza beneficio deja escapar a 6 de cada 10 clientes que se van, y eso incumple O2. Cumplir O2 cuesta 8,5 millones en la cohorte sintética. Proponemos el umbral operativo y pedimos que Finanzas lo ratifique. Transición: vamos a la demo.

**12. Demo: del repositorio a la lista en un comando**, Rafael, 2,5 min

Corro pytest, luego el piloto, abro la lista y corro el monitoreo. Si algo falla, esta salida es la ejecución registrada y la diapositiva B2 tiene el monitoreo. Transición: Oscar, monitoreo y transferencia.

**13. El monitoreo detectó el cambio en la semana 4**, Oscar, 1,5 min

En la semana 4, el score quedó en vigilar, bureau_score activó una alerta y el AUC bajó. El control evalúa rachas independientes de AUC y recall, y en la demo marca reentrenamiento en la semana 5 por la segunda caída de AUC. El paquete de transferencia está completo, salvo lo que depende de actos reales. Transición: Daniel, el balance.

**14. Hitos: el final en la semana 12; dos desplazamientos absorbidos**, Daniel, 1,5 min

M2 y M4 se desplazaron por la misma causa. El resto llegó en su semana. Distinguimos la cronología del escenario de las fechas académicas. Transición: el dinero.

**15. Presupuesto: 169,0 frente a 169,2 millones, sin tocar la reserva**, Daniel, 2,0 min

Base aprobada, gasto, pronóstico y reserva por separado. En S2 íbamos 2,8 % por debajo. Cerramos 0,12 % por debajo. Gestión superó su rubro por las escalaciones, pero el total queda dentro del límite. Transición: lo que aprendimos.

**16. Lo que aprendimos como equipo y como líderes**, Oscar, 2,0 min

Oscar abre y cada uno dice su aprendizaje en una frase. Daniel: comunicación temprana con el patrocinador. Rafael: decir que no en este sprint. Oscar: reglas escritas. Transición: Daniel cierra.

**17. Recomendamos cerrar; estos pendientes tienen dueño**, Daniel, 1,5 min

La decisión del escenario es el cierre condicionado. Los pendientes reales no los simulamos: cada uno tiene dueño. Gracias. Abrimos preguntas.

**18. Preguntas**, Todos, 5,0 min

Cinco minutos de preguntas. Ver respuestas preparadas.

**19. B1 · Evidencia de GitHub**, Oscar, respaldo

Respaldo si preguntan por las aprobaciones o el CI.

**20. B2 · Salida del monitoreo**, Rafael, respaldo

Respaldo si falla la demo en vivo.

**21. B3 · Presupuesto por sprint**, Daniel, respaldo

Respaldo si preguntan por la fórmula de desviación.

## Demo y respaldo

1. `pytest -q` (todas en verde). 2. `python scripts/run_pilot.py`. 3. Abrir `reports/pilot/early_warning_list.csv`. 4. `python scripts/run_monitoring.py`.

Respaldo: la diapositiva 12 muestra la salida registrada del piloto, B2 la del monitoreo y `docs/corte3/evidence/` las ejecuciones completas. Antes de la sustentación, correr la demo una vez en el equipo que se va a usar.

## Preguntas previsibles

| Pregunta | Responde | Respuesta corta |
|---|---|---|
| ¿Los modelos cumplen O1 y O2? | Rafael | En el prototipo sí: AUC fuera de tiempo de 0,7959 y recall de 0,6203 al umbral operativo, sobre datos sintéticos. Con datos de FinBank no está acreditado; la sección 6 del runbook dice cómo hacerlo. |
| ¿Por qué no usar el umbral de máximo beneficio? | Rafael | Porque incumple O2: su recall es de 0,41. La regla propuesta toma el mayor beneficio entre los umbrales con recall ≥ 0,60. La última palabra es de Finanzas. |
| ¿Se gastó la reserva? | Daniel | No. La solicitud de COP 4,2 M de S2 nunca se activó porque la credencial llegó antes de los 10 días. El gasto cerró en 169,0 frente a 169,2. |
| ¿Por qué S6-04 no está en Done si todo está entregado? | Oscar | Porque la DoD exige la validación del responsable de negocio, y el acta requiere la firma real tras la auditoría. Marcarla Done habría inflado la velocidad. |
| ¿Los PR están aprobados? | Oscar | Están abiertos con el CI en verde y la revisión pedida a Daniel y Rafael. El autor no se aprueba a sí mismo, y no damos nada por integrado hasta el merge. |
| ¿Qué cambió frente al Corte 1 y al Corte 2? | Oscar | Corte 1: PMBOK y Kanban, métricas de flujo. Corte 2: Scrum y XP, velocidad y DoD con pruebas. Corte 3: el mismo marco hasta el cierre, más la separación entre el Done técnico y la aceptación del negocio. |
| ¿Qué pasa si el piloto se degrada? | Rafael | El monitoreo marca reentrenamiento tras dos semanas con caída > 0,05. El runbook asigna la decisión a la VP de Riesgo, con un plazo de 10 días hábiles. |
| ¿Cómo protegen los datos personales? | Daniel | Muestra anonimizada desde S1, listas con clave SHA-256 con sal y la sal bajo custodia del oficial de protección de datos. Ese fue justamente el hallazgo de la auditoría. |

## Reglas para la sustentación

- No presentar actos simulados (Review, firma, Finanzas) como aceptaciones reales.
- Decir «prototipo sobre datos sintéticos» cada vez que se cite AUC o recall.
- Si alguien pregunta por la aprobación de los PR, mostrar su estado real en GitHub (B1).
