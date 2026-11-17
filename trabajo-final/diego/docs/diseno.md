# Diseño

## Arquitectura

    Navegador (index.html + main.js + datos.js)
            |  fetch /api/evaluar, /api/sentencia, /api/estado
            v
    servidor.py  ──>  RAG: búsqueda BM25 en corpus/*.md
            |
            └──>  Proveedor de IA (se elige solo):
                    1. Claude (SDK de Anthropic)   si hay ANTHROPIC_API_KEY
                    2. Ollama local                si está encendido
                    3. Modo sin IA (reglas locales) si no hay ninguno

El navegador solo muestra el juego. Todo lo que requiere la clave, el corpus o la rúbrica vive en el servidor.

## Componentes

- **Interfaz** (`index.html`, `estilos.css`, `main.js`): pantallas de inicio, personajes, relato animado, juzgado y resultado. Dibujos en SVG, sin imágenes externas.
- **Contenido** (`datos.js`): personajes, seis escenas del relato, 8 preguntas con tres opciones (2, 1 y 0 puntos) y su explicación, veredictos y línea de tiempo real.
- **Servidor** (`servidor.py`): sirve los archivos, expone tres rutas y coordina RAG e IA. Bloquea `rubrica.json`, `servidor.py` y `corpus/` para el navegador.
- **Corpus** (`corpus/`): cuatro archivos en Markdown (hechos y trámite del caso, Constitución y tratados, Código Civil, doctrina), cada uno dividido en secciones `## Título`.
- **Rúbrica** (`rubrica.json`): para cada pregunta, el criterio ideal y su explicación; la jueza lo usa para puntuar y el navegador no lo ve.

## RAG

1. Al iniciar, el servidor divide cada archivo del corpus en trozos por sección (`## `).
2. Normaliza el texto (minúsculas, sin tildes, sin palabras vacías, plurales simples) y arma un índice BM25.
3. Ante cada argumento, busca los trozos más relacionados con el tema, la pregunta y la respuesta (4 trozos con Claude; 2 o 3 con modelo local, recortados, para acelerar).
4. Esos trozos se pasan al modelo como CONTEXTO y se devuelven al navegador como "material consultado".

**Decisión:** BM25 en lugar de embeddings, porque el corpus es chico (unos 20 trozos), no requiere servicios externos y funciona igual en modo sin IA. Queda como mejora usar `nomic-embed-text` (Ollama) para buscar por significado.

## La jueza

- **Personalidad** (prompt de sistema): serena, formal, exigente e imparcial; trata de "usted" y de "doctor/a".
- **Reglas:** fundar solo en el CONTEXTO; citar fuentes entre corchetes; no inventar artículos, fallos, fechas ni cifras; no hablar en nombre de personas reales; no usar "correcto/incorrecto"; no anticipar la sentencia.
- **Contrato de respuesta (JSON):**
  - Evaluación: `{"comentario": "...", "puntos": 0|1|2}`.
  - Sentencia: `{"resultado": "favorable|parcial|rechazada", "titulo": "...", "texto": "...", "consejo": "..."}`.
- **Rúbrica de puntos:** 2 = cubre lo esencial del criterio ideal con fundamento; 1 = lo cubre en parte o sin fundamento; 0 = ausente, errónea, afirma hechos falsos o ataca a las personas.
- **Coherencia:** a cada evaluación se le pasan las respuestas anteriores para que la jueza detecte contradicciones. La sentencia recibe todo el desarrollo; como guía, 75 % o más suele ser favorable, 40 a 75 % parcial y menos de 40 % rechazada.

## Modelos y por qué

| Camino | Modelo | Motivo |
|--------|--------|--------|
| Claude (SDK) | `claude-haiku-5-5` por defecto | Rápido y barato; se puede cambiar con `MODELO_JUEZA`. |
| Ollama | el primer modelo que conversa (por ejemplo `qwen2.5:3b`) | Gratis y local. Se descartan los modelos de embeddings y los de personajes. |
| Sin IA | reglas locales | Respaldo: el juego nunca se rompe. |

Para acelerar el modelo local se reducen el contexto y la salida máxima, se mantiene el modelo cargado (`keep_alive`) y se lo precarga al iniciar el servidor.

## Seguridad

La clave solo se lee de una variable de entorno y no se guarda en ningún archivo. Si la IA falla, el servidor lo registra y responde en modo sin IA.

## Diseño visual

Estilo de juzgado: madera oscura, papel color pergamino, grises y bronce, tipografías con serifa. En el juzgado, la jueza va al centro, la parte actora a la izquierda, la demandada a la derecha, y la pregunta y la respuesta en el medio, sin necesidad de desplazarse.

## Alternativas descartadas

- Publicar en GitHub Pages: no permite ejecutar un servidor ni proteger una clave.
- Llamar a la IA desde el navegador: expondría la clave.
- Embeddings desde el inicio: más complejidad sin beneficio con un corpus tan chico.

## Trabajo futuro

Más casos con selector de niveles, búsqueda con embeddings, agentes para el abogado contrario y la clienta, y revisión del corpus por una persona del área jurídica.
