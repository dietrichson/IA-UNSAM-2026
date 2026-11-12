"""Sugeridor de puestos: CV -> puestos de la base ordenados por ajuste, con motivos y brechas."""
import streamlit as st

import componentes
import estado
import estilo
from estilo import esc
from servicios.llm_client import LLMError
from servicios.cv_parser import ErrorArchivo
from servicios.matcher import CachePuntajes
from servicios.oferta_parser import parsear_oferta
from servicios.puestos_repo import puesto_desde_oferta
from servicios.sugeridor import analizar_puesto, sugerir

S = estado.servicios()
estilo.encabezado("Sugeridor de puestos", "Cargá tu CV y mirá qué puestos te convienen y qué te falta para cada uno.",
                  "lupa", "celeste")

if not estado.aviso_aceptado():
    estilo.aviso("Primero leé el aviso de privacidad en Inicio.", "privado", "Antes de empezar")
    st.stop()

ok, mensaje = S.llm.estado()
if not ok:
    estilo.aviso(mensaje, "error", "El modelo no está disponible")

# ---------------------------------------------------------------- 1. CV y opciones
st.markdown("## 1. Tu CV")
cv_texto = componentes.entrada_cv(S)

st.markdown("## 2. Opciones")
col1, col2 = st.columns(2)
n = col1.slider("Cuántos puestos puntuar", 1, 10, min(S.cfg.puntuar_n, 10),
                help="Cada puesto es una consulta al modelo. Sin placa de video puede tardar varios minutos en total.")
modalidades = col2.multiselect("Modalidad", ["remoto", "hibrido", "presencial"], placeholder="Cualquiera")
guardar_cache = st.checkbox("Guardar los resultados en esta computadora para no repetir cálculos", value=True)
st.caption("Puntuar tarda: cada puesto es una consulta al modelo. La primera búsqueda además prepara la base de "
           "puestos (se hace una sola vez).")

buscar = st.button("Buscar puestos", type="primary", disabled=not cv_texto or not ok)
if not cv_texto:
    st.caption("Cargá tu CV para poder buscar.")


def filtro(p):
    return not modalidades or p.modalidad_tipo in modalidades or p.modalidad_tipo == "no figura"


if buscar:
    try:
        cv = componentes.obtener_cv(S, cv_texto)
        barra = st.progress(0.0, text="Empezando…")

        def avance(etapa, i, total, detalle):
            if etapa == "puntuar":
                barra.progress(min(0.1 + 0.9 * i / max(total, 1), 1.0), text=f"Puntuando {i + 1} de {total}: {detalle}" if detalle else "Listo")
            elif etapa == "indice":
                barra.progress(0.02 + 0.08 * i / max(total, 1), text=f"{detalle} ({i}/{total})")
            else:
                barra.progress(0.01, text=detalle)

        st.session_state["resultados_sugeridor"] = sugerir(
            cv, S.llm, S.cfg, S.puestos, n=n, filtro=filtro,
            cache=CachePuntajes() if guardar_cache else None, progreso=avance)
        st.session_state["cv_de_resultados"] = cv
        barra.empty()
    except (LLMError, ErrorArchivo) as e:
        st.session_state.pop("resultados_sugeridor", None)
        estilo.aviso(str(e), "error", "No pude completar la búsqueda")

# ---------------------------------------------------------------- 3. resultados
sug = st.session_state.get("resultados_sugeridor")
if sug:
    st.markdown("## 3. Puestos sugeridos")
    for a in sug.avisos:
        estilo.aviso(a, "alerta")
    if not sug.resultados:
        estilo.aviso("Ningún puesto coincide con los filtros elegidos.", "info")
    for i, res in enumerate(sug.resultados, 1):
        componentes.mostrar_resultado(res, i, S.puestos)
    sin_puntuar = [c.puesto.titulo for c in sug.busqueda.candidatos[len(sug.resultados):]]
    if sin_puntuar:
        with st.expander(f"Otros {len(sin_puntuar)} puestos parecidos (sin puntuar)"):
            st.markdown("".join(f"- {esc(t)}\n" for t in sin_puntuar))
    st.caption("Los puntajes son orientativos: herramientas e idiomas se calculan con reglas; experiencia y formación "
               "los estima un modelo chico, que puede equivocarse.")

    if sug.agregado:
        st.markdown("## Lo que más conviene aprender")
        filas = "".join(
            f"<li><b>{esc(f.texto)}</b>: aparece en {f.veces} de los {f.de} mejores puestos</li>" for f in sug.agregado)
        estilo.tarjeta(f"<ul>{filas}</ul>", "lila", "Brechas más repetidas", "alerta")
    with st.expander("Herramientas más pedidas en toda la base"):
        st.markdown(estilo.chips(
            [f"{f.herramienta} · {f.puestos}" + (" ✓" if f.la_tengo else "") for f in sug.herramientas],
            "menta"), unsafe_allow_html=True)
        st.caption("El número es en cuántos puestos se pide. ✓ = figura en tu CV.")

# ---------------------------------------------------------------- 4. brechas de un puesto elegido
st.markdown("## ¿Qué me falta para un puesto?")
origen = st.radio("Puesto", ["De la base", "Pegar una oferta"], horizontal=True, key="brechas_origen")
puesto = None
if origen == "De la base":
    etiquetas = {f"{p.titulo} ({p.empresa})" if p.empresa.lower() != "no figura" else p.titulo: p for p in S.puestos}
    elegido = st.selectbox("Elegí un puesto", list(etiquetas), index=None, placeholder="Elegí un puesto",
                           key="brechas_puesto")
    puesto = etiquetas.get(elegido) if elegido else None
    oferta_texto = None
else:
    oferta_texto = st.text_area("Texto de la oferta", height=200, key="brechas_oferta")

if st.button("Ver brechas", disabled=not cv_texto or not ok or (origen == "De la base" and puesto is None)
             or (origen != "De la base" and not (oferta_texto or "").strip())):
    try:
        cv = componentes.obtener_cv(S, cv_texto)
        with st.spinner("Comparando tu CV con el puesto… (puede tardar un par de minutos)"):
            if origen != "De la base":
                oferta = parsear_oferta(oferta_texto, S.llm, S.vocabulario)
                est = oferta.estructura
                est.herramientas, est.idiomas = oferta.herramientas, oferta.idiomas  # incluye lo detectado por reglas
                puesto = puesto_desde_oferta(oferta.texto, est)
            st.session_state["analisis_puesto"] = analizar_puesto(
                cv, puesto, S.llm, S.cfg, S.puestos, CachePuntajes() if guardar_cache else None)
    except (LLMError, ErrorArchivo) as e:
        st.session_state.pop("analisis_puesto", None)
        estilo.aviso(str(e), "error", "No pude analizar el puesto")

analisis = st.session_state.get("analisis_puesto")
if analisis:
    componentes.mostrar_resultado(analisis.resultado, None, S.puestos)
