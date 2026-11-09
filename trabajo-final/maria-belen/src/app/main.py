"""Copiloto de búsqueda laboral para Comunicación. Se ejecuta con: streamlit run app/main.py"""
import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parent.parent
for _ruta in (str(_RAIZ), str(_RAIZ / "app")):
    if _ruta not in sys.path:
        sys.path.insert(0, _ruta)

import streamlit as st  # noqa: E402

import estado  # noqa: E402
import estilo  # noqa: E402

st.set_page_config(page_title="Copiloto laboral", page_icon="⭐", layout="centered")
estilo.inyectar_estilo()

PAGINAS = Path(__file__).resolve().parent / "paginas"
navegacion = st.navigation(
    [st.Page(PAGINAS / "inicio.py", title="Inicio", default=True),
     st.Page(PAGINAS / "sugeridor.py", title="Sugeridor de puestos", url_path="sugeridor"),
     st.Page(PAGINAS / "adaptador.py", title="Adaptador de CV y carta", url_path="adaptador")],
    position="top",
)
navegacion.run()
