**Equipo Lidia – Segunda etapa del trabajo final**

*El Profe Histérico* es un juego web de cultura general argentina en el que el jugador compite contra un profesor de historia con una personalidad exagerada y humorística. Durante la partida, ambos responden preguntas, apuestan puntos y el profesor reacciona a los resultados mediante inteligencia artificial.

## Requisitos imprescindibles [M]

### Partida y preguntas

**R1 [M].** Cada partida incluye 10 preguntas seleccionadas aleatoriamente de un banco de al menos 40, sin repetir ninguna.

**R2 [M].** El juego incluye cuatro formatos de preguntas: opción múltiple, posta o mito, ordenar acontecimientos y adivinar un año, con al menos tres formatos diferentes por partida.

**R3 [M].** Cada partida incluye al menos dos preguntas para reconocer personajes mediante fotografías, con textos alternativos que no revelan la respuesta y fuentes y licencias registradas.

**R4 [M].** Todas las preguntas incluyen una breve explicación y sus datos son verificados por al menos dos integrantes del equipo, con las fuentes registradas en el repositorio.

### Reglas del juego

**R5 [M].** Antes de responder, el jugador elige entre tres apuestas (tiro al voleo, más o menos y seguro), que modifican su puntaje según una tabla presentada al inicio.

**R6 [M].** Antes de cada respuesta, el profesor muestra su apuesta y su porcentaje de seguridad.

**R7 [M].** Después de cada pregunta se muestran la respuesta correcta, las respuestas de ambos participantes y los puntos obtenidos, actualizando automáticamente el marcador.

**R8 [M].** El jugador dispone de tres comodines de un solo uso por partida: 50/50, chusmear al profe y doble o nada.

**R9 [M].** Un medidor de histeria aumenta cuando alguno de los participantes falla y disminuye cuando ambos aciertan.

### El profesor y la inteligencia artificial

**R10 [M].** El profesor reacciona a los aciertos y errores con frases humorísticas generadas por un LLM, configurado con instrucciones sobre su personalidad, y al menos cinco frases de cada partida provienen del modelo.

**R11 [M].** Si la inteligencia artificial falla o tarda más de cinco segundos, el juego utiliza frases predeterminadas sin interrumpir la partida ni mostrar errores.

**R12 [M].** Se realiza y registra en el repositorio una prueba de 30 frases generadas, verificando que no incluyan insultos graves, discriminación ni referencias a política partidaria.

**R13 [M].** La clave de acceso a la inteligencia artificial permanece protegida y no aparece en el código del navegador.

**R14 [M].** El profesor responde las preguntas mediante probabilidades de acierto según su dificultad, sin depender del LLM para decidir las respuestas.

### Personalización del jugador

**R15 [M].** Antes de jugar, el usuario puede elegir género femenino o masculino, cinco peinados por género, cuatro colores de pelo y cinco colores de ropa, visualizando los cambios en una vista previa.

**R16 [M].** El personaje dispone de al menos cuatro accesorios combinables, salvo los incompatibles, y el jugador puede ingresar un nombre opcional que el profesor utilizará en sus comentarios.

**R17 [M].** El personaje aparece en el marcador y en el boletín final, cambiando su expresión según los aciertos y errores.

### Final de la partida

**R18 [M].** Al finalizar, aparece un boletín con los aciertos por materia, los aciertos totales de ambos participantes, el puntaje final, la nota sobre 10 y el mejor puntaje guardado en ese navegador.

**R19 [M].** El boletín incluye un sello rojo animado con la nota, respetando la configuración de movimiento reducido del dispositivo, y sonidos de papel y golpe de sello.

**R20 [M].** El jugador puede comenzar otra partida desde el boletín sin recargar la página.

### Sonido y funcionamiento

**R21 [M].** El juego incluye música de fondo que comienza tras la primera interacción, un botón para silenciarla en todas las pantallas y la opción de recordar esa preferencia sin afectar el funcionamiento si no se puede guardar.

**R22 [M].** El juego incluye efectos de sonido diferentes para respuestas correctas, incorrectas, victorias y derrotas.

**R23 [M].** El juego funciona en computadoras y celulares de 400 píxeles de ancho, sin desplazamiento horizontal, y es compatible con las versiones actuales de Chrome y Firefox sin instalación ni registro.

**R24 [M].** Todas las pantallas pueden utilizarse mediante el teclado y los botones seleccionados muestran claramente el foco.

## Requisitos adicionales: si llegamos [S]

**R25 [S].** Incorporar una barra de progreso que indique cuántas preguntas faltan para terminar la partida.

**R26 [S].** Agregar un botón de ayuda para consultar las reglas y el funcionamiento de los comodines durante el juego.

**R27 [S].** Incorporar nuevos comentarios humorísticos del profesor al finalizar la partida, según si el jugador gana, pierde o empata.

**R28 [S].** Agregar una opción para copiar y compartir el resultado final de la partida.

**R29 [S].** Permitir que el jugador elija entre dos estilos visuales para cambiar la apariencia del juego.

## Fuera de alcance

Para este proyecto decidimos no incluir:

- Registro de usuarios, rankings en línea ni partidas multijugador.
- Desarrollo de una aplicación móvil descargable.
- Generación automática de preguntas sin revisión humana.
- Uso de imágenes sin licencia verificada o preguntas sobre política partidaria actual.
- Versiones del juego en otros idiomas.
