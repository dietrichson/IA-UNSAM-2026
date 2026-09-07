# Laboratorio 1 — System Prompt

## 1. Objetivo

El objetivo de esta experiencia es observar cómo un system prompt puede modificar el comportamiento de un modelo de lenguaje y analizar qué aspectos de su respuesta pueden cambiar y cuáles no pueden garantizarse.

Para la experiencia se utilizó el modelo `qwen2.5:3b` y se realizó la misma pregunta en dos situaciones: primero sin un system prompt específico y luego utilizando el system prompt desarrollado para Atenea.

---

## 2. Pregunta utilizada

La misma pregunta utilizada en las dos pruebas fue:

> ¿Qué es la fotosíntesis?

La pregunta se mantuvo exactamente igual para poder comparar el comportamiento del modelo con y sin las instrucciones de Atenea.

---

## 3. Ejemplo sin system prompt

### Pregunta

> ¿Qué es la fotosíntesis?

### Respuesta obtenida

> La fotosíntesis es un proceso biológico crucial que las plantas, hongos y algunas bacterias utilizan para sintetizar ácido fólico (o clorofiliano), un ácido orgánico que las células utilizan para generar energía. Es conocido principalmente por su papel en la producción de oxígeno y la formación de azúcares (principalmente glucosa) en ambientes con luz solar.
>
> Aquí hay algunos detalles más específicos sobre la fotosíntesis:
>
> 1. **Proceso de la Fotosíntesis**: Se divide en dos etapas principales: la captura de luz (oísmosis de luz) y la producción de energía (caloresis).
>
> 2. **Componentes Importantes**: El clorofilo, que es el pigmento verde que permite a las plantas capturar luz solar, jugando un papel crucial en la fotosíntesis.
>
> 3. **Interacción con el Sol**: Las plantas y otros organismos fotosintéticos capturan la luz solar con su clorofilo y la utilizan para convertir la luz solar en energía química almacenada en las moléculas de azúcar.
>
> 4. **Importancia para la Tierra**: La fotosíntesis es un proceso fundamental para la vida en la Tierra porque proporciona la mayoría de la energía que utilizan los organismos. También producirá oxígeno para el aire.
>
> 5. **Impacto Ambiental**: Aunque la fotosíntesis es generalmente positiva, puede verse afectada por factores ambientales como la contaminación y la pérdida de bosques.

---

## 4. Ejemplo con el system prompt de Atenea

### Pregunta

> ¿Qué es la fotosíntesis?

### Respuesta obtenida

> La fotosíntesis es un proceso biológico fundamental que las plantas, algunos hongos y ciertas bacterias utilizan para transformar la energía del sol en energía química que pueden utilizar. Este proceso es esencial para la vida en la Tierra porque permite la producción de alimento y la generación de oxígeno.
>
> ### Explicación Detallada de la Fotosíntesis
>
> #### Componentes Principales de la Fotosíntesis
>
> La fotosíntesis se divide en dos fases principales: la captura de luz y la producción de energía.
>
> 1. **Carga de Luz (Oísmosis de Luz)**:
>    - La luz solar se captura por los pigmentos, especialmente la clorofila.
>    - La luz solar se utiliza para sintetizar una molécula de ácido fólico (glucosa fosfátil) a partir del agua y dióxido de carbono.
>
> 2. **Producción de Energía (Caloresis)**:
>    - La molécula sintetizada se utiliza para descomponer el ácido fólico (glucosa fosfátil) en ácido fólico (glucosa), que a su vez se descompone en ácido fólico (glucosa) y oxígeno.
>
> ### Importancia de la Fotosíntesis
>
> 1. **Producción de Energía**:
>    - Las plantas transforman la luz solar en energía química almacenada en moléculas de glucosa.
>
> 2. **Producción de Oxígeno**:
>    - Las plantas producen oxígeno a través de la fotosíntesis.
>
> 3. **Ciclo del Carbono**:
>    - La fotosíntesis involucra la absorción de dióxido de carbono por las plantas.

---

## 5. Comparación de los resultados

Las dos respuestas muestran que el modelo puede proporcionar información relacionada con la pregunta, pero también presentan errores conceptuales.

La respuesta con system prompt presenta una estructura más organizada, utiliza títulos y desarrolla la explicación de manera más didáctica. Esto coincide con las instrucciones establecidas para Atenea, que indican que debe responder de manera clara, organizada y orientada a la comprensión.

Sin embargo, el system prompt no consiguió evitar los errores de contenido. En ambas respuestas aparecen afirmaciones incorrectas, como la asociación de la fotosíntesis con la producción de ácido fólico y la utilización de términos como "oísmosis de luz" y "caloresis".

Esto resulta especialmente importante porque el system prompt de Atenea incluye reglas como "No inventar información" y "No presentar una hipótesis como un hecho". A pesar de estas instrucciones, el modelo continuó generando información incorrecta.

Por lo tanto, la experiencia permite observar que un system prompt puede influir en **la forma, el tono, la organización y las prioridades de una respuesta**, pero no garantiza por sí mismo que el modelo produzca información verdadera.

---

## 6. ¿Qué se puede cambiar mediante un system prompt?

Un system prompt puede orientar diferentes aspectos del comportamiento de un modelo, entre ellos:

- la identidad y el rol que adopta;
- la personalidad;
- el tono de comunicación;
- el idioma;
- la estructura de las respuestas;
- el nivel de explicación;
- la utilización de ejemplos;
- determinadas reglas de comportamiento;
- la forma de expresar incertidumbre;
- las prioridades que debe seguir al responder.

En el caso de Atenea, el system prompt establece que debe comportarse como una asistente académica y tecnológica, con una comunicación clara, analítica, didáctica y profesional.

Los resultados obtenidos permiten observar que estas instrucciones pueden modificar principalmente la manera en que el modelo organiza y presenta su respuesta.

---

## 7. ¿Qué no puede garantizar un system prompt?

Un system prompt no garantiza que el modelo siempre produzca respuestas correctas.

El experimento demuestra esto de manera concreta. Aunque el system prompt de Atenea indica que no debe inventar información y que debe reconocer la incertidumbre, la respuesta obtenida continuó incluyendo información incorrecta.

Por ejemplo, el modelo afirmó que la fotosíntesis produce o utiliza "ácido fólico" y utilizó términos que no corresponden a las etapas reales de la fotosíntesis.

Esto demuestra que las instrucciones pueden orientar el comportamiento del modelo, pero no eliminan sus limitaciones.

La calidad y exactitud de las respuestas también dependen del modelo utilizado, de los datos con los que fue entrenado, de la pregunta realizada y de la información disponible en el contexto.

Por esta razón, un system prompt debe entenderse como una herramienta de orientación y personalización, no como una garantía de exactitud.

---

## 8. Reflexión final

La experiencia permitió comprobar de manera práctica que un system prompt funciona como una capa de instrucciones que orienta el comportamiento de un modelo de lenguaje.

En la comparación realizada, la respuesta con el system prompt de Atenea presentó una organización más cercana al comportamiento definido para la asistente. Utilizó títulos, explicaciones y una estructura más didáctica.

Sin embargo, también se comprobó que las instrucciones no son suficientes para garantizar la exactitud de la información. El modelo continuó generando errores científicos incluso después de recibir instrucciones explícitas para no inventar información.

Por lo tanto, el principal aprendizaje de la experiencia es que un system prompt puede **personalizar y orientar el comportamiento del modelo**, pero no convierte automáticamente al modelo en una fuente infalible de conocimiento.

En el caso de Atenea, las instrucciones permiten establecer una identidad, una personalidad, objetivos y reglas de comunicación. Para mejorar la confiabilidad de sus respuestas resulta necesario complementar estas instrucciones con mecanismos adicionales, como información de contexto, fuentes confiables o sistemas de recuperación de información.

La experiencia también permite comprender la diferencia entre **cómo responde un modelo** y **qué tan correcta es la información que proporciona**. El system prompt puede influir fuertemente en el primer aspecto, pero no garantiza por sí solo el segundo.
