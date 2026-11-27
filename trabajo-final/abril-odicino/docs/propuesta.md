# Consigna en pasos

Abril Odicino · Trabajo final del seminario de IA, UNSAM

## Qué voy a construir

Voy a construir una página que ayude a convertir una consigna de clase en una lista de tareas que se puedan marcar. La persona pega la consigna, usa un prompt preparado por la página en ChatGPT y trae de vuelta la lista generada para revisarla y usarla.

## Para quién y qué problema resuelve

Está pensado para estudiantes que tienen una consigna con varios puntos y quieren organizarse antes de empezar. Por ejemplo, una consigna puede pedir un archivo, una prueba y una breve explicación, además de sugerir una actividad opcional. Tener el texto original y la lista a la vista ayuda a revisar qué exige la consigna y qué queda por hacer.

## Qué parte usa IA

El modelo de lenguaje leerá la consigna y extraerá las tareas en lenguaje simple, una por línea. El prompt le pedirá que distinga lo obligatorio de lo opcional, conserve las fechas tal como aparecen y evite agregar requisitos. La consulta al modelo será manual, por copiar y pegar en ChatGPT. La página se encargará de armar el prompt y de convertir la respuesta pegada en una lista que se pueda marcar.

## Qué retomo del seminario y qué me falta aprender

Del Laboratorio 1 retomo el uso de instrucciones para orientar la respuesta de un modelo. Del Laboratorio 4 retomo la idea de hacer un programa chico que se abra en el navegador. Me falta comprobar qué redacción del prompt ayuda a conservar los requisitos y qué tan seguido el modelo devuelve una lista que la página pueda leer.

## Versión mínima y cómo voy a comprobarla

La versión mínima será un `index.html` que se abre con doble clic. Tendrá un campo para pegar la consigna y otro para pegar la respuesta del modelo. Mostrará la consigna junto a la lista para poder compararlas. La página funcionará con las funciones del navegador. Para generar la lista se necesitará acceso a ChatGPT. La primera versión trabajará con texto pegado y una consigna por vez.

Voy a probar tres consignas breves de ejemplo: una con varios entregables, una con un punto opcional y una sin fecha. Antes de probarlas, anotaré a mano qué tareas espero encontrar. Compararé cada lista con ese registro para ver si omitió o inventó algo, confundió lo obligatorio con lo opcional o agregó una fecha. También comprobaré que se puedan marcar tareas y que la página avise si la respuesta pegada no contiene una lista reconocible.
