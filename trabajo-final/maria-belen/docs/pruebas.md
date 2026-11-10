# Pruebas · Copiloto de búsqueda laboral para Comunicación

## Cómo se probó

1. **Tests automáticos (201):** `python -m pytest -q` desde `src/`. Usan modelos simulados, así que verifican la lógica (puntajes, reglas, verificador, caché, pantallas, lectura de archivos) y **no** la calidad del modelo real.
2. **Pruebas a mano con `qwen2.5:3b` real**, hechas por María Belén en GitHub Codespaces con Ollama, con dos tipos de datos:
   - **CV real y ofertas reales:** su propio CV en PDF (con experiencia en fotografía, retoque y community management) y ofertas reales de Comunicación y marketing digital, pegadas a mano o tomadas de la base de puestos. El flujo completo (cargar el CV, adaptar el CV, escribir la carta, ver puestos sugeridos y brechas) funcionó de punta a punta.
   - **CV ficticios:** el CV junior de ejemplo (Camila) y ofertas armadas para provocar casos difíciles, como «Asistente. Requisitos: Curso de Marketing Digital. Canva. Suma inglés intermedio.».

   Cada problema encontrado se corrigió y se agregó un test para que no vuelva.

**Qué no se hizo:** la evaluación con 10 CV × 3 ofertas contra el criterio de una persona del rubro, la prueba con 3 personas y la medición formal de tiempos. Los casos y el evaluador existen (`src/evaluacion/`), pero no hay resultados guardados.

## Resultados por requisito

| Requisito | Cómo se probó | Resultado |
|---|---|---|
| R1 Cargar CV (texto, PDF, DOCX, TXT, MD) | Tests de lectura de cada formato; CV real propio en PDF a mano | Funciona: el CV real en PDF se leyó bien, sin tener que pegar el texto. Un PDF escaneado (imagen) no se puede leer: en ese caso hay que pegar el texto |
| R2 Extraer datos de una oferta | Tests con modelo simulado; ofertas pegadas a mano | Funciona a medias: el modelo chico a veces omite o duplica requisitos, por eso formación, experiencia y cursos se leen también con reglas |
| R3 Palabras clave presentes y faltantes | Tests y prueba a mano | Funciona |
| R4 CV adaptado solo con datos del CV | Prueba a mano con el CV real propio y ofertas reales | Funciona: el «Sobre mí» copiaba lo que pedía la oferta y el CV salía sin títulos de sección ni orden; se corrigió con el ajuste del prompt (ronda 3f) y se verificó a mano. El modelo chico igual puede omitir contenido, por eso hay que leer el resultado antes de usarlo |
| R5 Carta solo con datos del CV | Prueba a mano con el CV real propio y ofertas reales | Funciona a medias: no siempre lee «B2» como «intermedio»; el género y las categorías de herramientas se corrigen con reglas |
| R6 Verificador de datos no respaldados | Tests; prueba a mano | Funciona: marcó una herramienta que no estaba en el CV (Canva). Da falsos positivos, por ejemplo con un error de tipeo corregido por el modelo («Parti-time») |
| R7 Base de 30 o más puestos en `.md` | Revisión de la carpeta y tests de carga | Funciona: 40 puestos activos (y 3 pendientes sin indexar) |
| R8 RAG y puntaje 0–100 por criterios | Tests; prueba a mano con el CV de Camila y ofertas | Funciona a medias: el puntaje es coherente con los casos revisados, pero no se midió contra el criterio de una persona del rubro |
| R9 Lista ordenada con motivos, citas y brechas | Tests de pantalla; prueba a mano con CV real y ficticio | Funciona |
| R10 Brechas de un puesto elegido o pegado | Tests; prueba a mano con ofertas reales pegadas | Funciona |
| R11 Aviso de qué datos salen | Tests de la pantalla de inicio | Funciona |
| R12 Mensajes de error comprensibles | Tests con Ollama falso (sin servidor, sin modelo, JSON inválido) | Funciona |
| R13 Instalación con el README en 8 GB | Descomprimir el zip en una carpeta limpia, instalar y correr tests; uso en Codespaces | Funciona a medias: no se probó en otra computadora de 8 GB real; es lento sin placa de video |
| R14 Brechas más frecuentes | Tests; prueba a mano | Funciona |
| R15 Editar, revisar y descargar `.txt` y `.docx` | Tests de exportación y de pantalla | Funciona |
| R16 Tono de la carta y género | Tests; prueba a mano | Funciona |
| R17 Deseables no restan, suman como «Plus» | Tests; ofertas con «suma», «plus» y «se valora» | Funciona |
| R18 Caché de puntajes y borrado de datos | Tests; prueba a mano (un caché viejo mostró resultados desactualizados hasta cambiar la versión de la clave) | Funciona |
| R19 Filtros por modalidad, seniority o área | Revisión de la pantalla | Funciona a medias: solo hay filtro por modalidad |
| R20 Agregar puestos desde la app | — | No funciona: no se implementó |
| R21 Evaluación sistemática con 10 CV × 3 ofertas | El evaluador (`src/evaluacion/`) y los 30 casos ficticios existen y se probaron en modo simulado | Funciona a medias: el script y los casos corren, pero no se hicieron las corridas con el modelo real ni la comparación con el criterio de una persona del rubro. Las pruebas a mano con el CV real propio están en las filas R1 a R10; esta fila se refiere a la medición formal (porcentajes de veracidad, palabras clave, ranking y brechas) |
| R22 Prueba con 3 personas | — | No funciona: no se hizo |
| R23 Menos de 60 segundos | Uso a mano; sin medición formal | No funciona: con 8 GB y sin GPU cada llamada tarda de 1 a 3 minutos |

## Problemas encontrados en las pruebas y qué se hizo

Cada punto surgió de usar la app y se corrigió con cambios en el código o en los prompts, más un test para que no vuelva.

**Herramientas**
- Herramientas duplicadas o con sinónimos («Canva» y «Diseño en Canva y/o Adobe», «Adobe» y «Adobe Creative Suite») → se cuentan una vez; «y/o» se lee como alternativas.
- Una herramienta que el CV sí tiene aparecía como brecha (contradicción entre herramientas y brechas) → las brechas del modelo sobre cosas ya cubiertas se descartan.
- «Inglés» aparecía a la vez como herramienta e idioma, y repetido en «Plus» → los idiomas salen de las listas de herramientas.
- Categorías mal puestas en la carta («herramientas de IA como Excel», «ofimática» en lugar de «informática») → categorías fijas, regla en el prompt y verificador.

**Puntaje**
- Seniority puntuado dos veces, como criterio propio y dentro de experiencia → se sacó como criterio aparte.
- El nombre del puesto contado como requisito faltante → el título ya no cuenta como requisito.
- Todo lo que un puesto no pide bajaba el puntaje → los criterios que no aplican no se puntúan y su peso se reparte.
- Experiencia: un puesto que no la exige («sin experiencia», pasantías, «0 a 2 años») no suma ni resta; Meta Ads, Google Ads y campañas pagas cuentan como experiencia en publicidad o marketing digital.
- Deseables que restaban → los requisitos son excluyentes salvo que el aviso diga «deseable», «plus», «se valora», «suma» u «opcional»; un deseable faltante no resta y uno cubierto suma como «Plus» (hasta 10 puntos).
- «Suma inglés intermedio» se trataba como excluyente → pasó a deseable.
- Idiomas: se compara el nivel (avanzado cubre intermedio) y solo es brecha si falta el idioma o el nivel es menor.

**Formación y cursos**
- La formación de ofertas pegadas a mano no se leía → se extrae del texto por reglas, junto con los años de experiencia.
- Graduado vs. estudiante, y carreras no afines con 81 % (Tecnicatura en imagen fotográfica, Contador Público) → equivalencias de carrera, niveles de estudio, piso 85 si coincide, rango 35 a 50 si falta el título y tope 20 si la carrera no coincide.
- Falsos positivos: «Radio de la facultad» contaba como estudio y los años sueltos como «graduado» → se acotaron las palabras que indican estudios.
- Los cursos no se evaluaban, o un curso que el CV sí tenía figuraba como brecha con 83 puntos → los cursos y certificaciones se evalúan aparte con poco peso; curso y diplomatura son equivalentes; el mismo curso repetido en la oferta se cuenta una vez.
- «Por dónde empezar» hablaba de experiencia en un curso faltante → ahora sugiere sumar o mostrar el curso pedido.

**Adaptador de CV y carta**
- Requisito «Estudiante avanzado» listado como faltante → se compara por carrera equivalente y nivel, no palabra por palabra.
- Salida repetida (triplicada) → se quitan las repeticiones y se avisa.
- Carta con «o/a» o con el género equivocado → el género se detecta del CV o se elige, y se escribe en una sola forma.
- CV adaptado con «Sobre mí» copiado de la oferta, sin títulos de sección ni orden → prompt con estructura (Sobre mí, Experiencia, Formación, Herramientas e idiomas), orden cronológico inverso y viñetas (ronda 3f).

**Otros**
- Un resultado viejo seguía apareciendo tras corregir el código (caché) → la clave del caché incluye una versión de la lógica.
