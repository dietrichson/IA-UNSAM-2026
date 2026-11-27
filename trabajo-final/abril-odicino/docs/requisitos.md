# Etapa 2. Requisitos de Consigna en pasos

## Imprescindibles

| ID | Requisito comprobable |
| --- | --- |
| R1 | La página permite pegar una consigna en español y mantenerla a la vista mientras se revisa la lista. |
| R2 | A partir de la consigna, la página genera un texto listo para copiar que pide al modelo extraer tareas obligatorias y opcionales, conservar las fechas y ceñirse al texto original. |
| R3 | La página transforma la respuesta del modelo en una lista con tareas etiquetadas como obligatorias u opcionales y muestra por separado las fechas que aparecen en la respuesta. |
| R4 | Cada tarea puede marcarse y desmarcarse, y el contador de tareas completadas se actualiza con cada cambio. |
| R5 | La página avisa cuando falta pegar la consigna o cuando la respuesta pegada no contiene tareas que se puedan reconocer. |
| R6 | El archivo `src/index.html` se abre y procesa texto de ejemplo en el navegador sin instalación, servidor ni conexión. |

## Si queda tiempo

| ID | Requisito comprobable |
| --- | --- |
| R7 | Se puede cargar una consigna y una respuesta de ejemplo con un botón para conocer el flujo. |

## Fuera de alcance

Conexión automática con ChatGPT, lectura de PDF o imágenes, cuentas, historial y guardado de avances al cerrar la página. Para generar una lista nueva con IA, la persona usa ChatGPT por separado y pega el resultado en la página. Las tareas propuestas por el modelo se revisan con la consigna original.
