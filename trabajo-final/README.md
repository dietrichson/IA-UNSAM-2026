# Trabajo final

Acá viven los proyectos finales del seminario. Cada equipo (o persona que trabaja
sola) tiene su propia carpeta en este directorio y su propio **milestone** en
GitHub con los tickets de su proyecto.

## Equipos

| Carpeta | Integrantes | Milestone en GitHub |
|---|---|---|
| `equipo-sofi/` | Sofía, Rosario, Agostina | Trabajo final — Equipo Sofi |
| `equipo-lidia/` | Lidia, Lola, Carolina, Emma | Trabajo final — Equipo Lidia |
| `maria-belen/` | María Belén | Trabajo final — María Belén |
| `erika/` | Erika | Trabajo final — Erika |
| `diego/` | Diego | Trabajo final — Diego |
| `jeremias/` | Jeremías | Trabajo final — Jeremías |
| `juan-marcos-gatti/` | Juan Marcos Gatti | Trabajo final — Juan Marcos Gatti |

## Cómo trabajamos

El trabajo final se lleva como un proyecto de software de verdad, en versión
chica. Todos los proyectos pasan por las mismas cinco etapas, y cada etapa es un
**ticket** (issue) en GitHub dentro del milestone del equipo:

1. **Propuesta** — qué vamos a hacer y para quién.
2. **Requisitos** — qué tiene que hacer el proyecto para estar terminado.
3. **Diseño** — cómo lo vamos a construir: herramientas, modelos, piezas.
4. **Implementación** — construirlo, en versiones chicas que funcionen.
5. **Pruebas y entrega** — comprobar que hace lo que prometimos, documentar y presentar.

Reglas simples:

- Se trabaja una etapa a la vez, en orden. Una etapa se cierra cuando el docente
  la aprueba en el ticket.
- Todo lo que se produce se sube por **pull request** a la carpeta del equipo.
  El PR menciona el ticket al que corresponde (por ejemplo `Cierra #12`).
- Las conversaciones sobre el proyecto van en el ticket, no por chat ni mail.
  Así queda todo registrado y cualquiera del equipo puede seguirlo.
- Cada ticket dice qué hay que entregar y cuándo se considera listo.

## Estructura de la carpeta de cada equipo

```
trabajo-final/equipo-sofi/
├── README.md          ← qué es el proyecto y cómo correrlo (se completa al final)
├── docs/
│   ├── propuesta.md   ← etapa 1
│   ├── requisitos.md  ← etapa 2
│   ├── diseno.md      ← etapa 3
│   └── pruebas.md     ← etapa 5
└── src/               ← el código, los Modelfiles, los prompts, los datos chicos
```

- Nombres de carpetas y archivos en minúsculas, sin espacios ni tildes, con
  guiones: `mi-archivo.md`.
- Al repo van archivos chicos. Datos grandes (más de ~10 MB) o modelos no se
  suben: se deja un link en el README del proyecto.
- Nunca se suben claves, contraseñas ni tokens.
