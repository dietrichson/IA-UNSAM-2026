"""Inicio: aviso de privacidad (obligatorio la primera vez), estado del modelo y presentación."""
import streamlit as st

import estado
import estilo
from estilo import esc

S = estado.servicios()
cfg = S.cfg

estilo.encabezado("Copiloto de búsqueda laboral", "Para estudiantes y graduados/as de Comunicación.", "estrella")

# ---------------------------------------------------------------- privacidad
if cfg.es_local:
    estilo.tarjeta(
        "<p>Con esta configuración <b>todo se procesa en tu computadora</b> con Ollama. "
        "Tu CV y las ofertas que pegues <b>no se envían a internet</b>.</p>", "lila", "Modo local", "candado")
else:
    destinos = []
    if cfg.provider != "ollama":
        destinos.append({"gemini": "Google (Gemini)", "claude": "Anthropic (Claude)"}[cfg.provider])
    if cfg.embeddings_provider != "ollama":
        destinos.append("Google (embeddings)")
    estilo.tarjeta(
        f"<p>Está activado un proveedor en la nube. El <b>texto de tu CV y de las ofertas se envía a: "
        f"{esc(', '.join(destinos))}</b>. Si no querés eso, volvé a Ollama en el archivo <code>.env</code>.</p>",
        "durazno", "Modo nube", "alerta")

with st.expander("¿Qué pasa con mis datos?", expanded=not estado.aviso_aceptado()):
    st.markdown(
        "- Tu CV y las ofertas se usan **solo mientras la app está abierta**; no hay cuentas ni base de datos de usuarios.\n"
        "- Para no repetir cálculos lentos, la app guarda **en tu computadora** (carpeta `data/local/`) los puntajes ya "
        "calculados. Ese caché incluye frases de tu CV usadas como evidencia. Podés borrarlo con el botón de abajo.\n"
        "- Los CV de `data/ejemplos/` son ficticios.\n"
        "- La base de **40 puestos** es una muestra de avisos públicos relevados entre el 26/10 y el 3/11/2026; "
        "puede estar desactualizada y no es el mercado completo.\n"
        "- Los puntajes y los textos generados son **orientativos**. Un modelo chico puede equivocarse: "
        "revisá todo antes de enviar algo a una empresa."
    )

# ---------------------------------------------------------------- estado del modelo
ok, mensaje = S.llm.estado()
if ok:
    estilo.tarjeta(
        f"<p>Modelo principal: <b>{esc(cfg.modelo_principal)}</b> · Embeddings: <b>{esc(cfg.modelo_embeddings)}</b></p>",
        "menta", "Todo listo", "check")
else:
    estilo.tarjeta(f"<p>{estilo.esc_codigo(mensaje)}</p>", "rosa", "Falta algo para empezar", "alerta")
    st.button("Revisar de nuevo")  # al hacer clic Streamlit vuelve a ejecutar la página

if not estado.aviso_aceptado():
    st.button("Entendido, empezar", type="primary", on_click=estado.aceptar_aviso, disabled=not ok,
              help=None if ok else "Resolvé lo de arriba y revisá de nuevo.")
    if not ok:
        st.caption("Podés leer la app igual, pero no va a funcionar hasta que el modelo esté disponible.")
        st.button("Continuar de todos modos", on_click=estado.aceptar_aviso)
else:
    estilo.tarjeta("<p>Cargás tu CV y la app te sugiere puestos de la base y te dice qué te falta para cada uno.</p>",
                   "celeste", "Sugeridor de puestos", "lupa")
    st.page_link("paginas/sugeridor.py", label="Ir al Sugeridor")
    estilo.tarjeta("<p>Pegás una oferta y la app adapta tu CV y escribe una carta, usando <b>solo</b> lo que ya figura "
                   "en tu CV. Marca lo que no pudo respaldar.</p>", "rosa", "Adaptador de CV y carta", "hoja")
    st.page_link("paginas/adaptador.py", label="Ir al Adaptador")
    with st.expander("Borrar datos guardados"):
        st.write("Elimina el caché de puntajes y cualquier CV guardado en esta computadora.")
        if st.button("Borrar ahora"):
            n = estado.borrar_datos_locales()
            st.success(f"Listo: se borraron {n} archivo(s).")
