"""Piezas de pantalla compartidas por el Sugeridor y el Adaptador: entrada del CV y tarjetas de resultado."""
from __future__ import annotations

import streamlit as st

import estado
import estilo
from estilo import esc
from servicios.brechas import Brecha, brechas_de_puesto, sugerencia
from servicios.config import EJEMPLOS_DIR
from servicios.cv_parser import CVProcesado, ErrorArchivo, leer_archivo, parsear_cv
from servicios.matcher import ResultadoPuesto
from servicios.puestos_repo import NO_FIGURA
from servicios.texto import hash_texto

ORIGENES = ("Pegar texto", "Subir archivo", "Usar un ejemplo")


def _dato(v: str) -> bool:
    return bool(v) and not v.lower().startswith(NO_FIGURA)


# ---------------------------------------------------------------- entrada del CV
def entrada_cv(S) -> str | None:
    """Pide el CV (texto, archivo o ejemplo) y lo deja en `st.session_state['cv_texto']`. Devuelve el texto o None."""
    guardado = estado.leer_cv_guardado()
    if guardado and not st.session_state.get("cv_texto") and not st.session_state.get("cv_guardado_ignorado"):
        estilo.aviso("Tenés un CV guardado en esta computadora.", "info", "CV recordado")
        c1, c2 = st.columns(2)
        if c1.button("Usar mi CV guardado"):
            st.session_state["cv_texto"] = guardado
            st.session_state["cv_input_texto"] = guardado
            st.rerun()
        if c2.button("Empezar con otro"):
            st.session_state["cv_guardado_ignorado"] = True
            st.rerun()

    origen = st.radio("¿Cómo querés cargar tu CV?", ORIGENES, horizontal=True, key="cv_origen")
    texto: str | None = None
    if origen == ORIGENES[0]:
        texto = st.text_area("Texto de tu CV", height=260, key="cv_input_texto",
                             placeholder="Pegá acá el contenido de tu CV (experiencia, formación, herramientas, idiomas).")
    elif origen == ORIGENES[1]:
        archivo = st.file_uploader("Archivo (.pdf, .docx, .txt o .md)", type=["pdf", "docx", "txt", "md"], key="cv_archivo")
        if archivo is not None:
            try:
                texto = leer_archivo(archivo.name, archivo.getvalue())
            except ErrorArchivo as e:
                estilo.aviso(str(e), "error", "No pude leer el archivo")
    else:
        ejemplos = sorted(EJEMPLOS_DIR.glob("*.md"))
        nombres = {p.stem.replace("cv-ejemplo-", "CV ficticio: ").replace("-", " "): p for p in ejemplos}
        if nombres:
            elegido = st.selectbox("Ejemplo", list(nombres), key="cv_ejemplo")
            texto = nombres[elegido].read_text(encoding="utf-8")
            with st.expander("Ver el CV de ejemplo"):
                st.text(texto)
        else:
            estilo.aviso("No hay ejemplos en data/ejemplos/.", "alerta")

    texto = (texto or "").strip() or None
    st.session_state["cv_texto"] = texto
    if texto and len(texto) > S.cfg.max_cv_chars:
        st.caption(f"Tu CV tiene {len(texto)} caracteres; se usarán los primeros {S.cfg.max_cv_chars}.")

    recordar = st.checkbox("Recordar mi CV en esta computadora (carpeta data/local, no se envía a ningún lado)",
                           key="cv_recordar", value=guardado is not None)
    if recordar and texto:
        estado.guardar_cv(texto)
    elif st.session_state.get("_recordar_prev") is True and not recordar:
        estado.borrar_cv_guardado()  # la persona destildó la opción
    st.session_state["_recordar_prev"] = recordar
    return texto


def obtener_cv(S, texto: str) -> CVProcesado:
    """Analiza el CV una sola vez por texto (la lectura con el modelo es lenta); se guarda en la sesión."""
    clave = hash_texto(texto)
    guardado = st.session_state.get("cv_procesado")
    if guardado and guardado[0] == clave:
        return guardado[1]
    with st.spinner("Leyendo tu CV…"):
        cv = parsear_cv(texto, S.llm, S.cfg, S.vocabulario)
    st.session_state["cv_procesado"] = (clave, cv)
    return cv


# ---------------------------------------------------------------- resultados
def _color_por_puntaje(p: int) -> str:
    return "menta" if p >= 70 else "limon" if p >= 40 else "durazno"


def _detalle_html(res: ResultadoPuesto, brechas: list[Brecha], consejo: str) -> str:
    partes = []
    if res.resumen:
        partes.append(f"<p>{esc(res.resumen)}</p>")
    for i in res.items:
        linea = f"<p><b>{esc(i.etiqueta)}</b> {estilo.barra_puntaje(i.puntaje)}"
        if i.peso:
            linea += f' <small>(pesa {round(i.peso * 100)} %)</small>'
        if i.comentario:
            linea += f"<br>{esc(i.comentario)}"
        for q in i.evidencia:
            linea += f"<br><i>«{esc(q)}»</i>"
        partes.append(linea + "</p>")
    if res.herramientas_cubiertas or res.herramientas_faltantes:
        partes.append("<p><b>Herramientas del puesto</b><br>" + estilo.chips(res.herramientas_cubiertas, "menta")
                      + estilo.chips(res.herramientas_faltantes, "rosa") + "</p>"
                      "<p><small>Verde: figura en tu CV. Rosa: no figura.</small></p>")
    else:
        partes.append("<p><small>Este puesto no detalla herramientas, así que no se puntuó ese criterio.</small></p>")
    if res.plus:
        partes.append(f"<p><b>Plus (deseables que cubrís)</b> <small>+{res.bonus} puntos</small><br>"
                      + estilo.chips(res.plus, "menta") + "</p>")
    opcionales = [b for b in brechas if b.tipo == "deseable"]
    brechas = [b for b in brechas if b.tipo != "deseable"]
    if brechas:
        lista = "".join(
            f"<li>{esc(b.texto)}" + (f" <small>(se pide en {b.frecuencia} puestos de la base)</small>"
                                      if b.tipo == "herramienta" and b.frecuencia > 1 else "") + "</li>" for b in brechas)
        partes.append(f"<p><b>Brechas (requisitos excluyentes)</b></p><ul>{lista}</ul>")
    if opcionales:
        partes.append("<p><b>Deseables que no figuran</b> <small>(no restan puntaje)</small></p><ul>"
                      + "".join(f"<li>{esc(b.texto)}</li>" for b in opcionales) + "</ul>")
    partes.append(f"<p><b>{esc(consejo)}</b></p>")
    for a in res.avisos:
        partes.append(f"<p>⚠ {esc(a)}</p>")
    p = res.puesto
    fuente = "; ".join(p.fuente) if p.fuente else "sin dato"
    partes.append(f"<p><small>Fuente: {esc(fuente)} · Relevado: {esc(p.relevado)}</small></p>")
    return "".join(partes)


def mostrar_resultado(res: ResultadoPuesto, posicion: int | None, puestos_base) -> None:
    p = res.puesto
    chips = []
    if _dato(p.modalidad_tipo):
        chips.append(estilo.chip(p.modalidad_tipo, "celeste"))
    if p.requiere_titulo in ("sí", "deseable"):
        chips.append(estilo.chip(f"Título: {p.requiere_titulo}", "lila"))
    if p.lectura != "aviso completo":
        chips.append(estilo.chip("Datos parciales (resumen de listado)", "limon"))
    if res.parcial:
        chips.append(estilo.chip("Puntaje parcial", "durazno"))
    if res.desde_cache:
        chips.append(estilo.chip("Calculado antes", "blanco"))
    empresa = f"<p>{esc(p.empresa)}</p>" if _dato(p.empresa) else ""
    prefijo = f"#{posicion} " if posicion else ""
    estilo.tarjeta(f"{empresa}<p>{estilo.barra_puntaje(res.puntaje)}</p><p>{''.join(chips)}</p>",
                   _color_por_puntaje(res.puntaje) if not res.parcial else "blanco", f"{prefijo}{p.titulo}")
    brechas = brechas_de_puesto(res, puestos_base)
    with st.expander("Ver detalle y brechas"):
        st.markdown(_detalle_html(res, brechas, sugerencia(brechas, len(puestos_base))), unsafe_allow_html=True)
