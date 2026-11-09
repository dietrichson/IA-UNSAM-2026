"""Adaptador de CV y carta: palabras clave, CV adaptado y carta a medida, usando solo lo que ya figura en el CV."""
import streamlit as st

import componentes
import estado
import estilo
from estilo import esc
from servicios.genero import GENEROS, inferir_genero
from servicios.adaptador import TONOS, adaptar_cv, analizar_palabras, redactar_carta
from servicios.cv_parser import ErrorArchivo
from servicios.exportar import a_docx
from servicios.llm_client import LLMError
from servicios.oferta_parser import parsear_oferta
from servicios.texto import hash_texto
from servicios.verificador import verificar

S = estado.servicios()
estilo.encabezado("Adaptador de CV y carta", "Pegá una oferta y adaptá tu CV y tu carta usando solo lo que ya figura en tu CV.",
                  "hoja", "rosa")

if not estado.aviso_aceptado():
    estilo.aviso("Primero leé el aviso de privacidad en Inicio.", "privado", "Antes de empezar")
    st.stop()

ok, mensaje = S.llm.estado()
if not ok:
    estilo.aviso(mensaje, "error", "El modelo no está disponible")

# ---------------------------------------------------------------- 1 y 2. entradas
st.markdown("## 1. Tu CV")
cv_texto = componentes.entrada_cv(S)

st.markdown("## 2. La oferta")
oferta_texto = st.text_area("Texto de la oferta", height=220, key="oferta_texto",
                            placeholder="Pegá el aviso completo: título, tareas, requisitos y herramientas.")
listo = bool(cv_texto and (oferta_texto or "").strip() and ok)
if st.button("Analizar oferta", type="primary", disabled=not listo):
    try:
        cv = componentes.obtener_cv(S, cv_texto)
        with st.spinner("Leyendo la oferta y comparando palabras clave…"):
            oferta = parsear_oferta(oferta_texto, S.llm, S.vocabulario)
            analisis = analizar_palabras(cv, oferta, S.llm)
        st.session_state["adaptacion"] = {"clave": hash_texto(cv_texto + "|" + oferta_texto.strip()), "cv": cv,
                                          "oferta": oferta, "analisis": analisis}
        for k in ("edit_cv", "edit_carta", "gen_cv", "gen_carta"):
            st.session_state.pop(k, None)
    except (LLMError, ErrorArchivo) as e:
        st.session_state.pop("adaptacion", None)
        estilo.aviso(str(e), "error", "No pude analizar la oferta")
if not listo:
    st.caption("Cargá tu CV y pegá la oferta para poder analizarla.")

ad = st.session_state.get("adaptacion")
if not ad:
    st.stop()
if ad["clave"] != hash_texto((cv_texto or "") + "|" + (oferta_texto or "").strip()):
    estilo.aviso("Cambiaste el CV o la oferta desde el último análisis. Tocá «Analizar oferta» otra vez.", "alerta")
    st.stop()

cv, oferta, analisis = ad["cv"], ad["oferta"], ad["analisis"]

# ---------------------------------------------------------------- 3. palabras clave
st.markdown("## 3. Palabras clave de la oferta")
est = oferta.estructura
if est.titulo or est.empresa:
    st.markdown(f"**Puesto:** {esc(est.titulo or 'sin dato')} · **Empresa:** {esc(est.empresa or 'sin dato')}", unsafe_allow_html=True)
for a in [*oferta.avisos, *cv.avisos, *analisis.avisos]:
    estilo.aviso(a, "alerta")
presentes = [p.palabra + (" ≈" if p.via != "exacta" else "") for p in analisis.presentes]
estilo.tarjeta(
    f"<p><b>Ya están en tu CV</b> ({len(presentes)})</p><p>{estilo.chips(presentes, 'menta') or 'Ninguna.'}</p>"
    f"<p><b>No figuran en tu CV</b> ({len(analisis.faltantes)})</p><p>{estilo.chips(analisis.faltantes, 'rosa') or 'Ninguna.'}</p>"
    "<p><small>≈ = aparece con otras palabras (sinónimo) o el modelo lo confirmó con una frase de tu CV.</small></p>",
    "blanco", "Coincidencia con tu CV", "lupa")
if analisis.no_cubiertos:
    items = "".join(f"<li>{esc(x)}</li>" for x in analisis.no_cubiertos)
    estilo.tarjeta(f"<p>Tu CV no permite cubrir esto, así que <b>no se va a completar con datos inventados</b>:</p><ul>{items}</ul>",
                   "durazno", "Puntos que no podés cubrir (todavía)", "alerta")

# ---------------------------------------------------------------- 4. generar
st.markdown("## 4. Generar")
tono = st.selectbox("Tono de la carta", list(TONOS), index=1, key="tono",
                    format_func=lambda t: {"formal": "Formal", "cercano": "Cercano", "creativo": "Creativo"}[t])
_detectado = inferir_genero(cv.texto)
genero = st.selectbox("Cómo querés que se escriba (género gramatical)", list(GENEROS), index=0, key="genero",
                      format_func=lambda g: GENEROS[g] + (f" (detecté: {GENEROS[_detectado].lower()})"
                                                          if g == "auto" and _detectado else
                                                          " (no pude detectarlo: se usa redacción neutra)" if g == "auto" else ""))
st.caption("Cada texto puede tardar un par de minutos sin placa de video; si el verificador encuentra datos que no "
           "están en tu CV, se genera una segunda versión.")
c1, c2 = st.columns(2)
hacer_cv = c1.button("Adaptar mi CV", disabled=not ok)
hacer_carta = c2.button("Escribir la carta", disabled=not ok)


def generar(clave: str, funcion):
    try:
        with st.spinner("Escribiendo y verificando…"):
            g = funcion()
        st.session_state[f"gen_{clave}"] = g
        st.session_state[f"edit_{clave}"] = g.texto
        st.session_state[f"hallazgos_{clave}"] = g.hallazgos
    except (LLMError, ErrorArchivo) as e:
        estilo.aviso(str(e), "error", "No pude generar el texto")


if hacer_cv:
    generar("cv", lambda: adaptar_cv(cv, oferta, analisis, S.llm, S.cfg, S.vocabulario, genero))
if hacer_carta:
    generar("carta", lambda: redactar_carta(cv, oferta, analisis, S.llm, S.cfg, tono, S.vocabulario, genero))


def mostrar(clave: str, titulo: str, archivo: str) -> None:
    g = st.session_state.get(f"gen_{clave}")
    if g is None:
        return
    st.markdown(f"## {titulo}")
    for a in getattr(g, "avisos", []):
        estilo.aviso(a, "alerta")
    st.session_state.setdefault(f"edit_{clave}", g.texto)  # si la pantalla se limpió al cambiar de página
    hallazgos = st.session_state.get(f"hallazgos_{clave}", [])
    if hallazgos:
        lista = "".join(f"<li><b>{esc(h.fragmento)}</b> ({esc(h.tipo)}): {esc(h.motivo)}</li>" for h in hallazgos)
        estilo.tarjeta(f"<p>Revisá estos datos antes de usar el texto: no los encontré en tu CV.</p><ul>{lista}</ul>"
                       "<p>Corregilos o borralos en el cuadro de abajo.</p>", "durazno", "Revisá esto", "alerta")
        estilo.tarjeta(f"<p>{estilo.resaltar(st.session_state[f'edit_{clave}'], [h.fragmento for h in hallazgos])}</p>",
                       "blanco", "Vista con marcas")
    else:
        extra = " (la primera versión tenía datos sin respaldo y se corrigió)" if g.regenerado else ""
        estilo.aviso(f"No encontré datos que no estén en tu CV{extra}. Igual leelo completo antes de enviarlo.", "ok", "Verificado")
    texto = st.text_area("Podés editarlo acá", height=420, key=f"edit_{clave}")
    if st.button("Revisar mi edición", key=f"rev_{clave}"):
        st.session_state[f"hallazgos_{clave}"] = verificar(texto, cv.texto, oferta.texto, S.vocabulario)
        st.rerun()
    d1, d2 = st.columns(2)
    d1.download_button("Descargar .txt", texto.encode("utf-8"), f"{archivo}.txt", "text/plain", key=f"txt_{clave}")
    d2.download_button("Descargar .docx", a_docx(texto), f"{archivo}.docx",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"docx_{clave}")


mostrar("cv", "Tu CV adaptado", "cv-adaptado")
mostrar("carta", "Tu carta de presentación", "carta-de-presentacion")
