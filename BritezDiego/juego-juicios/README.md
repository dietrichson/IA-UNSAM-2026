# El caso Salomón — Juego de decisiones legales (prueba piloto)

Juego 2D de navegador: relato animado de lo ocurrido el 6 y 7 de octubre de 2004 y juicio con 8 preguntas
en las que el jugador defiende a la actora. Según sus respuestas, la sentencia es favorable, parcial o rechazada.

Reconstrucción educativa basada en la sentencia de la Cámara Civil (Sala B, 24/05/2018) y en notas periodísticas.
Las voces del juzgado (jueza y abogado de las demandadas) son ficticias. No es asesoramiento legal.

## Cómo abrirlo

En una terminal, dentro de esta carpeta:

    python3 -m http.server 8002

Después abrí http://localhost:8002 (en Codespaces: pestaña Puertos, puerto 8002).

## Archivos

- index.html: pantallas y escenario del programa
- estilos.css: colores y animaciones
- datos.js: personajes, relato, preguntas y veredictos (acá se edita el contenido)
- main.js: lógica del juego
