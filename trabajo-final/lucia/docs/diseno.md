# Diseño: Ta-te-ti con comentarista deportivo

**Autora:** Lucia Ruiz Serman

**Seminario Experimental de Inteligencia Artificial (UNSAM)**

## Las piezas del sistema y cómo se conectan

El proyecto tiene cuatro piezas:

1. **La página del juego** (HTML y JavaScript). Muestra el tablero de 3x3, recibe los clics de la persona, aplica las reglas del ta-te-ti y hace jugar al rival al azar. También muestra el relato en pantalla.
2. **Un programa intermediario** (Python), que corre en mi computadora. Recibe de la página lo que pasó en cada jugada, arma el pedido para la LLM y le devuelve a la página el relato.
3. **El modelo de lenguaje**, que corre en mi computadora con Ollama. Recibe el pedido (el *system prompt* de relator y los datos de la jugada) y escribe el relato.
4. **Un registro de partidas** (archivo CSV). El programa intermediario guarda una fila por cada jugada narrada, para poder revisarlas después.

El recorrido de cada jugada es este:

```
Persona hace clic en una casilla
        ↓
Página del juego: aplica la jugada, juega el rival, revisa si hay victoria o empate
        ↓
Página → Programa intermediario: tablero, quién jugó, casilla, resultado (sigue / gana X / gana O / empate)
        ↓
Programa intermediario → LLM (Ollama): system prompt de relator + datos de la jugada
        ↓
LLM → Programa intermediario: el relato (1 o 2 oraciones)
        ↓
Programa intermediario: guarda la fila en el CSV y devuelve el relato a la página
        ↓
Página: muestra el relato debajo del tablero
```

Las reglas y el resultado de la partida los calcula siempre la página, no la IA. La LLM solo recibe esos datos ya resueltos y los cuenta.

## Herramientas, modelos y datos

- **Página:** HTML y JavaScript, sin librerías externas.
- **Programa intermediario:** Python, con herramientas básicas (sin instalar nada complicado).
- **Modelo de lenguaje:** un modelo chico de la familia Qwen 2.5 (por ejemplo, la versión de 1.500 millones de parámetros) corriendo con **Ollama** en mi computadora. Elijo un modelo chico porque mi computadora tiene recursos limitados y porque no necesito que sea muy inteligente para contar una jugada.
- **Plan B:** si el modelo elegido no anda bien en mi computadora, pruebo uno todavía más chico. Cualquier cambio se anota en el ticket de implementación.
- **Datos:** un archivo `partidas.csv` con las columnas partida, número de jugada, tablero, quién jugó, casilla, resultado y relato. Después le agrego a mano dos columnas: si el relato fue fiel (sí o no) y qué error tuvo. De ahí salen las tablas de `pruebas.md`.
- **Código y archivos:** todo va a `trabajo-final/lucia/src/`. No se suben claves ni archivos grandes (el modelo no se sube al repositorio).

## Quién hace qué

El proyecto es individual: yo defino las decisiones, pruebo y reviso los resultados, y me apoyo en un asistente de IA para escribir el código y entender cómo correrlo. La revisión de los relatos (jugada por jugada) la hago yo, sin ayuda de la IA.

## Qué entra en la primera versión y qué queda para después

**Primera versión que funciona:**
- La página con el tablero y las reglas, contra un rival al azar (R1, R2).
- El programa intermediario conectado a Ollama, con un solo relator de fútbol (R3, R4, R5).
- El registro de las jugadas en el CSV, para poder revisarlas (R8).
- Instrucciones escritas para correr todo (R9).

**Queda para después (si llegamos):**
- Elegir entre relator de fútbol y de hockey (R10).
- Comparar dos versiones del *system prompt* (R11).
- Botón de nueva partida (R12).

**Se va a probar así:** con la primera versión funcionando, juego 10 partidas, reviso cada relato y completo la tabla de `pruebas.md` (R6, R7, R8).
