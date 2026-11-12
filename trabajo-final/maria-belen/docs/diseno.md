# Diseño · Copiloto de búsqueda laboral para Comunicación

## Piezas del sistema y cómo se conectan

```
Navegador (Streamlit)         app/main.py + app/paginas/ (Inicio, Sugeridor, Adaptador)
        │
        ▼
Servicios (Python)            servicios/
  cv_parser · oferta_parser   leen CV (PDF/DOCX/texto) y ofertas → datos estructurados
  recuperador                 RAG: vectores de los puestos y del CV, devuelve los más cercanos
  matcher                     puntaje 0–100 por criterios (LLM + reglas)
  brechas                     qué falta para un puesto y qué falta más seguido
  adaptador                   CV adaptado y carta (solo con hechos del CV)
  verificador                 detecta datos no respaldados por el CV
  formacion · vocabulario ·   reglas escritas a mano: equivalencias de carreras, sinónimos de
  genero                      herramientas, género gramatical
  llm_client                  único punto de contacto con el modelo: reintentos, JSON validado, tiempos
        │
        ├── Ollama: qwen2.5:3b (generación) y bge-m3 (embeddings)
        ├── data/puestos/*.md  (base de 40 puestos)
        └── data/local/        (caché y CV guardado, solo en la computadora de la persona)
```

Las páginas solo muestran datos y recogen entradas; la lógica está en `servicios/`, por eso se puede probar sin abrir la app.

## Herramientas, modelos y datos

| Qué | Elección | Por qué |
|---|---|---|
| Lenguaje e interfaz | Python + Streamlit | Subida de archivos y tablas ya resueltas; corre en el navegador sin escribir front-end |
| Modelo de generación | `qwen2.5:3b` con Ollama | Entra en 8 GB de RAM, es gratis y los datos no salen del equipo |
| Embeddings | `bge-m3` con Ollama (alternativa: `nomic-embed-text`) | Multilingüe; el RAG del seminario también usó Ollama |
| Proveedor configurable | `.env` (`LLM_PROVIDER`: ollama, gemini o claude) | Permite cambiar de modelo sin tocar el código; solo está probado Ollama |
| Base de puestos | 40 archivos `.md` con encabezado (herramientas, idiomas, modalidad, requisitos…) | Editable a mano; `no figura` marca lo que el aviso no trae |
| Prompts | Archivos en `prompts/` | Versionados; cambiar un prompt invalida el caché solo |
| Datos de prueba | 2 CV ficticios en `data/ejemplos/`; 10 CV × 3 ofertas en `evaluacion/casos/` | Sin CV reales en el repositorio |

## Decisiones de diseño que importan

- **El modelo es chico, así que no se le deja decidir solo.** Herramientas e idiomas se puntúan con reglas; experiencia y formación las estima el modelo y se corrigen con reglas (pisos, topes, equivalencias de carrera). Pesos: herramientas 31, experiencia 37, formación 16, cursos 6, idiomas 10. Lo que un puesto no pide no se puntúa y su peso se reparte.
- **Excluyente por defecto:** un requisito es excluyente salvo que el aviso lo marque como deseable («plus», «se valora», «suma»…). Los deseables no restan: suman hasta 10 puntos de bonus.
- **Un puesto por llamada:** con contexto de 4096 tokens, la base completa no entra, y por eso se usa RAG.
- **Veracidad por diseño:** el prompt prohíbe agregar datos, el verificador compara la salida con el CV y la app muestra lo que no pudo respaldar para que la persona lo corrija.
- **El texto de CV y ofertas es dato, no instrucción:** va delimitado y el modelo no ejecuta acciones, solo produce texto o JSON que se valida.

## Quién hace qué

Proyecto individual. María Belén eligió y definió el proyecto, armó y curó la base de puestos, probó la app con su CV y con CV de ejemplo, y decidió qué entra y qué no. El código se escribió con ayuda de un asistente de IA (Claude), que propuso la implementación y los arreglos que ella fue pidiendo a partir de sus pruebas.

## Primera versión y lo que queda para después

- **Primera versión (la mínima):** carga de CV y oferta, palabras clave, CV adaptado y carta con verificador, y sugeridor con RAG, puntaje, motivos y brechas.
- **Se sumó después:** reglas de formación y cursos, deseables y plus, idiomas por nivel, género de la carta, exportar a `.docx`, caché de puntajes.
- **Para después:** filtros por seniority y área, agregar puestos desde la app, evaluación completa con criterio de una persona del rubro, pruebas con usuarias reales, probar Gemini y Claude, y mejorar la velocidad.
