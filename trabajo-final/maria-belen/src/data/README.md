# Base de puestos · Comunicación, prensa y marketing digital

Base estática del sugeridor de puestos: **40 puestos activos** en `puestos/` (un `.md` por puesto, es lo que se indexa) y **3 en `pendientes/`** (no se indexan). `base-completa.md` es una versión de lectura generada a partir de los archivos; no se edita a mano.

## De dónde sale

| Tramo | Puestos | Cómo se obtuvo |
|---|---|---|
| Relevamiento del 26/10/2026 | 12 | Avisos públicos: 3 completos de CazVid (mayo de 2024, no recientes) y 9 resúmenes de listados de Jooble, Indeed y Glassdoor |
| Primera selección aportada el 2/11/2026 | 11 | Texto completo de cada aviso, pegado a mano, sin enlace ni fecha; 4 originales en inglés, traducidos al español |
| Segunda selección aportada el 2/11/2026 | 16 | Igual que la anterior; 5 originales en inglés, traducidos al español. Se omitió un aviso repetido (Especialista en comunicación interna, ya cargado como 016) |
| Aviso de LinkedIn del 3/11/2026 | 1 | `marketing-performance-seo-043`: texto pegado a mano, con el enlace del aviso |
| `pendientes/` | 3 | Solo se conocía el título (Computrabajo e Idealist). Se sacaron de la base porque su contenido era mayormente referencia general; se reincorporan si se pega el aviso real |

Los puestos 030, 041 y 042 se ajustaron según lo indicado por quien seleccionó los avisos (ubicación Argentina y horario). El dato de salarios se eliminó de toda la base porque casi ningún aviso lo trae. También se eliminaron las secciones de "herramientas habituales del rubro": eran conocimiento general, no salían de ningún aviso, y metían ruido en la recuperación y el puntaje.

## Formato de cada puesto

Encabezado (entre `---`) con campos que el programa usa para filtrar y puntuar, y cuerpo con texto para el embedding.

| Campo | Contenido |
|---|---|
| `id`, `titulo`, `empresa`, `area` | Identificación; `area` es una de: comunicacion-institucional, comunicacion-interna, contenidos, direccion-creativa, ecommerce-contenido, marketing, marketing-digital, periodismo, prensa, produccion-audiovisual, redes-sociales, relaciones-institucionales |
| `seniority`, `experiencia` | Nivel y años que declara el aviso; si no, `no figura` |
| `titulo_universitario`, `requiere_titulo` | Texto del aviso y valor normalizado: `sí`, `deseable` o `no figura` |
| `modalidad`, `modalidad_tipo` | Texto del aviso y valor normalizado: `remoto`, `hibrido`, `presencial` o `no figura` |
| `ubicacion` | Tal como figura |
| `herramientas`, `idiomas` | Solo lo que el aviso nombra; sirve para detectar brechas |
| `lectura`, `fuente`, `publicado`, `relevado` | Cuánto se leyó (`aviso completo` o `resumen de listado`), de dónde, y fechas |
| `notas` | Qué falta, dudas y aclaraciones (no se embebe) |

Cuerpo: `# Título`, `Resumen`, `## Tareas`, `## Requisitos`, `## Herramientas`. **Todo el cuerpo se embebe**; las notas viven en el encabezado.

## Pensada para el contexto del modelo (8 GB, 4096 tokens)

Estimación propia (1,7 tokens por palabra más unos 120 del encabezado): cada puesto ocupa entre **216 y 684 tokens** (mediana 418); el más largo es `marketing-performance-seo-043`. Un CV de una página más un puesto más las instrucciones queda dentro de 4096. En cambio, la base completa suma unos **15,922 tokens** y no entra en un solo contexto, por eso se recupera con RAG y se puntúa **un puesto por llamada**. Medir con el modelo real antes de fiarse de estos números.

## Cobertura

| Dato | Puestos (de 40) |
|---|---|
| Aviso completo / resumen de listado | 31 / 9 |
| Modalidad: remoto / híbrido / presencial / no figura | 10 / 5 / 8 / 17 |
| Exige título: sí / deseable / no figura | 17 / 4 / 19 |
| Idiomas exigidos | 14 |

Áreas: redes-sociales (9), contenidos (7), marketing-digital (6), prensa (4), comunicacion-institucional (3), comunicacion-interna (2), marketing (2), relaciones-institucionales (2), periodismo (2), produccion-audiovisual (1), direccion-creativa (1), ecommerce-contenido (1).

## Límites y cuidados

- **No todo es Buenos Aires:** hay puestos en Vicente López, en la provincia de Buenos Aires, remotos con horario de España (5:00 a 6:00 a. m. en Argentina) o de EE. UU. (Mountain Time o EST) y otros sin ubicación. El campo `modalidad` lo aclara.
- **Contratación:** `consultor-relaciones-publicas-034` es por prestación de servicios; `analista-contenidos-jr-cms-040` es "remoto" pero con asistencia a la oficina dos veces por mes (se clasificó como híbrido); `pasante-marketing-hibrido-041` y `pasantia-estrategia-medios-deinsa-042` son pasantías (la primera remunerada y la segunda no).
- **Aviso con modalidad a confirmar:** `pasante-marketing-hibrido-041` dice "híbrida" en el aviso, pero se indicó que se ofrece remoto para Argentina.
- **Sesgo:** 15 de 40 son de community management, redes y marketing digital; prensa, relaciones institucionales, periodismo y comunicación interna ya tienen presencia, pero siguen siendo pocos puestos por área.
- **Avisos sin enlace ni fecha:** los 27 aportados a mano el 2/11/2026 no se pueden verificar contra una fuente; los 3 completos de CazVid son de 2024.
- **Datos que faltan** quedan como `no figura`; nunca se completaron con suposiciones.
- Los textos están resumidos con palabras propias; no se copiaron avisos completos.

## Índice

| id | Puesto | Área | Modalidad | Título | Lectura |
|---|---|---|---|---|---|
| `cm-jr-pyme-importadora-001` | Community Manager (perfil junior, PYME importadora) | redes-sociales | no figura | no figura | resumen de listado |
| `cm-compra-gamer-002` | Community Manager (especialista en contenido) | redes-sociales | no figura | no figura | resumen de listado |
| `cm-agencia-publicidad-003` | Community Manager en agencia de publicidad | redes-sociales | no figura | no figura | resumen de listado |
| `cm-sr-agencia-contenido-cultural-004` | Community Manager Sr. (contenido reactivo y tendencias culturales) | redes-sociales | no figura | no figura | resumen de listado |
| `cm-medior-agencia-turno-extendido-005` | Medior Community Manager (tardes/noches y fines de semana) | redes-sociales | no figura | no figura | resumen de listado |
| `cm-b2b-social-selling-006` | Community Manager B2B (social selling) | redes-sociales | remoto | no figura | resumen de listado |
| `cm-diseno-grafico-estudio-juridico-007` | Community Manager y Diseñador/a gráfico | redes-sociales | no figura | no figura | resumen de listado |
| `content-creator-cm-audiovisual-008` | Content Creator y Community Manager (producción audiovisual) | contenidos | no figura | no figura | resumen de listado |
| `cm-presencial-vicente-lopez-009` | Community Manager (presencial, zona norte del GBA) | redes-sociales | presencial | no figura | resumen de listado |
| `social-media-manager-remoto-010` | Social Media Manager (remoto) | redes-sociales | remoto | no figura | aviso completo |
| `especialista-marketing-digital-comunicacion-011` | Especialista en Marketing Digital y Comunicación (remoto) | contenidos | remoto | no figura | aviso completo |
| `asistente-comunicacion-prensa-012` | Asistente de Comunicación y Prensa (remoto) | prensa | remoto | sí | aviso completo |
| `comunicacion-interna-especialista-016` | Especialista en comunicación interna | comunicacion-interna | no figura | sí | aviso completo |
| `copywriter-remoto-argentina-017` | Copywriter (remoto, Argentina) | contenidos | remoto | no figura | aviso completo |
| `digital-marketing-associate-fever-018` | Digital Marketing Associate | marketing-digital | no figura | sí | aviso completo |
| `editor-video-ugc-ia-019` | Editor/a de video UGC e IA (AI & UGC Video Editor) | produccion-audiovisual | remoto | no figura | aviso completo |
| `junior-digital-marketing-remoto-espana-020` | Junior Digital Marketing Specialist (100 % remoto) | marketing-digital | remoto | sí | aviso completo |
| `creador-contenido-retail-021` | Creador/a de contenido | contenidos | no figura | sí | aviso completo |
| `director-creativo-hibrido-022` | Director/a creativo/a (Creative Director) | direccion-creativa | hibrido | no figura | aviso completo |
| `asistente-ecommerce-contenido-moda-023` | Asistente de e-commerce y contenido digital | ecommerce-contenido | presencial | deseable | aviso completo |
| `asistente-comunicacion-institucional-024` | Asistente de Comunicación Institucional | comunicacion-institucional | no figura | sí | aviso completo |
| `analista-marketing-consumo-masivo-025` | Analista de marketing | marketing | no figura | no figura | aviso completo |
| `paid-search-especialista-remoto-026` | Especialista en búsqueda paga (Paid Search Marketing Specialist) | marketing-digital | remoto | no figura | aviso completo |
| `responsable-prensa-facultad-027` | Responsable de prensa y comunicación (facultad universitaria) | prensa | no figura | sí | aviso completo |
| `ejecutivo-cuentas-comunicacion-028` | Ejecutivo/a de cuentas (comunicación) | comunicacion-institucional | presencial | sí | aviso completo |
| `asistente-relaciones-institucionales-eventos-029` | Asistente de relaciones institucionales y eventos | relaciones-institucionales | presencial | deseable | aviso completo |
| `seo-geo-especialista-030` | Especialista en SEO y GEO (SEO Specialist) | marketing-digital | remoto | deseable | aviso completo |
| `productor-periodistico-031` | Productor/a periodístico/a | periodismo | presencial | sí | aviso completo |
| `corrector-textos-b2b-est-032` | Corrector/a de textos B2B (Proofreader) | contenidos | no figura | no figura | aviso completo |
| `gerente-relaciones-institucionales-caba-033` | Gerente/a de relaciones institucionales | relaciones-institucionales | hibrido | deseable | aviso completo |
| `consultor-relaciones-publicas-034` | Consultor/a de relaciones públicas | prensa | no figura | no figura | aviso completo |
| `asistente-comunicacion-universidad-035` | Asistente de comunicación institucional (universidad) | comunicacion-institucional | presencial | sí | aviso completo |
| `analista-comunicacion-prensa-palermo-036` | Analista de comunicación y prensa | prensa | presencial | sí | aviso completo |
| `pasante-comunicaciones-pfizer-037` | Pasante de comunicaciones (Communications Intern) | comunicacion-interna | presencial | sí | aviso completo |
| `redactor-periodistico-038` | Redactor/a periodístico/a | periodismo | no figura | sí | aviso completo |
| `especialista-contenidos-adtech-039` | Especialista en contenidos (content specialist, adtech) | contenidos | no figura | no figura | aviso completo |
| `analista-contenidos-jr-cms-040` | Analista de contenidos Jr. (Content Analyst Jr) | contenidos | hibrido | sí | aviso completo |
| `pasante-marketing-hibrido-041` | Pasante de marketing | marketing | hibrido | sí | aviso completo |
| `pasantia-estrategia-medios-deinsa-042` | Pasantía en estrategia de medios (Media Strategy) | marketing-digital | remoto | sí | aviso completo |
| `marketing-performance-seo-043` | Especialista en marketing de performance y SEO (Marketing Performance Specialist SEO) | marketing-digital | hibrido | sí | aviso completo |

## Uso con el RAG

- Indexar `puestos/*.md` completos (el encabezado se descarta o se usa solo para metadatos).
- Filtros: `modalidad_tipo`, `requiere_titulo`, `area`.
- Brechas: comparar `herramientas` e `idiomas` del puesto con el CV.
