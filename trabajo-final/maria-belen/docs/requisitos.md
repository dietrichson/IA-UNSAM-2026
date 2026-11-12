# Requisitos · Copiloto de búsqueda laboral para Comunicación

Cada requisito se puede comprobar con una prueba. **Imprescindible** = versión mínima que funciona. **Si llegamos** = mejora deseable.

## Imprescindibles

| ID | Requisito |
|---|---|
| R1 | La persona puede cargar su CV pegando el texto o subiendo un archivo `.pdf`, `.docx`, `.txt` o `.md`. |
| R2 | La persona puede pegar el texto de una oferta y la app extrae título, requisitos, herramientas e idiomas. |
| R3 | La app muestra qué palabras clave de la oferta están presentes en el CV y cuáles faltan. |
| R4 | La app genera una versión del CV reordenada para la oferta usando solo información que figura en el CV original. |
| R5 | La app genera una carta de presentación para la oferta usando solo información que figura en el CV original. |
| R6 | Un verificador marca cualquier cifra, herramienta, nombre propio o título del CV adaptado o de la carta que no esté en el CV ni en la oferta. |
| R7 | La base de puestos son archivos `.md` con encabezado estructurado y tiene al menos 30 puestos de Comunicación. |
| R8 | Dado un CV, la app recupera los puestos más cercanos con embeddings (RAG) y asigna a cada uno un puntaje de 0 a 100 con criterios fijos (herramientas, experiencia, formación, cursos, idiomas). |
| R9 | La lista de puestos se muestra ordenada por puntaje, con los motivos, citas textuales del CV y las brechas de cada puesto. |
| R10 | La persona puede elegir un puesto de la base o pegar uno y ver qué herramientas y requisitos le faltan. |
| R11 | La pantalla de inicio explica qué datos se envían a un servicio externo; por defecto ningún dato sale de la computadora. |
| R12 | Cuando falla el modelo, falta Ollama o el archivo no se puede leer, la app muestra un mensaje comprensible con qué hacer. |
| R13 | Otra persona puede instalar y ejecutar el proyecto en una computadora de 8 GB de RAM siguiendo el README. |

## Importantes (forman parte del proyecto, pero la versión mínima funciona sin ellos)

| ID | Requisito |
|---|---|
| R14 | La app resume qué herramientas faltan con más frecuencia entre los mejores puestos. |
| R15 | La persona puede editar el CV y la carta generados, volver a verificarlos y descargarlos en `.txt` y `.docx`. |
| R16 | La persona puede elegir el tono de la carta (formal, cercano o creativo) y el género gramatical. |
| R17 | Un deseable que el CV no cubre no baja el puntaje; uno que sí cubre suma como «Plus». |
| R18 | Los puntajes ya calculados se guardan para no repetir llamadas al modelo, y la persona puede borrar los datos guardados. |

## Si llegamos

| ID | Requisito |
|---|---|
| R19 | La persona puede filtrar los puestos por modalidad, seniority o área. |
| R20 | La persona puede agregar un puesto nuevo a la base desde la app. |
| R21 | Existe una evaluación automática con 10 CV ficticios × 3 ofertas que mide veracidad, palabras clave, recuperación, ranking y brechas, con resultados guardados. |
| R22 | Al menos 3 personas del público destinatario prueban la app y sus problemas graves se resuelven. |
| R23 | Adaptar un CV y generar una carta tarda menos de 60 segundos con el modelo por defecto. |

## Fuera de alcance

- Enviar postulaciones o completar formularios en portales de empleo.
- Rastrear portales de empleo automáticamente; la base de puestos se arma a mano.
- **Seguimiento de postulaciones (tracker):** estaba en la propuesta inicial y se sacó del alcance para concentrarse en los otros dos módulos.
- Cuentas de usuario, base de datos compartida o versión móvil.
- Garantizar resultados o reemplazar el asesoramiento laboral profesional.
- Usar un modelo en la nube por defecto (se puede configurar, pero no se probó con servicios reales).
