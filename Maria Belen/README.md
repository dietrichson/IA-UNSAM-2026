# Copiloto de búsqueda laboral para Comunicación

App que corre en el navegador, pensada para estudiantes y graduados/as de Comunicación. Tiene dos módulos:

- **Sugeridor de puestos (RAG):** cargás tu CV y la app busca, en una base de 40 puestos, los más parecidos, los puntúa con criterios fijos (herramientas, experiencia, formación, seniority, idiomas) y te dice qué te falta para cada uno.
- **Adaptador de CV y carta:** pegás una oferta y la app te muestra qué palabras clave ya tenés y cuáles no, adapta tu CV y escribe una carta usando **solo** lo que figura en tu CV. Un verificador marca cualquier cifra, herramienta, nombre propio o título que no esté respaldado.

Es **gratis y local por defecto**: usa [Ollama](https://ollama.com) en tu computadora (modelo `qwen2.5:3b`), sin cuentas ni claves.

**Qué no hace:** no envía postulaciones, no entra a portales de empleo, no guarda un seguimiento de postulaciones y no reemplaza el asesoramiento laboral. Los puntajes son orientativos.

---

## 1. Requisitos

- Python **3.10 o superior** (`python --version`; se probó con 3.13).
- [Ollama](https://ollama.com/download) instalado y abierto.
- Unos 8 GB de memoria RAM (alcanza, justo). Cerrá otros programas pesados mientras la usás. No hace falta placa de video, pero va a ser lento (ver «Límites»).
- Espacio en disco para los modelos: unos 3 GB.

## 2. Instalación

Desde la carpeta del proyecto:

```bash
# 1) Dependencias de Python (recomendado, dentro de un entorno virtual)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Modelos en Ollama (una sola vez; con Ollama abierto)
ollama pull qwen2.5:3b             # el modelo que escribe y puntúa
ollama pull bge-m3                 # el modelo que convierte textos en vectores (RAG)

# 3) Ejecutar
streamlit run app/main.py
```

Se abre en `http://localhost:8501`. No hace falta crear un `.env`: los valores por defecto ya son estos. Si querés cambiar algo, copiá `.env.example` como `.env`.

Si `bge-m3` te resulta pesado, usá `ollama pull nomic-embed-text` y agregá `EMBEDDINGS_MODELO=nomic-embed-text` al `.env`.

## 3. Cómo probarla (guía rápida, 15 minutos)

1. **Inicio:** tiene que decir «Todo listo» en verde. Si dice «Falta algo para empezar», muestra el comando exacto que falta (por ejemplo `ollama pull bge-m3`). Leé «¿Qué pasa con mis datos?» y tocá **Entendido, empezar**.
2. **Sugeridor de puestos:** elegí «Usar un ejemplo» → «CV ficticio: junior». Dejá **3** puestos para puntuar en el control deslizante y tocá **Buscar puestos**.
   - La primera vez prepara la base de puestos (es más lento; después queda guardada).
   - Esperable: una lista de 3 puestos con barra de puntaje, y un desplegable «Ver detalle y brechas» con citas de tu CV.
   - Cosas para mirar: ¿los puestos tienen sentido para ese CV? ¿Las citas están realmente en el CV? ¿Las brechas son razonables?
3. **¿Qué me falta para un puesto?** (al final de esa pantalla): elegí un puesto de la lista y tocá **Ver brechas**.
4. **Adaptador de CV y carta:** con el mismo CV de ejemplo, pegá una oferta (podés usar una de `evaluacion/casos/ofertas/`), tocá **Analizar oferta** y revisá las palabras clave. Después **Adaptar mi CV** y **Escribir la carta**.
   - Esperable: «Verificado» en verde, o una tarjeta naranja «Revisá esto» con lo que el modelo agregó y tu CV no tiene.
   - Probá editar el texto, tocar **Revisar mi edición** y descargarlo en `.txt` y `.docx`.
5. Probá con **tu propio CV** (pegado o en PDF/DOCX). Si tildás «Recordar mi CV», queda guardado solo en tu computadora.

Tiempos esperables sin placa de video (estimación, no medición): cada consulta al modelo puede tardar de 1 a 3 minutos; puntuar 3 puestos, entre 3 y 9 minutos la primera vez. Los resultados ya calculados se guardan y repetirlos es instantáneo.

## 4. Tests automáticos

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Los tests **no necesitan Ollama**: usan modelos simulados y un servidor Ollama falso. Verifican la lógica (puntajes, verificador, caché, pantallas), **no** la calidad del modelo real.

## 5. Evaluación (criterios del documento de requisitos)

```bash
# Prueba rápida del evaluador, sin modelo (no mide calidad real):
python -m evaluacion.evaluar --simulado --cvs cv-01-camila-rojas --n 3

# Evaluación real (con Ollama abierto). Empezá chico:
python -m evaluacion.evaluar --que recuperacion ranking --cvs cv-01-camila-rojas cv-02-tomas-benitez
python -m evaluacion.evaluar                      # todo: puede tardar horas sin placa de video
```

- Los casos están en `evaluacion/casos/`: **10 CV ficticios × 3 ofertas ficticias**.
- Para medir recuperación, ranking y palabras clave faltantes hace falta que **una persona del rubro** complete `evaluacion/casos/esperados.json` (hasta 3 puestos elegidos por CV y la lista de faltantes por oferta). Hasta entonces esas métricas dicen «Sin datos».
- La veracidad se mide con el verificador automático y se revisa a mano en una muestra de 10 casos (`...-revision-veracidad.md`). Las brechas se revisan a mano en 15 casos (`...-revision-brechas.csv`).
- Cada corrida guarda en `evaluacion/resultados/` un informe `.md`, el detalle `.json`, proveedor, modelo y **versión de prompts**, además de cantidad y duración de las llamadas al modelo (sin guardar el contenido de CV). Para comparar proveedores, repetí la corrida cambiando `LLM_PROVIDER` en el `.env`.

## 6. Privacidad

- Con Ollama (por defecto) tu CV y las ofertas **no salen de tu computadora**.
- Si activás Gemini o Claude en el `.env`, el texto del CV y de la oferta **se envía a ese proveedor**; la app lo avisa en la pantalla de inicio. Revisá sus términos y, para probar, usá CV ficticios.
- La app guarda en `data/local/` (solo si lo permitís): un caché de puntajes (incluye frases de tu CV usadas como evidencia) y, si lo pedís, tu CV. Se borran desde **Inicio → Borrar datos guardados**.
- `.gitignore` excluye `.env`, `data/local/` y el índice. Solo se publican datos ficticios.
- Las claves de API se leen solo del `.env` o del entorno, nunca llegan al navegador.
- El texto del CV y de las ofertas se trata como **dato, no como instrucciones**: está delimitado y el modelo nunca ejecuta acciones, solo produce texto o JSON que se valida.

## 7. Límites conocidos

- **Velocidad:** con 8 GB y sin GPU, `qwen2.5:3b` es lento. La meta de «menos de 60 segundos» del documento de requisitos **probablemente no se cumpla** con la configuración por defecto; por eso se puntúan 5 puestos (no 10) y se guardan los resultados.
- **Calidad:** un modelo de 3.000 millones de parámetros puede equivocarse, devolver JSON inválido o inventar. Por eso hay validación con reintento, citas verificadas contra el CV y un verificador de datos inventados. El verificador prefiere avisar de más: puede marcar nombres legítimos (falsos positivos).
- **Puntaje:** herramientas e idiomas se calculan con reglas; experiencia, formación y seniority las estima el modelo. No se compara el nivel de idioma. Si un puesto no detalla herramientas (17 de los 40), ese criterio no se puntúa y su peso se reparte.
- **Base de puestos:** 40 avisos públicos relevados entre el 26/10 y el 3/11/2026; es una muestra, no el mercado, y puede estar desactualizada (ver `data/README.md`).
- **Sin probar con servicios reales:** los proveedores Gemini y Claude están implementados pero solo se probó el armado de los pedidos, no las llamadas a sus servidores. Tampoco se midió el comportamiento de `qwen2.5:3b` real.
- **PDF:** solo se lee texto seleccionable; un PDF escaneado (imagen) no funciona: pegá el texto.
- Con `OLLAMA_NUM_CTX=4096` los textos largos se recortan (CV a 5.000 caracteres, oferta a 4.000) y la app lo avisa.

## 8. Solución de problemas

| Síntoma | Qué hacer |
|---|---|
| «No encuentro Ollama» | Abrí la aplicación de Ollama o ejecutá `ollama serve`, y tocá «Revisar de nuevo». |
| «Falta descargar…» | Ejecutá el `ollama pull` que indica el mensaje. |
| La búsqueda es muy lenta | Bajá la cantidad de puestos a puntuar, cerrá otros programas, esperá: la segunda vez usa el caché. |
| «El modelo no devolvió un JSON válido» | Reintentá; si se repite, probá `LLM_MODELO_PRINCIPAL=qwen2.5:7b` (más lento y pesado) o un proveedor en la nube. |
| El cambio de estilo no se ve | Detené la app (Ctrl+C) y volvé a ejecutarla. |
| Quiero rehacer el índice de puestos | Borrá los archivos de `data/indice/`; se regenera solo. |

## 9. Estructura

```
app/            interfaz (Streamlit): main.py, estilo.py (8 bits pastel), componentes.py, paginas/
servicios/      lógica: llm_client, cv_parser, oferta_parser, recuperador, matcher, brechas, adaptador, verificador, exportar
prompts/        los prompts, como archivos de texto editables
data/puestos/   base de 40 puestos en .md (con encabezado estructurado)
data/ejemplos/  CV ficticios de ejemplo
evaluacion/     casos de prueba, evaluador y resultados
tests/          pruebas automáticas
```

## 10. Licencias de las fuentes

Las tipografías Press Start 2P y Pixelify Sans están bajo licencia SIL Open Font License 1.1 (ver `app/static/LICENCIAS-FUENTES.txt`).
