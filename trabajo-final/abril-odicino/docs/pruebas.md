# Etapa 5. Pruebas de Consigna en pasos

## Funcionamiento de la página

Se abrió `src/index.html` como archivo local en Chrome 157, con conexión desactivada durante las pruebas de la página. Se pegaron las tres respuestas registradas más abajo y se probaron entradas vacías y fuera de formato. También se revisó el diseño en escritorio y en anchos de 390 y 320 píxeles. No se observaron errores de JavaScript ni solicitudes externas.

| Requisito | Cómo se probó | Resultado |
| --- | --- | --- |
| R1 | Se pegaron tres consignas y se verificó que seguían visibles al obtener la lista. | Funciona. |
| R2 | Se generó un prompt por consigna y se verificó que incluía el texto original, los tres prefijos y la instrucción de respetar fechas y requisitos. También se probó **Copiar prompt**. | Funciona. |
| R3 | Se pegaron las tres respuestas de ChatGPT. Se verificaron el texto de las tareas, sus etiquetas y la presencia de fecha solo en el primer caso. | Funciona. |
| R4 | Se marcó y desmarcó una tarea. El contador pasó de cero a uno y volvió a cero. | Funciona. |
| R5 | Se probaron ambos campos vacíos, texto sin prefijos, una respuesta parcialmente válida y `SIN TAREAS`. La página mostró el aviso correspondiente a cada caso. | Funciona. |
| R6 | Se abrió el HTML por `file://` con conexión desactivada y se completó el flujo con respuestas disponibles. | Funciona. |
| R7 | Se pulsó **Cargar ejemplo**. Aparecieron tres tareas, una fecha y un prompt listo. | Funciona. |

## Fidelidad de las respuestas de ChatGPT

El 19/11/2026 se probó el prompt de la página en tres chats nuevos de la versión web de ChatGPT sin iniciar sesión. La interfaz no mostró el nombre del modelo. Las entradas fueron ficticias. Se definió qué debía aparecer en cada caso antes de correrlos, se conservaron las respuestas y luego se volvieron a pegar en la página para comprobar que se podían importar.

### Caso 1. Varios entregables y fecha

Consigna: «Entregá un PDF de una página y subí una captura de los resultados hasta el 21 de noviembre.»

Se esperaba una tarea para el PDF de una página, otra para la captura de resultados y el plazo «hasta el 21 de noviembre».

```text
OBLIGATORIA: Entregar un PDF de una página.
OBLIGATORIA: Subir una captura de los resultados.
FECHA: hasta el 21 de noviembre.
```

Resultado: se importaron dos tareas obligatorias y el plazo. El modelo agregó un punto final a la línea de fecha. El día y el significado del plazo se conservaron.

### Caso 2. Tarea opcional

Consigna: «Subí el código al repositorio. Si querés, agregá una captura de pantalla.»

Se esperaba que subir el código fuera obligatorio y agregar la captura fuera opcional, sin fecha.

```text
OBLIGATORIA: Subir el código al repositorio.
OPCIONAL: Agregar una captura de pantalla.
```

Resultado: se importaron las dos tareas con las etiquetas esperadas y ninguna fecha.

### Caso 3. Consigna sin fecha

Consigna: «Escribí un resumen de tres líneas.»

Se esperaba una tarea que conservara el límite de tres líneas y ninguna fecha.

```text
OBLIGATORIA: Escribir un resumen de tres líneas.
```

Resultado: se importó una tarea obligatoria que conservó el límite. No apareció una fecha inventada.

## Alcance de la verificación

Las tres respuestas incluían los entregables esperados. Con tres casos breves no se puede estimar qué tan seguido el modelo omite requisitos en consignas más largas o ambiguas. La página comprueba el formato de las líneas. La fidelidad de cada tarea se revisa con la consigna original a la vista.
