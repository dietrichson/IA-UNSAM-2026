# El Profe Histérico

## Qué es el proyecto

*El Profe Histérico* es un juego web de cultura general argentina desarrollado por Equipo Lidia.

El jugador compite contra un profesor de historia de personalidad exagerada y humorística. Durante una partida de diez preguntas, ambos responden, apuestan puntos y acumulan resultados mientras cambia el medidor de histeria del profesor.

El juego incluye:

- cuatro formatos de preguntas;
- tres niveles de apuesta;
- tres comodines;
- sistema de puntajes;
- medidor de histeria;
- personalización del personaje;
- música y efectos de sonido;
- reacciones del profesor;
- boletín final.

La inteligencia artificial se utiliza para generar algunas reacciones del profesor. Cuando el modelo no está disponible, el juego utiliza frases de respaldo para que la partida pueda continuar.

## Cómo correr el juego

La versión final del juego se encuentra en:

`trabajo-final/equipo-lidia/src/El Profe Histérico - Versión Final.html`

Para jugar desde GitHub:

1. Entrar en la carpeta `trabajo-final/equipo-lidia/src/`.
2. Abrir el archivo `El Profe Histérico - Versión Final.html`.
3. Seleccionar la opción **Descargar archivo sin procesar**.
4. Una vez descargado el archivo HTML en la computadora, abrirlo con un navegador web.
5. El juego se abrirá y se podrá comenzar una partida.

No es necesario instalar programas adicionales para jugar la versión autónoma.

La versión final está contenida en un único archivo HTML, lo que facilita su descarga y ejecución desde una computadora.

## Qué funciona

La versión final funciona correctamente en computadora y permite:

- completar partidas de diez preguntas;
- utilizar cuatro formatos de preguntas;
- elegir entre tres niveles de apuesta;
- utilizar tres comodines;
- competir contra el profesor;
- visualizar los puntajes;
- utilizar el medidor de histeria;
- personalizar el personaje;
- ingresar un nombre;
- escuchar música y efectos de sonido;
- silenciar el sonido;
- visualizar el boletín final;
- guardar el mejor puntaje;
- comenzar una nueva partida;
- copiar el resultado final;
- continuar jugando aunque la inteligencia artificial no esté disponible.

## Qué no funciona o queda pendiente

El principal problema pendiente es la adaptación a dispositivos móviles.

Actualmente el juego funciona correctamente en computadora, pero no puede jugarse de manera adecuada desde un celular.

También quedan pendientes algunos aspectos de documentación y verificación:

- completar el registro de fuentes y verificación de las preguntas;
- completar las fuentes y licencias de las fotografías;
- ejecutar y registrar la prueba de 30 frases generadas mediante Ollama.

Los requisitos adicionales que no se incorporaron son:

- barra gráfica de progreso;
- botón de ayuda durante la partida;
- dos estilos visuales diferentes.

## Qué aprendimos

Durante el desarrollo aprendimos que crear un proyecto implica avanzar sobre distintas versiones, probarlas y corregir los problemas que aparecen durante el uso.

Partimos de una primera versión funcional y posteriormente incorporamos música, efectos de sonido, cambios de tipografía, mejoras en los personajes, nuevas opciones de personalización y ajustes visuales.

Uno de los principales problemas que encontramos fue que la versión final dependía de distintos archivos externos y no siempre podía abrirse fácilmente desde una computadora. Para solucionarlo reorganizamos el proyecto y generamos una versión final en un único archivo HTML, más simple de descargar, abrir y probar.

También aprendimos a utilizar GitHub para organizar archivos, trabajar con distintas versiones y registrar los cambios mediante pull requests.

La incorporación de inteligencia artificial nos permitió comprender que un modelo puede utilizarse para una función específica sin hacer depender todo el juego de él. Por eso las reacciones del profesor pueden utilizar inteligencia artificial, mientras que las reglas, preguntas, puntajes y resultados permanecen controlados por el juego.

Finalmente, aprendimos que la documentación, las pruebas, las fuentes y la organización del trabajo son parte del proyecto tanto como la programación.
