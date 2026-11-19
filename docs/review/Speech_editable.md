# Guion de la Sprint Review del Corte 2

Actualización: 16 de octubre de 2026. Duración prevista: 15:00, incluidos 150 s de demo y 60 s de preguntas.

Daniel: Project Leader; Rafael: Business Analyst y PO; Oscar: Scrum Facilitator y SM. Los tres participan como Developers.

## 01 Seguimiento del corte 2
00:00-00:30 | 30 s | Daniel Martínez

Retomamos el compromiso presentado a FinBank. En esta revisión mostraremos el incremento de preparación de datos, sus pruebas y el cierre técnico en GitHub. Las cifras de los dos sprints corresponden al caso académico. La implementación, las aprobaciones y la integración tienen evidencia en el repositorio. Cerramos con las decisiones que necesita el siguiente sprint.

**En escena:** Señalar el título y el equipo. Abrir con el resultado de la entrega.

## 02 El compromiso del primer corte sigue vigente
00:30-01:20 | 50 s | Daniel Martínez

Seguimos trabajando sobre la línea base de doce semanas y ciento ochenta millones de pesos. El Charter organiza los frentes de mora y abandono de clientes. La captura conserva el tablero presentado en el primer corte, situado en el día nueve del segundo sprint. Para esta entrega añadimos un registro de C2 con las historias, sus puntos y sus criterios. Así puede seguirse el paso desde el tablero inicial hasta el incremento integrado. El patrocinador mantiene las decisiones sobre alcance, calendario y reserva.

**En escena:** Identificar la captura como histórica. Mostrar el enlace a docs/SPRINT_BACKLOG.md.

## 03 Qué cambia en la forma de entregar
01:20-02:10 | 50 s | Daniel Martínez

El primer corte definió alcance, riesgos, responsables y límites al trabajo en curso. En C2 profundizamos los eventos y las métricas Scrum. Las pruebas, el trabajo en parejas y las revisiones por PR incorporan controles al desarrollo. Ahora cada requisito puede seguirse desde el README hasta el archivo o la ejecución que lo demuestra. Conservamos la validación de negocio como condición de aceptación. Rafael participa como Product Owner, Oscar como Scrum Master y los tres desarrollamos. Yo mantengo la coordinación y el reporte previstos en el Charter.

**En escena:** Recorrer compromiso, calidad y mejora. Ceder la palabra a Rafael.

## 04 El incremento construido prepara los datos de mora
02:10-03:05 | 55 s | Rafael Baracaldo

El proceso parte de cinco mil registros sintéticos. Comprueba las entradas, calcula la calidad por variable, genera el diccionario y construye etiquetas de mora a treinta y sesenta días. La muestra pasa las reglas implementadas. Trescientas diecinueve cuentas conservan su observación faltante y quedan fuera del cálculo de tasas. El recorrido produce dos archivos CSV que podemos abrir y revisar. El modelo predictivo aparece como siguiente etapa: requiere definir ventanas temporales, persistir el conjunto de entrenamiento y separar la validación fuera de tiempo.

**En escena:** Recorrer el diagrama. Mostrar los dos CSV y señalar el modelo como próximo incremento.

## 05 Cuatro variables se excluyen por baja completitud
03:05-04:00 | 55 s | Rafael Baracaldo

Usamos un umbral inclusivo del ochenta por ciento de completitud. Canal digital, educación, dependientes y vivienda quedan por debajo y se excluyen del diccionario. Las otras dieciocho variables conservan descripción, tipo, valores válidos y dueño de negocio. El reporte registra la razón de cada exclusión para facilitar la revisión. La completitud permite decidir qué datos están disponibles con suficiente cobertura. El valor predictivo y los posibles sesgos se evaluarán durante la modelación. Todos los porcentajes de esta gráfica proceden de la muestra sintética.

**En escena:** Señalar el umbral, una exclusión y las 18 variables documentadas.

## 06 Demostración del incremento
04:00-06:30 | 150 s | Rafael Baracaldo

Vamos a ejecutar las dieciséis pruebas y el pipeline. Después abriremos los resultados de calidad y diccionario. En el último paso introduciremos un score de mil doscientos y una columna cedula: ambas reglas deben activar el rechazo. La captura muestra el CI exitoso de main tras la integración del PR ocho. El registro de ejecución queda disponible junto a las salidas.

**En escena:** Ejecutar python scripts/demo_review.py. Reservar 30 s a pruebas, 55 s a pipeline/CSV y 40 s al rechazo; usar el resto para abrir y cerrar. Si se usa respaldo, identificarlo como ejecución previa.

## 07 XP convierte reglas de negocio en evidencia
06:30-07:25 | 55 s | Oscar Merino

El ejemplo de TDD elimina loan_amount, una columna requerida. En la revisión roja, una prueba falla porque el validador deja pasar esa ausencia. Después del refactor, las doce pruebas de esa etapa pasan. La suite del incremento completo tiene dieciséis. El script reproduce ambos estados en copias temporales y guarda sus resultados. La bitácora añade dos sesiones de pairing con roles y decisiones, respaldadas por commits coautorados. Esta evidencia permite que otro integrante revise los supuestos y repita las comprobaciones.

**En escena:** Distinguir las 12 pruebas históricas de las 16 actuales. Mostrar los commits vigentes c90a325 y d9d2b52.

## 08 Un solo lugar para mantener las reglas
07:25-08:20 | 55 s | Rafael Baracaldo

La primera validación usaba bloques separados para cinco variables y repetía sus límites. El refactor consulta el esquema y recorre las veintidós candidatas con una función compartida. El diccionario usa la misma fuente. Cuando cambia un criterio de negocio, ese límite se mantiene en un solo lugar y las pruebas comprueban su aplicación. El módulo pasa de noventa y nueve a ochenta y cuatro líneas. La mejora que podemos verificar es la reducción de duplicación y la cobertura del esquema; el tiempo de mantenimiento se medirá cuando lleguen cambios reales.

**En escena:** Comparar cinco y 22 variables; señalar la fuente común de límites.

## 09 Capacidad de referencia y compromiso
08:20-09:25 | 65 s | Oscar Merino

El escenario cierra el primer sprint con dieciséis de dieciséis puntos y el segundo con quince de veinte. El cumplimiento de S2 es setenta y cinco por ciento y la media de ambos ciclos es quince coma cinco puntos. El compromiso creció veinticinco por ciento entre sprints. Cinco puntos dependían de una credencial externa que quedó pendiente. Estas cifras ofrecen una referencia inicial para la siguiente planificación. El estado técnico se comprueba por separado: el incremento de mora está integrado en main y sus pruebas pasan.

**En escena:** Señalar compromiso, cierre y promedio. Identificar las cifras como parte del escenario.

## 10 Burndown conciliado con la bitácora
09:25-10:25 | 60 s | Oscar Merino

Las curvas descuentan puntos al cierre del día en que la bitácora registra la terminación o aceptación del ítem. En S2 se descuentan dos puntos en el día tres por muestra y layout; tres en el día cinco por validaciones; siete en el día ocho por calidad y targets; y tres en el día diez por diccionario. Permanecen cinco de churn. Reconstruimos la serie para conciliarla con los Dailies del caso y dejamos el CSV en el repositorio. Cada descenso puede relacionarse con sus ítems.

**En escena:** Mostrar la curva S2 y el CSV. Explicar que es una reconstrucción documental del caso.

## 11 El bloqueo se convierte en una decisión de alcance
10:25-11:15 | 50 s | Oscar Merino

En el día seis del caso la falta de credencial bloquea churn. El Scrum Master escala el impedimento al día siguiente y el equipo adelanta los targets de mora con el Product Owner. Al cierre, los cinco puntos vuelven al backlog. La dependencia queda visible y requiere responsable y fecha de solución. Cuando se habilite el acceso, el equipo tendrá que estimar el trabajo y revisar su prioridad. Ese ajuste debe respetar la capacidad disponible del siguiente sprint.

**En escena:** Recorrer días seis, siete, ocho y diez. Señalar la decisión sobre el backlog.

## 12 Las retrospectivas cambian el siguiente sprint
11:15-12:05 | 50 s | Oscar Merino

La retrospectiva de S1 propuso centralizar scripts, probar reglas y programar en parejas. Esa preparación ya tiene evidencia: repositorio, CI y coautoría. La de S2 propone verificar dependencias antes de comprometer historias. En Planning S3 comprobaré acceso y condiciones de entrada; Rafael priorizará con los Developers. Daniel hará seguimiento a las evidencias y al registro de aceptación. Cada acción tiene responsable y momento de verificación en la bitácora. Los bloqueos deberán escalarse dentro de veinticuatro horas.

**En escena:** Señalar una acción completada y otra que se verificará en Planning S3.

## 13 Integración y aceptación del incremento
12:05-13:00 | 55 s | Daniel Martínez

Los ocho pull requests están integrados. Los componentes se revisaron entre ramas y el PR ocho los consolidó en main el quince de octubre. Oscar y mi cuenta aprobaron esa integración; Rafael había revisado los contenidos técnicos. La rama cuenta con protección y el CI de main terminó correctamente. Durante esta Review registraremos la decisión sobre el incremento: qué criterios se aceptan y qué observaciones requieren seguimiento. El formato incluye el commit demostrado, participantes y responsables de cualquier ajuste.

**En escena:** Mostrar captura del PR #8 y abrir docs/SPRINT_REVIEW_ACCEPTANCE.md.

## 14 Sprint 3 debe proteger el objetivo de mora
13:00-13:40 | 40 s | Daniel Martínez

Proponemos tomar el modelo base de mora, de trece puntos. La referencia inicial de capacidad es quince a dieciséis. Añadir churn completo llevaría el compromiso a dieciocho. Si se libera el acceso, PO y Developers acordarán una sustitución o dividirán el alcance y volverán a estimar. Para US-06 se requieren ventanas temporales, un dataset persistido y validación fuera de tiempo frente al AUC objetivo de cero coma setenta y cinco. El patrocinador revisará también el efecto sobre M4.

**En escena:** Señalar 13 y 18; pedir una decisión sobre alcance.

## 15 Decisión solicitada a FinBank
13:40-15:00 | 80 s | Daniel Martínez

Solicitamos confirmar el foco de mora, registrar la aceptación de este incremento y asignar responsable y fecha para el acceso a churn. Ajustaremos M4 con el patrocinador según el alcance acordado. Abrimos un minuto para preguntas.

**En escena:** Veinte segundos de cierre y sesenta de preguntas. Rafael responde sobre datos; Oscar sobre método. Registrar decisiones al terminar.
