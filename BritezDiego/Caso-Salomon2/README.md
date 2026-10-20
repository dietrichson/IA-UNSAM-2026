# El caso Salomón 2 — La jueza con IA (segunda prueba piloto)

Juego de decisiones legales con una jueza que usa Claude y un RAG sobre el caso y las leyes.
Reconstrucción educativa basada en la sentencia de la Cámara Civil (2018) y notas periodísticas; no es asesoramiento legal.

## Modos
- **Fácil:** el relato inicial y 8 preguntas con opciones.
- **Difícil:** el mismo relato y las 8 preguntas se responden escribiendo; la jueza (IA) comenta qué tan sólido queda el caso y dicta una sentencia final según todas las respuestas.

## Cómo ejecutarlo (en Codespaces)
    pip install anthropic
    export ANTHROPIC_API_KEY="tu-clave"      # opcional; sin clave funciona en modo sin IA
    python3 servidor.py

Abrí el puerto 8000 desde la pestaña Puertos. Para guardar la clave de forma permanente: GitHub → Settings → Codespaces → Secrets → New secret (`ANTHROPIC_API_KEY`). Nunca la pongas en el código.

## Archivos
- `servidor.py`: sirve el juego, hace la búsqueda (RAG, BM25) en `corpus/` y llama a Claude.
- `corpus/`: textos que la jueza puede consultar (hechos del caso, Constitución y tratados, Código Civil, doctrina).
- `rubrica.json`: criterio ideal de cada pregunta (lo usa la jueza; el navegador no puede verlo).
- `datos.js`, `main.js`, `index.html`, `estilos.css`: el juego.

Para cambiar lo que sabe la jueza, editá o agregá archivos `.md` en `corpus/` (secciones con `## Título`) y reiniciá el servidor.
