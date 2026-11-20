# Consigna en pasos

Abril Odicino · Trabajo final del seminario de IA, UNSAM

## Qué es

Una página que ayuda a transformar una consigna de clase en una lista marcable. Prepara un prompt para pedirle a ChatGPT que extraiga las tareas. Al pegar la respuesta de vuelta, la página muestra las tareas obligatorias, las opcionales y las fechas por separado, con la consigna original a la vista.

## Cómo abrirlo

1. Descargá [`src/index.html`](src/index.html) y abrilo con doble clic en el navegador.
2. Tocá **Cargar ejemplo** para probar el recorrido sin conexión. Marcá una tarea y mirá cómo cambia el contador.
3. Para usar una consigna propia, pegala en **Consigna original** y tocá **Generar prompt**. Copiá el prompt y pegalo en un chat nuevo de ChatGPT.
4. Pegá el texto que te devuelve el modelo en **Respuesta de ChatGPT** y tocá **Convertir en lista**. Revisá las tareas y fechas junto con el original antes de usarlas.

## Qué funciona y qué queda afuera

La página puede preparar el prompt, importar respuestas con los prefijos establecidos, señalar líneas fuera de formato y actualizar el contador. Se probó como archivo local en Chrome y con tres respuestas reales de ChatGPT.

La generación de nuevas listas requiere acceso a ChatGPT por separado. La página admite una consigna de texto por vez, y las marcas se pierden al recargar o cerrar. La validez del formato de la respuesta y la fidelidad a la consigna se revisan por separado. Una tarea puede tener el prefijo correcto y aun así incluir un detalle equivocado.

## Aprendizajes

Pedir una tarea por línea con tres prefijos explícitos facilitó que la página pudiera leer la respuesta. La prueba con una consigna sin fecha permitió comprobar que el campo podía quedar vacío. También apareció un cambio menor de puntuación en una fecha, que muestra por qué conviene tener el texto original a mano y distinguir entre una variación de forma y un cambio de significado.

## Documentación

- [Propuesta](docs/propuesta.md)
- [Requisitos](docs/requisitos.md)
- [Diseño](docs/diseno.md)
- [Pruebas y respuestas del modelo](docs/pruebas.md)

## Demostración en clase

Abrir la página, cargar el ejemplo y marcar una tarea. Después, mostrar una consigna propia y su prompt. Si hay acceso a ChatGPT, pegar la respuesta en la página y comparar qué tareas y fechas detectó con el texto original. La consigna sin fecha de las pruebas sirve como ejemplo breve para esa segunda parte.
