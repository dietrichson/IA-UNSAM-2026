# Etapa 3. Diseño de Consigna en pasos

## Piezas del sistema

1. **Consigna.** Un formulario recibe texto en español. Ese texto queda visible para comparar las tareas con el original.
2. **Preparación del prompt.** JavaScript agrega instrucciones y el formato de respuesta. La persona copia el prompt a ChatGPT y trae la respuesta a la página.
3. **Lectura de la respuesta.** JavaScript reconoce tareas obligatorias, tareas opcionales y fechas, las muestra por separado y resume las tareas completadas. Si no encuentra tareas en el formato acordado, indica qué formato espera. Si solo algunas líneas se reconocen, muestra un aviso para revisar el resultado.

## Herramientas, modelo y datos

Un solo archivo `src/index.html` contiene la estructura, los estilos y JavaScript. Se usa la API estándar del navegador para manejar formularios, mostrar texto y marcar casillas. El texto pegado se representa como texto plano. La aplicación trabaja en memoria durante la sesión y la integración con ChatGPT es manual. El ejemplo usa una consigna ficticia que viene incluida con la página. No se necesita una versión de modelo específica para importar el resultado.

El formato pedido usa una línea por elemento con `OBLIGATORIA:`, `OPCIONAL:` o `FECHA:` al comienzo. El modelo debe usar `FECHA:` solo cuando la consigna indique un plazo y copiarlo tal como está escrito. Si la consigna no contiene tareas, el formato permite responder `SIN TAREAS`.

## Primera versión y alcance

La primera versión incluye el flujo completo de consigna, prompt, respuesta pegada y lista marcable. Incluye un ejemplo para probar el recorrido con el navegador desconectado. La consulta a un modelo para generar resultados nuevos requiere acceso a ChatGPT. Quedan para otro proyecto la carga de archivos y la conexión automática con el modelo.

## Organización

La propuesta está preparada para una entrega individual de Abril Odicino. La verificación se divide en el funcionamiento de la página y la revisión de la fidelidad de lo que responde el modelo.
