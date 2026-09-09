# Laboratorio 3: Silicon sampling

> Consigna propuesta por Thiago ([@akathiago](https://github.com/akathiago)) para la clase
> invitada del 07/09/2026, adaptada de [`tarea/consigna.md`](https://github.com/akathiago/clase-silicon-sampling/blob/main/tarea/consigna.md)
> y [`tarea/rubrica.md`](https://github.com/akathiago/clase-silicon-sampling/blob/main/tarea/rubrica.md)
> en [akathiago/clase-silicon-sampling](https://github.com/akathiago/clase-silicon-sampling).

En la clase de Silicon Sampling vimos que una muestra sintética —perfiles de personas
inventados y "entrevistados" por un LLM— se arma en cinco minutos y produce números de
aspecto convincente. También vimos que esos números, contrastados contra datos reales de
consumo de noticias en Argentina, fallaban en las tres cosas que medimos.

Ahora te toca a vos. La idea no es que te salga bien. La idea es que veas fallar tu propia
muestra y puedas explicar exactamente **dónde** y **por qué**.

> **Se evalúa que sepas por qué tu muestra no sirve, no que la muestra sirva.**
> Un trabajo que dice "me dio bastante parecido a la realidad" sin haber comparado contra
> nada vale menos que uno que muestra un desastre y lo analiza.

## Objetivo

- Generar una muestra sintética con un LLM: tres personas ficticias, mismo prompt, mismo
  modelo.
- Detectar en tus propias respuestas los signos de homogeneidad, estereotipo y ausencia de
  matices que hacen que una muestra sintética no reemplace a una encuesta real.
- Proponer contra qué fuente real contrastarías esos resultados, y con qué precisión.
- Decidir, con argumentos propios, si usarías esta técnica en tu propio trabajo de
  investigación.

## Qué necesitás

Este laboratorio no usa Ollama ni Codespaces. Alcanza con:

- Un navegador.
- Una cuenta gratuita de ChatGPT o de Claude (la versión gratuita de cualquiera de los dos
  sirve).

No hace falta instalar nada ni pagar ninguna suscripción.

## Qué tenés que hacer

### 1. Elegí una pregunta

Una sola pregunta sobre **consumo mediático o consumos culturales** que te interese de
verdad. Puede ser algo cercano a tu tema de tesis, o algo que te dé curiosidad.

Ejemplos, por si no se te ocurre nada: cómo se entera la gente de las noticias locales de su
barrio · qué hacen cuando les llega algo dudoso por WhatsApp · si miran streaming de noticias
y qué les parece · qué pasó con la radio en su casa · a quién le creen y a quién no.

### 2. Definí tres perfiles

Tres personas sintéticas que sean **bien distintas entre sí**. Distintas en al menos tres de
estas dimensiones: edad, género, lugar de residencia, ocupación, nivel educativo, nivel de
ingreso.

Escribí cada perfil en dos o tres líneas, antes de abrir el chat. Si improvisás el perfil
mientras escribís el prompt, después no vas a poder analizar qué causó qué.

### 3. Corrélos

En ChatGPT o Claude, la versión gratuita alcanza.

> ⚠️ **Cada perfil va en un chat nuevo y en blanco.** Si corrés los tres en la misma
> conversación, el modelo se contamina con lo que ya escribió y las tres respuestas se van a
> parecer más de lo que se parecerían de otro modo. Es el error más común y arruina el
> ejercicio.

Hacele a cada perfil **la misma pregunta, con la misma redacción**. Si cambiás una palabra
entre un perfil y otro, ya no estás comparando personas: estás comparando prompts.

**Recomendado, vale como punto extra:** corré uno de los tres perfiles **dos veces**, en dos
chats distintos, con el prompt idéntico. Comparar esas dos corridas te va a dar la mitad del
análisis regalada.

### 4. Guardá todo

Copiá y pegá, tal cual salió, sin editar ni corregir: los prompts textuales, las respuestas
completas, el nombre del modelo y la fecha. Eso es el anexo.

### 5. Escribí una carilla

Tiene que responder estas cuatro preguntas. No hace falta que uses subtítulos, pero las
cuatro tienen que estar.

**a) ¿Qué encontraste?**
Qué te contestaron los tres perfiles. Dos o tres oraciones, no transcribas.

**b) ¿Qué te resultó sospechosamente homogéneo, prolijo o estereotipado?**
El corazón del trabajo. Buscá concretamente:

- ¿Los tres dicen lo mismo con distinto vocabulario?
- ¿Cada perfil consume exactamente el medio que "le corresponde"?
- ¿Alguno dice "no sé", se contradice, se va de tema o contesta con desgano? ¿Por qué no?
- ¿Aparece algún medio, plataforma o programa que exista de verdad y sea reciente? ¿Cuáles
  faltan?
- Si corriste el mismo perfil dos veces: ¿cuánto se parecen entre sí las dos corridas?

Citá el fragmento exacto que te hizo sospechar. Un ejemplo concreto vale más que tres
párrafos de generalidades.

**c) ¿Contra qué fuente real lo contrastarías?**
Nombrá una fuente concreta y decí **qué dato específico** buscarías en ella y **cómo
tendrías que haber redactado tu pregunta** para que la comparación fuera legítima.
Fuentes disponibles: Digital News Report (capítulo Argentina), Encuesta Nacional de Consumos
Culturales del SINCA (tiene microdatos descargables), datos.gob.ar.
Si conseguís el dato y hacés la comparación, mejor. Si no llegás, alcanza con que expliques
con precisión cómo la harías.

**d) ¿Lo usarías en tu propia tesis?**
Sí o no, y por qué. Si es que sí: en qué rol exacto (pretest, exploración, generación de
hipótesis), y qué límites declararías en el apartado metodológico. Si es que no: qué te lo
impide.
**No hay respuesta correcta.** Hay respuestas fundamentadas y respuestas que no.

### Qué NO hace falta

- No hace falta que tu muestra se parezca a la realidad.
- No hace falta que uses estadística.
- No hace falta pagar ninguna suscripción.
- No hace falta leer toda la bibliografía de la clase. Si querés citar algo, Lin (2025) es lo
  más legible y lo que mejor ordena la discusión.

## Para entregar

Un PDF con dos partes:

1. **Análisis**: una carilla, las cuatro preguntas de la sección anterior.
2. **Anexo**: los tres perfiles tal como los escribiste, los prompts textuales, las
   respuestas completas sin editar, y el modelo y la fecha en que lo corriste.

Los trabajos sin anexo no se corrigen: el registro del procedimiento *es* el trabajo.

## Rúbrica

Cuatro criterios de 25 puntos. Total 100. Se aprueba con 60.

| Criterio | 23–25 | 18–22 | 13–17 | 6–12 | 0–5 |
|---|---|---|---|---|---|
| **1. Rigor en el registro del procedimiento** — ¿se puede reconstruir exactamente lo que hizo? | Anexo completo: los tres perfiles escritos antes de correr, prompts textuales, respuestas sin editar, modelo y fecha. Los tres perfiles se corrieron en chats separados y lo aclara. La pregunta es idéntica en los tres. | Anexo completo pero falta un dato menor (la fecha, la versión del modelo), o la redacción de la pregunta varía levemente entre perfiles sin que lo advierta. | Registro parcial: transcribe respuestas pero no los prompts, o las respuestas están editadas o resumidas. | Solo cuenta lo que hizo, sin anexo verificable. | Sin anexo. *(Los trabajos sin anexo no se corrigen, se devuelven para rehacer.)* |
| **2. Detección de sesgo y homogeneidad** — ¿vio dónde falla, o se quedó en que "estuvo bastante bien"? | Identifica al menos dos problemas distintos **con evidencia citada del propio material**. Reconoce el patrón difícil: que los tres perfiles dicen lo mismo con distinto vocabulario, o que cada uno consume exactamente el medio que le corresponde. Nota ausencias, no solo presencias. | Identifica problemas reales y cita ejemplos, pero se queda en lo evidente (el vocabulario, el tono) sin llegar a la estructura de las respuestas. | Afirma que hay estereotipo u homogeneidad pero no cita nada concreto que lo sostenga. | Descripción de las respuestas sin análisis crítico. | Concluye que la muestra "funcionó bien" sin haber comparado contra nada. |
| **3. Propuesta de validación externa** — ¿sabe contra qué se contrasta un dato, y qué hace falta para que la comparación valga? | Nombra una fuente concreta, identifica el dato específico que buscaría, **y advierte que la pregunta tiene que estar redactada igual que el ítem original** para que la comparación sea válida. Si consiguió el dato y comparó, acá va el techo. | Fuente concreta y dato específico, pero no repara en el problema de la armonización del instrumento. | Menciona una fuente pertinente en general ("el SINCA", "una encuesta") sin decir qué dato buscaría. | Propone validar contra algo no verificable: su propia intuición, gente que conoce, "lo que se ve en redes". | No aborda la validación. |
| **4. Reflexión metodológica aplicada a su trabajo** — ¿puede decidir con criterio, o solo repetir la posición de la clase? | Toma una posición fundamentada y **la aplica a su tema concreto**, no en abstracto. Si dice que sí, especifica el rol exacto y qué declararía como limitación. Si dice que no, explica qué característica de su objeto lo impide. Puede sostener una posición distinta a la de la clase si la argumenta. | Posición fundamentada pero genérica: correcta y aplicable a cualquier tesis, no a la suya. | Repite las conclusiones de la clase sin elaborarlas ni conectarlas con su trabajo. | Posición sin fundamento, o contradictoria con lo que su propia muestra mostró. | No responde la pregunta. |

**Bonus +3** en el criterio 1: corriste el mismo perfil dos veces en chats distintos y
comparaste las dos corridas.

## Notas

- **El error más común es mezclar los tres perfiles en un solo chat.** Cada perfil va en una
  conversación nueva y en blanco; si no, el modelo se contamina con lo que ya escribió y las
  tres respuestas se parecen más de lo que se parecerían de otro modo. Arruina el ejercicio y
  no se puede corregir después.
- **Fuentes de validación disponibles:** Digital News Report (capítulo Argentina), Encuesta
  Nacional de Consumos Culturales del SINCA (tiene microdatos descargables), datos.gob.ar.
- No hace falta que tu muestra se parezca a la realidad, ni usar estadística, ni pagar
  ninguna suscripción.
