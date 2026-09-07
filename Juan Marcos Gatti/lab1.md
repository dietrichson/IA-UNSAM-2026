# Laboratorio 1 — System Prompt

## 1. Objetivo

El objetivo de esta experiencia es observar cómo un system prompt puede modificar el comportamiento, el tono, la forma de responder y las prioridades de un modelo de lenguaje.

Para la experiencia se utiliza el modelo `qwen2.5:3b` y se compara su comportamiento ante la misma pregunta con y sin las instrucciones definidas para Atenea.

---

## 2. Pregunta utilizada

La misma pregunta utilizada en las dos pruebas fue:

> ¿Qué es la fotosíntesis?

La pregunta se mantiene exactamente igual para poder observar qué cambia cuando se incorpora el system prompt.

---

## 3. Ejemplo sin system prompt

### Pregunta

> ¿Qué es la fotosíntesis?

### Respuesta del modelo

La fotosíntesis es el proceso mediante el cual las plantas, las algas y algunas bacterias utilizan la energía de la luz solar para transformar dióxido de carbono y agua en glucosa y oxígeno.

Este proceso ocurre principalmente en los cloroplastos de las células vegetales y utiliza un pigmento llamado clorofila, que permite captar la energía de la luz.

De manera simplificada:

Dióxido de carbono + agua + luz → glucosa + oxígeno.

La fotosíntesis es fundamental porque produce materia orgánica que sirve como fuente de energía para los seres vivos y libera oxígeno a la atmósfera.

---

## 4. Ejemplo con el system prompt de Atenea

### Pregunta

> ¿Qué es la fotosíntesis?

### Respuesta de Atenea

La fotosíntesis es el proceso mediante el cual las plantas, las algas y algunas bacterias utilizan la energía de la luz para producir materia orgánica a partir de sustancias inorgánicas.

Principalmente, utilizan:

- dióxido de carbono (CO₂);
- agua (H₂O);
- energía de la luz solar.

Como resultado, producen glucosa y liberan oxígeno (O₂).

De forma simplificada:

**CO₂ + H₂O + luz → glucosa + O₂**

### ¿Por qué es importante?

La fotosíntesis es fundamental para los ecosistemas porque permite producir materia orgánica que sirve de base para muchas cadenas alimentarias y contribuye a la presencia de oxígeno en la atmósfera.

En términos sencillos, puede entenderse como el mecanismo mediante el cual las plantas transforman la energía de la luz en energía química almacenada en moléculas orgánicas.

---

## 5. Comparación

La información principal de las dos respuestas es muy similar porque la pregunta es sencilla y el modelo ya posee conocimientos generales sobre el tema.

Sin embargo, el system prompt establece características específicas para el comportamiento de Atenea.

Sin system prompt, el modelo responde principalmente de acuerdo con sus características generales.

Con el system prompt, la respuesta queda orientada por instrucciones que establecen que Atenea debe ser clara, didáctica, organizada, profesional y honesta respecto de sus limitaciones.

También se establece que debe adaptar la profundidad de la explicación a la pregunta y utilizar ejemplos, listas o estructuras cuando ayuden a comprender mejor el contenido.

Por lo tanto, el system prompt no necesariamente cambia el conocimiento básico que posee el modelo, pero sí puede modificar **cómo organiza, presenta y comunica ese conocimiento**.

---

## 6. ¿Qué se puede cambiar mediante un system prompt?

Un system prompt puede modificar u orientar diferentes aspectos del comportamiento del modelo, por ejemplo:

- su identidad y rol;
- su personalidad;
- el tono de comunicación;
- el idioma utilizado;
- la estructura de las respuestas;
- el nivel de explicación;
- la forma de presentar ejemplos;
- determinadas reglas de comportamiento;
- la manera de expresar incertidumbre;
- las prioridades que debe seguir al responder.

En el caso de Atenea, el system prompt establece una identidad de asistente académica y tecnológica, con una comunicación clara, analítica, didáctica y profesional.

---

## 7. ¿Qué no puede garantizar un system prompt?

Un system prompt no garantiza que el modelo siempre produzca respuestas correctas.

Las instrucciones pueden orientar el comportamiento del modelo, pero no eliminan sus limitaciones ni garantizan que conozca toda la información existente.

Por ejemplo, indicarle al modelo:

> "No inventes información"

es una instrucción útil para orientar su comportamiento, pero no significa que el modelo sea incapaz de cometer errores.

La calidad de la respuesta también depende del modelo utilizado, de la información disponible y de la pregunta realizada.

Por eso, Atenea incluye dentro de sus reglas la obligación de reconocer la incertidumbre cuando no existe información suficiente.

---

## 8. Reflexión final

La experiencia permite observar que un system prompt funciona como una capa de instrucciones que orienta el comportamiento de un modelo de lenguaje.

La diferencia no consiste necesariamente en que el modelo "aprenda" nuevos conocimientos, sino en que las instrucciones pueden establecer una identidad, objetivos, reglas y una determinada forma de comunicarse.

En el caso de Atenea, el system prompt busca que el modelo no se limite a entregar respuestas, sino que actúe como una tutora académica digital que ayude al usuario a comprender los temas.

Por lo tanto, el system prompt permite personalizar el comportamiento del modelo, aunque no elimina sus limitaciones ni garantiza por sí mismo la exactitud de todas sus respuestas.
