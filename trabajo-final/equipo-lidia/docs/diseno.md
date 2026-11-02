# Diseño – Equipo Lidia

## 1. Piezas del sistema y cómo se conectan

- **Juego web:** desarrollado con HTML, CSS y JavaScript. Incluye las pantallas, la personalización del personaje, preguntas, apuestas, comodines, puntajes, medidor de histeria, sonidos y boletín final.

- **Banco de preguntas:** almacenado en `preguntas.json`, con las preguntas, respuestas, explicaciones, dificultad e imágenes cuando corresponde.

- **Lógica del profesor:** sus respuestas se calculan mediante probabilidades según la dificultad. La inteligencia artificial no decide si acierta o falla.

- **Servicio de IA:** desarrollado en Python con Flask. Comunica el juego con Ollama.

- **Frases de reserva:** si el modelo falla o tarda más de cinco segundos, se utilizan frases de `frases_reserva.json`.

Estas partes se conectan durante la partida de la siguiente manera: el juego toma las preguntas del banco, aplica la lógica de puntajes, apuestas, comodines e histeria y, cuando necesita una reacción del profesor, consulta al servicio de IA. Si ese servicio no responde, utiliza las frases de reserva.

## 2. Herramientas, modelos y datos

- **HTML:** estructura de las pantallas.
- **CSS:** diseño visual, personajes y adaptación a distintos tamaños.
- **JavaScript:** lógica del juego, puntajes, preguntas, apuestas, comodines y sonidos.
- **Python + Flask:** servicio que comunica el juego con la inteligencia artificial.
- **Ollama + qwen2.5:** generación de las frases del profesor.
- **`preguntas.json`:** banco de preguntas.
- **`frases_reserva.json`:** frases predeterminadas de respaldo.
- **CSV:** registro de fuentes y licencias.
- **Imágenes:** utilizadas en preguntas de reconocimiento de personajes.
- **GitHub:** organización, almacenamiento y documentación del proyecto.

## 3. Quién hace qué

### Carolina Romano – Desarrollo del juego

Se encarga principalmente del desarrollo técnico del proyecto: programación de la interfaz, lógica de las preguntas, apuestas, comodines, puntajes, personalización, boletín final e integración del sistema de reacciones.

### Lidia Ortiz Vázquez – GitHub y documentación

Se encarga de organizar el repositorio, subir los archivos del proyecto, mantener la estructura de carpetas y actualizar la documentación correspondiente a las distintas etapas.

### Dolores Mujica – Contenido y fuentes

Se encarga de la revisión de preguntas, respuestas y explicaciones, además del control de fuentes e imágenes utilizadas en el juego.

### Emma Wolfsteller – Pruebas y control de calidad

Se encarga de realizar partidas de prueba, comprobar los distintos formatos de preguntas, revisar el funcionamiento general y detectar posibles errores.

## 4. Primera versión funcional y qué queda para después

### Primera versión funcional

La primera versión funcional incluye:

- partidas de diez preguntas sin repetición;
- banco de más de 40 preguntas;
- cuatro formatos de preguntas;
- preguntas con fotografías;
- tres niveles de apuesta;
- tres comodines;
- puntajes y medidor de histeria;
- reacciones del profesor mediante un LLM;
- frases de reserva si la IA falla;
- personalización del personaje;
- boletín final con nota y puntaje;
- música y efectos de sonido;
- funcionamiento en computadora;
- navegación mediante teclado.

### Para después

Quedan como posibles mejoras:

- mejor adaptación a celulares;
- barra de progreso;
- botón de ayuda;
- nuevos comentarios finales del profesor;
- opción para copiar y compartir el resultado;
- dos estilos visuales diferentes.
