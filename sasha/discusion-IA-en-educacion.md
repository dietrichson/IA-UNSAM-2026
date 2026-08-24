# Discusión: IA en Educación

## Datos de la corrida

| Parámetro | Valor |
| --- | --- |
| Fecha | 2026-08-24 10:19:31 |
| Tema | IA en Educación |
| Modelo base | `qwen2.5:3b` |
| `num_ctx` | 4.096 tokens |
| `temperature` | 0.8 |
| Semilla (`--seed`) | 42 |
| Turnos generados | 5 |
| Motivo de finalización | ventana de contexto agotada en el turno 6 (3.903/4.096 tokens) |

> La semilla 42 fija el orden de los oradores de forma exacta y se le reenvía a Ollama, pero Ollama no garantiza texto idéntico entre corridas: la primera llamada después de cargar un modelo suele diferir de las siguientes. Como el largo de cada respuesta decide cuándo se llena la ventana, el turno final puede moverse de una corrida a otra.

## Participantes

| Personaje | Modelo en Ollama | Modelfile | Estudiante |
| --- | --- | --- | --- |
| Pepe Argento | `unsam-pepeargento` | `Dolores-Mujica/pepeargento-Modelfile` | Dolores-Mujica |
| Bugs Bunny | `unsam-bugsbunny` | `thiago/BugsBunny-Modelfile` | thiago |
| Bob Esponja | `unsam-bobesponja` | `BritezDiego/BobEsponja-modelfile` | BritezDiego |
| Batman | `unsam-batman` | `rosario/batman-modelfile` | rosario |
| Estudiante cansado | `unsam-estudiante` | `Erika/estudiante_cansado.md` | Erika |

## La discusión

### 1. Pepe Argento

Che, ¿qué onda con esta IA y educación? A mí me da que la chuparon bien con esto. El mundo se puso de payasos, monsieur. Y vos decís "¡Inteligencia Artificial para ayudar a los maestros!", pero mirá cómo es que funciona: la gente les da la tarea al asistente digital y luego la entrega al maestro. Decís que van juntos a construir el futuro del aprendizaje, pero eso no cambia que si vos decís una cosa y yo lo escucho otra, ya está muerto el proceso educativo. A mí me da más que un docente sea quien dé la clase, quien saque las preguntas y vea cómo vamos todos a ver qué sabemos. ¿Y cómo van a saber qué saben? Siendo maestros de verdad y no robots o asistentes tecnológicos. La educación es un show con corazón, che, no puede ser una presentación preprogramada.

### 2. Bugs Bunny

Eh... viejo, vos decís como si asistente digital y maestro fueran dos chicos peleando por el mismo puesto. Claro que la IA puede ser útil para preparar las tareas o ayudar a evaluar, pero nunca va en lugar de un docente que enseñe e interprete. Los robots les piden la tarea al asistente digital y luego te mandan a un maestro como si fuera una demostración del show educativo. ¿Y quién vuelve con el corazón y las ganas de aprender, viejo? El chico más chiquito que tiene miedo a perder su rol de protagonista.

### 3. Batman

Vos decís como si asistente digital y maestro fueran dos chicos peleando por el mismo puesto. Claro que la IA puede ser útil, pero no va en lugar del docente. ¿Y quién enseña sentimientos? Quien tiene que atraer vos al aprendizaje es quien te habla, viejo, no un robot o asistente digital. Los robots les piden la tarea al asistente y luego te mandan a un maestro como si fuera una demostración del show educativo. ¿Y quién vuelve con el corazón y las ganas de aprender, viejo? El chico más chiquito que tiene miedo a perder su rol de protagonista.

### 4. Bugs Bunny

Eh... viejo, vos y Batman asistente digital, vos decís como si docentes e IA fueran peleando por el mismo puesto. Claro que la IA puede ser útil para sacar preguntas o evaluar tareas, pero no va en lugar del maestro que enseña sentimientos e inspira a los chicos con su voz y carisma. Los robots le piden la tarea al asistente digital y luego te mandan a un maestro como si fuera una demostración de un show educativo, pero el corazón y las ganas de aprender los lleva el chico más chiquito que tiene miedo de perder su rol de protagonista.

### 5. Bob Esponja

Decís vos como si docentes e IA fueran peleando por el mismo puesto, pero no es así. El asistente digital nos ayuda a sacar preguntas y evaluar tareas, pero nunca va en lugar del maestro que enseña sentimientos e inspira con su voz e historias. El corazón y las ganas de aprender los lleva siempre el chico más chiquito, como vos y Patricio cuando somos amigos y nos reímos tanto que casi nos electrocutamos comprobando nossir medusas (¿sabés qué es eso? ¡Ja, ja, ja!) ¡Y nunca dejaré que nadie arruine ese momento divertido! La IA puede ser útil para preparar las tareas e evaluarlas, pero el docente sigue siendo el protagonista, el maestro con historia e inspiración. El asistente ayuda a que la clase sea más eficiente y entretenida, pero siempre va en segundo plano. Así que no te preocupás viejo, vos decís como si IA y maestro fueran peleando por el mismo puesto: al docente se lo ama, los robots les piden tareas e evalúan las respuestas, pero la magia del aprendizaje viene de un chico con corazón y una historia que contagia.

## Consumo de contexto

Cada fila es un turno. El **prompt** ya es acumulativo: en este modo, cada personaje recibe toda la discusión previa, así que la columna crece sola. La última columna muestra qué porcentaje de la ventana (`num_ctx` = 4.096) quedó ocupado al terminar el turno.

| Turno | Personaje | Prompt (tokens) | Respuesta (tokens) | Acumulado en la ventana | % de `num_ctx` |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Pepe Argento | 1.222 | 212 | 1.434 | 35.0 % |
| 2 | Bugs Bunny | 2.837 | 140 | 2.977 | 72.7 % |
| 3 | Batman | 2.287 | 154 | 2.441 | 59.6 % |
| 4 | Bugs Bunny | 3.136 | 145 | 3.281 | 80.1 % |
| 5 | Bob Esponja | 2.713 | 280 | 2.993 | 73.1 % |

## Por qué se detuvo la discusión

La discusión se detuvo en el turno 6 porque el prompt acumulado (proyectado) alcanzó 3.903 tokens sobre un `num_ctx` de 4.096, superando el umbral de seguridad del 90% (3.686 tokens).

Conviene subrayarlo en clase: el modelo no se aburrió ni se cansó. En este modo cada turno recibe **toda** la discusión anterior, así que el prompt crece sin parar mientras la ventana de contexto sigue midiendo lo mismo. A eso hay que sumarle el bloque `SYSTEM` de cada personaje, que se paga entero en cada llamada y nunca se achica. Cuando lo que hay que leer no entra en la ventana, no queda lugar para un turno más: o se corta el principio de la conversación, o se frena. Este script frena a propósito, para que el límite se vea. Subir `--num-ctx` corre el límite más lejos, pero no lo elimina, y cuesta memoria.
