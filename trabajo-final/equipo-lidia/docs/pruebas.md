# Pruebas – Equipo Lidia

Las pruebas se realizaron sobre la versión final de *El Profe Histérico*, disponible como un único archivo HTML que puede abrirse directamente desde una computadora.

## Requisitos imprescindibles

### R1. Partida de 10 preguntas, banco de al menos 40 y sin repetición
**Cómo se probó:** se realizaron partidas completas. El banco contiene más de 40 preguntas y en cada partida se seleccionan 10 sin repetir.  
**Resultado:** Funciona.

### R2. Cuatro formatos de preguntas
**Cómo se probó:** se probaron opción múltiple, posta o mito, ordenar acontecimientos y adivinar un año.  
**Resultado:** Funciona.

### R3. Preguntas con fotografías
**Cómo se probó:** el juego incluye preguntas con fotografías y textos alternativos. Las fuentes y licencias todavía deben completarse.  
**Resultado:** Funciona a medias.

### R4. Explicaciones, fuentes y verificación
**Cómo se probó:** las preguntas incluyen una explicación después de responder. Queda pendiente completar el registro de fuentes y verificación por dos integrantes.  
**Resultado:** Funciona a medias.

### R5. Tres niveles de apuesta
**Cómo se probó:** se probaron Tiro al voleo, Más o menos y Seguro y se verificaron sus distintos puntajes.  
**Resultado:** Funciona.

### R6. Apuesta y seguridad del profesor
**Cómo se probó:** antes de cada respuesta se muestran la apuesta y el porcentaje de seguridad del profesor.  
**Resultado:** Funciona.

### R7. Resultados después de cada pregunta
**Cómo se probó:** se muestran la respuesta correcta, las respuestas de ambos participantes y los puntos obtenidos.  
**Resultado:** Funciona.

### R8. Tres comodines
**Cómo se probó:** se probaron 50/50, Chusmear al profe y Doble o nada.  
**Resultado:** Funciona.

### R9. Medidor de histeria
**Cómo se probó:** se comprobó que cambia durante la partida según los resultados.  
**Resultado:** Funciona.

### R10. Frases generadas mediante LLM
**Cómo se probó:** el proyecto contempla el uso de Ollama + qwen2.5, pero la versión HTML autónoma puede funcionar utilizando frases de respaldo. Falta verificar una partida completa con al menos cinco frases generadas por el modelo.  
**Resultado:** Funciona a medias.

### R11. Frases de respaldo
**Cómo se probó:** se comprobó que el juego puede continuar utilizando frases predeterminadas cuando la IA no está disponible.  
**Resultado:** Funciona.

### R12. Prueba de 30 frases del modelo
**Cómo se probó:** queda pendiente ejecutar y registrar la prueba definitiva de 30 frases generadas mediante Ollama.  
**Resultado:** Funciona a medias.

### R13. Protección del acceso a la IA
**Cómo se probó:** la lógica prevista evita exponer directamente el acceso al modelo desde el navegador.  
**Resultado:** Funciona.

### R14. Respuestas del profesor por probabilidad
**Cómo se probó:** se comprobó que los aciertos del profesor se calculan según la dificultad y no dependen del LLM.  
**Resultado:** Funciona.

### R15. Personalización del personaje
**Cómo se probó:** se probaron las opciones de género, peinados, colores de pelo y ropa.  
**Resultado:** Funciona.

### R16. Accesorios y nombre
**Cómo se probó:** se probaron los accesorios y el ingreso de un nombre para el jugador.  
**Resultado:** Funciona.

### R17. Personaje durante la partida y al final
**Cómo se probó:** el personaje aparece durante el juego y en el boletín, con diferentes expresiones.  
**Resultado:** Funciona.

### R18. Boletín final
**Cómo se probó:** se verificaron los resultados, nota, puntaje y mejor puntaje al finalizar.  
**Resultado:** Funciona.

### R19. Sello, animación y sonidos
**Cómo se probó:** se comprobó el funcionamiento del sello final, las animaciones y los efectos de sonido.  
**Resultado:** Funciona.

### R20. Nueva partida sin recargar
**Cómo se probó:** se utilizó la opción para volver a jugar desde el final.  
**Resultado:** Funciona.

### R21. Música y control de sonido
**Cómo se probó:** se probó la música de fondo y la posibilidad de silenciarla.  
**Resultado:** Funciona.

### R22. Efectos de sonido
**Cómo se probó:** se verificaron distintos efectos durante la partida.  
**Resultado:** Funciona.

### R23. Computadora y celular
**Cómo se probó:** el juego funciona correctamente en computadora. En celular no puede jugarse correctamente.  
**Resultado:** Funciona a medias.

### R24. Navegación mediante teclado
**Cómo se probó:** se comprobó el uso de los controles mediante teclado y el foco visible.  
**Resultado:** Funciona.

## Requisitos adicionales

### R25. Barra de progreso
**Cómo se probó:** el juego muestra el número de pregunta actual, pero no posee una barra gráfica específica.  
**Resultado:** No funciona.

### R26. Botón de ayuda
**Cómo se probó:** las reglas aparecen al comienzo, pero no existe un botón de ayuda durante la partida.  
**Resultado:** No funciona.

### R27. Comentarios finales
**Cómo se probó:** existen reacciones diferentes según si el jugador gana, pierde o empata.  
**Resultado:** Funciona.

### R28. Copiar resultado
**Cómo se probó:** el resultado final puede copiarse.  
**Resultado:** Funciona.

### R29. Dos estilos visuales
**Cómo se probó:** el juego utiliza un único estilo visual.  
**Resultado:** No funciona.

## Resultado general

La versión final permite jugar una partida completa directamente desde un único archivo HTML en una computadora.

El principal problema de funcionamiento pendiente es la adaptación a celulares.

También quedan pendientes algunos aspectos de documentación y verificación:

- completar las fuentes y la verificación de las preguntas;
- completar las fuentes y licencias de las fotografías;
- ejecutar y registrar la prueba de 30 frases con Ollama.
