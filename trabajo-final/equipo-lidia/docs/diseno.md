Etapa 3: Diseño del sistema
Piezas del sistema y cómo se conectan
Juego web: desarrollado con HTML, CSS y JavaScript. Incluye las pantallas, la personalización del personaje, preguntas, apuestas, comodines, puntajes, medidor de histeria, sonidos y boletín final.
Banco de preguntas: almacenado en preguntas.json, con las preguntas, respuestas, explicaciones, dificultad e imágenes cuando corresponde.
Lógica del profesor: sus respuestas se calculan mediante probabilidades según la dificultad. La inteligencia artificial no decide si acierta o falla.
Servicio de IA: desarrollado en Python con Flask. Comunica el juego con Ollama.
Frases de reserva: si el modelo falla o tarda más de cinco segundos, se utilizan frases de frases_reserva.json.

Herramientas, modelos y datos
Herramienta o recurso
Uso
HTML
Estructura de las pantallas
CSS
Diseño visual, personajes y adaptación a distintos tamaños
JavaScript
Lógica del juego, puntajes, preguntas, apuestas, comodines y sonidos
Python + Flask
Servicio que comunica el juego con la IA
Ollama + qwen2.5
Generación de frases del profesor
preguntas.json
Banco de preguntas
frases_reserva.json
Frases predeterminadas de respaldo
CSV
Registro de fuentes y licencias
Imágenes
Preguntas de reconocimiento de personajes
GitHub
Organización y documentación del proyecto


 Quién hace qué
Integrante
Rol principal
Tareas
Carolina Romano
Desarrollo del juego
Programación de la interfaz, lógica de preguntas, apuestas, comodines, puntajes, personalización, boletín e integración del sistema de reacciones.
Lidia Ortiz Vázquez
GitHub y documentación
Organización del repositorio, carga de archivos y mantenimiento de la documentación del proyecto.
Dolores Mujica
Contenido y fuentes
Revisión de preguntas, respuestas, explicaciones, fuentes e imágenes.
Emma Wolfsteller
Pruebas y control de calidad
Pruebas de partidas completas, formatos de preguntas, navegadores, computadora, teclado y funcionamiento general.


Primera versión funcional y qué queda para después
Primera versión funcional
Incluye:
Partidas de diez preguntas sin repetición.
Banco de más de 40 preguntas.
Cuatro formatos de preguntas.
Preguntas con fotografías.
Tres niveles de apuesta.
Tres comodines.
Puntajes y medidor de histeria.
Reacciones del profesor mediante un LLM.
Frases de reserva si la IA falla.
Personalización del personaje.
Boletín final con nota y puntaje.
Música y efectos de sonido.
Funcionamiento en computadora.
Navegación mediante teclado.
Para después
Quedan como posibles mejoras:
Mejor adaptación a celulares.
Barra de progreso.
Botón de ayuda.
Nuevos comentarios finales del profesor.
Opción para copiar y compartir el resultado.
Dos estilos visuales diferentes.
