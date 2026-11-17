# Etapa 5: Pruebas y Entrega

## Tabla de Validación de Requisitos

| Requisito | Cómo se probó | Resultado |
| :--- | :--- | :--- |
| **Interfaz y tablero interactivo** (`index.html`) | Se abrió el archivo en el navegador web (Chrome) y se hizo clic en cada una de las 9 casillas para verificar la respuesta visual y el estado del tablero. | Funciona |
| **Alternancia de turnos** | Se jugó una partida completa verificando que el sistema alterne correctamente entre los turnos (X y O) sin saltar jugadas. | Funciona |
| **Prevención de jugadas inválidas** | Durante una partida en curso, se intentó hacer clic sobre una casilla que ya había sido marcada previamente para confirmar que el sistema la bloquea. | Funciona |
| **Detección de victoria (tres en línea)** | Se completaron líneas horizontales, verticales y diagonales para comprobar que el juego detecte correctamente al ganador. | Funciona |
| **Detección de empate** | Se llenaron todas las casillas del tablero sin formar tres en línea para verificar que se muestre el estado de empate. | Funciona |
| **Narración / Comentarista deportivo** | Se verificó que los mensajes e intervenciones del comentarista acompañen el desarrollo de la partida, las jugadas clave y el desenlace. | Funciona |
| **Reinicio de partida** | Al finalizar una partida, se probó la opción de reiniciar para limpiar el tablero y comenzar un nuevo encuentro. | Funciona |