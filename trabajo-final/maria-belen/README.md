# Copiloto de búsqueda laboral para Comunicación

Trabajo final del seminario de IA · María Belén Martínez Contardi · 2026

## Qué es

Una aplicación web que corre en tu computadora y ayuda a estudiantes y graduados/as de Comunicación a buscar trabajo. Tiene dos módulos:

- **Sugeridor de puestos (RAG):** cargás tu CV y la app busca, en una base de 40 puestos, los más parecidos, los puntúa con criterios fijos (herramientas, experiencia, formación, cursos e idiomas) y te dice qué te falta para cada uno.
- **Adaptador de CV y carta:** pegás una oferta, la app te muestra qué palabras clave ya tenés y cuáles no, adapta tu CV y escribe una carta usando **solo** lo que figura en tu CV. Un verificador marca lo que no está respaldado.

Es gratis y local: usa [Ollama](https://ollama.com) con `qwen2.5:3b` (generación) y `bge-m3` (embeddings). No necesita cuentas ni claves, y tu CV no sale de tu computadora.

La documentación del trabajo está en `docs/`: [propuesta](docs/propuesta.md), [requisitos](docs/requisitos.md), [diseño](docs/diseno.md) y [pruebas](docs/pruebas.md). El código y su README técnico están en [`src/`](src/README.md).

## Cómo correrlo

Necesitás Python 3.10 o superior, Ollama instalado y abierto, unos 8 GB de RAM y unos 3 GB de disco para los modelos.

```bash
cd src
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

ollama pull qwen2.5:3b
ollama pull bge-m3

streamlit run app/main.py
```

Se abre en `http://localhost:8501`. La pantalla de inicio tiene que decir «Todo listo»; si falta algo, muestra el comando exacto. Para una prueba rápida elegí «Usar un ejemplo» → «CV ficticio: junior». Hay una guía de 15 minutos en `src/README.md`.

Los tests automáticos no necesitan Ollama: `pip install -r requirements-dev.txt` y `python -m pytest -q` (201 tests).

## Qué funciona y qué no

**Funciona:** se probó de punta a punta con un CV real en PDF y ofertas reales: carga de CV (texto, PDF, DOCX), extracción de palabras clave, CV adaptado y carta con verificador, descarga en `.txt` y `.docx`, sugeridor con RAG, puntaje por criterios, brechas por puesto y resumen de brechas frecuentes, filtro por modalidad, caché de puntajes y borrado de datos.

**Funciona a medias:**
- Un modelo de 3.000 millones de parámetros puede omitir contenido del CV, redactar flojo o devolver datos mal armados. Por eso hay reglas, reintentos y verificador, pero conviene leer siempre el resultado antes de usarlo.
- El verificador prefiere avisar de más: puede marcar nombres legítimos.
- Los puntajes son orientativos y no se compararon con el criterio de una persona del rubro.

**No funciona o no se hizo:**
- Es lento: sin placa de video, cada consulta tarda de 1 a 3 minutos (la meta de menos de 60 segundos no se cumple).
- No agrega puestos desde la app ni filtra por seniority o área.
- No hay seguimiento de postulaciones (se sacó del alcance), ni envío automático, ni rastreo de portales.
- No se hizo la evaluación con 10 CV × 3 ofertas ni la prueba con 3 personas. Gemini y Claude están implementados como alternativas, pero no se probaron con servicios reales.
- Un PDF escaneado (imagen) no se lee: hay que pegar el texto.

El detalle por requisito está en [docs/pruebas.md](docs/pruebas.md).

## Qué aprendimos

- **Un modelo chico necesita andamios.** Pedirle todo al modelo no alcanzó: lo que se puede decidir con reglas (herramientas, idiomas, equivalencias de carrera, cursos) se resolvió con reglas, y el modelo quedó para lo que requiere leer texto libre.
- **Probar con casos reales encuentra lo que los tests no.** Casi todos los errores aparecieron al usar la app con CV y ofertas reales; cada uno se convirtió en un test.
- **Un caché necesita versión.** Un resultado guardado con una lógica vieja se siguió mostrando después de arreglar el código, hasta que la clave del caché incluyó una versión.
- **Honestidad por diseño.** Un verificador que avisa de más es preferible a un generador que inventa sin que nadie lo note.
- **Evaluar no es lo mismo que probar.** Los tests dicen que el código hace lo que se espera; medir la calidad requiere casos y criterio humano, y eso quedó pendiente.

## Privacidad

Con Ollama, el CV y las ofertas no salen de la computadora. La app guarda un caché y, si lo pedís, tu CV en `src/data/local/`, que se borra desde **Inicio → Borrar datos guardados** y no se publica. Los CV incluidos son ficticios. Si configurás Gemini o Claude, el texto se envía a ese proveedor y la app lo avisa.
