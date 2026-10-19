// datos.js — contenido del juego (personajes, relato animado y preguntas del caso)
// Fuentes: sentencia de la Cámara Civil, Sala B (24/05/2018, vLex), nota de La Nación (02/07/2025) y comentario de elDial.
'use strict';

// Personajes reales: sólo se los muestra con un dibujo genérico y se cuenta lo que dicen las fuentes
const PERSONAJES = [
  { id: 'beatriz', nombre: 'Beatriz Salomón', rol: 'Actriz. Tu clienta, que demanda por ella y por sus hijas menores.', g: 'ella', saco: '#E07A6F', corbata: '#FAF6EE', pelo: '#D9B26A', pareja: 1 },
  { id: 'alberto', nombre: 'Alberto Ferriols', rol: 'Cirujano, esposo de Beatriz en 2004.', g: 'el', saco: '#F4F7F8', corbata: '#5B8DB8', pelo: '#3B2A20', pareja: 1 },
  { id: 'jorge', nombre: 'Jorge Rial', rol: 'Conductor de "Intrusos en la Noche" (América TV).', g: 'el', saco: '#3E4C6B', corbata: '#E07A6F', pelo: '#2B2B2B' },
  { id: 'luis', nombre: 'Luis Ventura', rol: 'Conductor de "Intrusos en la Noche" (América TV).', g: 'el', saco: '#5A6B63', corbata: '#7FB08A', pelo: '#9AA3AD' },
];
const OTROS = 'También están demandados el canal América TV, la productora Eyeworks (antes Cuatro Cabezas), que hizo "Punto Doc", y sus conductores Daniel Tognetti y Miriam Lewin. En el juzgado hablan dos personajes ficticios: la jueza y el abogado de las demandadas.';
const JUEZA = { nombre: 'La jueza (personaje ficticio)', g: 'ella', saco: '#2F3A4A', corbata: '#FAF6EE', pelo: '#6B4A3A' };
const ABOGADO = { nombre: 'Abogado de las demandadas (personaje ficticio)', g: 'el', saco: '#6B5B7B', corbata: '#C9625A', pelo: '#4A4A4A' };

// Relato animado: sólo narración, sin voces ni frases inventadas de las personas reales
const BEATS = [
  { fecha: '6 OCT 2004', habla: ['jorge', 'luis'], t: 'América TV, 6 de octubre de 2004. El ciclo "Intrusos en la Noche", conducido por Jorge Rial y Luis Ventura, prepara su emisión en vivo.' },
  { fecha: '', habla: ['beatriz', 'jorge'], t: 'Invitan a Beatriz Salomón y a su esposo, el cirujano Alberto Ferriols. Según contó ella, creyó que iba a dar su descargo por una denuncia sobre el consultorio de él, y pidió un espacio para su derecho a réplica.' },
  { fecha: '', habla: [], t: 'Entonces se emite el informe de "Punto Doc", otro programa del mismo canal: una cámara oculta con escenas íntimas del cirujano. Según la sentencia, no hay prueba de que le anticiparan el contenido ni le pidieran su consentimiento.' },
  { fecha: '', habla: [], t: 'Beatriz ve esas imágenes en vivo, junto a su esposo y frente a las cámaras. Años después diría que la habían citado para ver cómo se enteraba en directo.' },
  { fecha: '7 OCT 2004', habla: ['jorge', 'luis'], t: 'Al día siguiente, "Intrusos" vuelve a emitir las imágenes, con comentarios sarcásticos, aunque ella había dicho que el tema era privado (según la sentencia de primera instancia).' },
  { fecha: '', habla: [], t: 'Beatriz se separó y contó que dejó de recibir ofertas de trabajo. Demandó por daños para ella y para sus hijas menores. Ahora te toca defenderla en el juzgado.' },
];

// 8 preguntas. p: 2 = muy buena, 1 = parcial, 0 = débil. Máximo 16 puntos.
const PREGUNTAS = [
  { quien: 'jueza', tema: 'Derechos vulnerados', texto: 'Doctor/a, tiene la palabra. ¿Qué derechos de su clienta y de sus hijas considera vulnerados por las emisiones del 6 y 7 de octubre de 2004?', ops: [
    { t: 'Su intimidad personal y familiar, su imagen y su honor: los de Beatriz y los de sus hijas menores.', p: 2, e: 'Es lo que se invocó en la demanda: intimidad, imagen y honor, con daños patrimoniales y extrapatrimoniales, por ella y por sus hijas.' },
    { t: 'Solo su honor, porque dijeron cosas falsas sobre ella.', p: 0, e: 'No se discutía que lo emitido fuera falso, sino la intromisión en la intimidad. Centrar todo en el honor debilita el reclamo.' },
    { t: 'Solo su imagen como artista, porque aparece en televisión.', p: 1, e: 'La imagen cuenta, pero el núcleo del caso es la intimidad personal y familiar; si te quedás solo con la imagen, dejás afuera lo principal.' } ] },
  { quien: 'jueza', tema: 'Contra quiénes demandar', texto: '¿Contra quiénes dirige la demanda?', ops: [
    { t: 'Contra el canal, la productora y los conductores de ambos programas, porque todos intervinieron en lo que se emitió.', p: 2, e: 'La demanda alcanzó a América TV, a Eyeworks y a los conductores de "Punto Doc" y de "Intrusos". La primera sentencia los condenó de forma concurrente.' },
    { t: 'Solo contra la productora que hizo la cámara oculta.', p: 1, e: 'Es defendible, pero deja afuera al canal y a quienes repitieron las imágenes y comentaron el material.' },
    { t: 'Solo contra uno de los conductores, el más conocido.', p: 0, e: 'Elegir por fama y no por responsabilidad es mala estrategia: la responsabilidad depende del rol de cada uno.' } ] },
  { quien: 'abogado', tema: 'Consentimiento', texto: 'Señoría, la actora fue al estudio por su propia voluntad. Si estuvo ahí, consintió. ¿No es así, doctor/a?', ops: [
    { t: 'Fue por otra razón: creyó que iba a dar su descargo por una denuncia sobre el consultorio. No sabía qué se iba a mostrar ni lo consintió, y el canal no probó lo contrario.', p: 2, e: 'La sentencia de primera instancia destacó que no había prueba de que le anticiparan el contenido ni le pidieran consentimiento. La Corte, en 2025, habló de la falta de un consentimiento claro.' },
    { t: 'Ir a un programa de chimentos implica aceptar que se hable de su vida.', p: 0, e: 'Es justo el argumento de la otra parte. Estar presente no equivale a consentir que se muestren escenas íntimas.' },
    { t: 'Ella nunca estuvo en ese programa.', p: 0, e: 'Es falso, y afirmar algo falso destruye tu credibilidad ante el tribunal.' } ] },
  { quien: 'abogado', tema: 'Figura pública e interés general', texto: 'La actora es una figura pública y el tema era de interés general. La prensa tiene derecho a informar sobre ella.', ops: [
    { t: 'Ser famosa permite informar sobre su actividad si hay interés general, pero no autoriza a invadir su vida íntima. Las escenas de su esposo eran ajenas a su actividad y no tenían interés general.', p: 2, e: 'Es el equilibrio que marcó la Corte en 2025: las figuras públicas pueden ser noticia en lo que se vincula con su actividad, pero conservan un ámbito de vida privada.' },
    { t: 'Estoy de acuerdo en que los famosos no tienen vida privada, pero igual pido indemnización.', p: 0, e: 'Concederlo hunde el caso: la intimidad también protege a las personas conocidas.' },
    { t: 'Si era de interés general, solo discutimos el monto.', p: 0, e: 'Regalás el punto central. Lo que hay que discutir es si ese interés general existía.' } ] },
  { quien: 'abogado', tema: 'Real malicia', texto: 'Invoco la doctrina de la real malicia: sin intención de dañar ni conocimiento de que algo es falso, no hay responsabilidad.', ops: [
    { t: 'No aplica: no discutimos que la información sea falsa, sino la intromisión en la intimidad mediante una cámara oculta y la repetición de las imágenes.', p: 2, e: 'El juez de primera instancia consideró inaplicable la real malicia. Ese estándar gira en torno a la falsedad, y acá el reclamo es por intimidad.' },
    { t: 'Entonces hay que probar que los periodistas sabían que lo emitido era falso.', p: 0, e: 'Aceptás el terreno del medio. La falsedad no es el eje de este caso.' },
    { t: 'Pido que se declare inválida la libertad de prensa.', p: 0, e: 'Es un planteo desmedido: la libertad de expresión es un derecho central y lo que corresponde es armonizarla con la intimidad.' } ] },
  { quien: 'abogado', tema: 'Responsabilidad conjunta', texto: 'Eran dos programas de empresas distintas. El canal no responde por lo que hizo la productora de "Punto Doc".', ops: [
    { t: 'Los programas actuaron coordinados: invitaron a Beatriz a verlo en vivo, el canal los emitió y "Intrusos" repitió las imágenes al día siguiente. Todos contribuyeron al daño.', p: 2, e: 'Esa fue la línea de la actora. La primera sentencia condenó a todos de modo concurrente, y la Corte consideró que quienes conducían "Intrusos" también se entrometieron en su intimidad.' },
    { t: 'Acepto y reclamo solo a la productora.', p: 1, e: 'Reducís el riesgo, pero abandonás la responsabilidad del canal y de quienes repitieron las imágenes.' },
    { t: 'Insisto en que fue un solo programa.', p: 0, e: 'No coincide con los hechos: eran dos ciclos distintos. Lo fuerte es probar la coordinación.' } ] },
  { quien: 'jueza', tema: 'Daños y prueba', texto: 'Hablemos de los daños. ¿Qué reclama y cómo piensa probarlo?', ops: [
    { t: 'Daño moral, por ella y por sus hijas, y daño patrimonial, como la pérdida de oportunidades de trabajo, con prueba de las ofertas y contratos que dejaron de llegar.', p: 2, e: 'La demanda pidió daños patrimoniales y extrapatrimoniales por un total de $ 4.717.200 más intereses. Sin prueba concreta de lo laboral, ese rubro puede rechazarse.' },
    { t: 'Solo una suma alta de dinero; el juez verá cómo la calcula.', p: 0, e: 'Los daños se detallan y se prueban. Pedir un monto sin respaldo debilita el reclamo.' },
    { t: 'Solo el daño moral, porque lo laboral es imposible de probar.', p: 1, e: 'Es más fácil, pero renunciás a un rubro que sí se reclamó.' } ] },
  { quien: 'jueza', tema: 'Alegato final', texto: 'Última oportunidad, doctor/a. Resuma su posición.', ops: [
    { t: 'La libertad de expresión no es absoluta y debe armonizarse con la intimidad: hubo engaño, falta de consentimiento, repetición y ningún interés general en esas escenas.', p: 2, e: 'Es el equilibrio que planteó la Corte Suprema en 2025 entre libertad de prensa e intimidad.' },
    { t: 'Los periodistas no tienen ética y deberían ser sancionados.', p: 0, e: 'Atacar a las personas en vez de argumentar jurídicamente le resta fuerza al alegato.' },
    { t: 'Que el tribunal prohíba para siempre las cámaras ocultas en televisión.', p: 0, e: 'Excede lo que se discute: se juzga este caso, no se dicta una norma general.' } ] },
];

const VEREDICTOS = [
  { min: 13, t: 'Sentencia favorable', c: 'verde', x: 'El tribunal hace lugar a la demanda: considera que las emisiones invadieron la intimidad de Beatriz y de sus hijas, sin consentimiento y sin interés general, y condena a los responsables a indemnizar los daños.' },
  { min: 8, t: 'Sentencia parcial', c: 'azul', x: 'El tribunal reconoce parte del daño, pero reduce la indemnización y limita la responsabilidad. Faltó firmeza en puntos clave. Algo parecido pasó en la Cámara en 2018, que redujo el monto y descartó responsables.' },
  { min: 0, t: 'Demanda rechazada', c: 'coral', x: 'El tribunal no encuentra probado que corresponda responsabilizar a los demandados. Repasá las explicaciones de cada pregunta y volvé a intentarlo.' },
];

const REALIDAD = [
  ['6 y 7 de octubre de 2004', 'Se emiten "Punto Doc" e "Intrusos en la Noche" por América TV.'],
  ['2017', 'Primera instancia: condena a los demandados, de forma concurrente, a pagar $ 14.593.551 más intereses.'],
  ['Mayo de 2018', 'La Cámara Civil (Sala B) revierte la condena para el canal y los periodistas por falta de prueba y reduce el monto de la productora.'],
  ['2019', 'Beatriz apela ante la Corte Suprema y muere ese año; sus herederas continúan el caso.'],
  ['Julio de 2025', 'La Corte Suprema falla a favor de las herederas: hubo intromisión en la intimidad, sin consentimiento claro y sin interés general.'],
];
