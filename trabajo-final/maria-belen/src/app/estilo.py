"""Estilo 8 bits, minimalista, en colores pasteles.

Todo el aspecto vive acá: paleta, tipografías pixel, sombras duras sin bordes redondeados,
íconos dibujados con cuadraditos (SVG con `crispEdges`) y barras de puntaje hechas con bloques.
Los textos que vienen del usuario o del modelo se escapan siempre antes de ir al HTML.
"""
from __future__ import annotations

import html
import re

import streamlit as st

PALETA = {
    "crema": "#FBF4E9", "tinta": "#4A4458", "rosa": "#F7C6D9", "menta": "#BFE8D4", "celeste": "#BFDDF5",
    "lila": "#D9CCF2", "durazno": "#FFD9B8", "limon": "#FBF0B2", "blanco": "#FFFFFF",
}
COLORES_TARJETA = ("crema", "blanco", "rosa", "menta", "celeste", "lila", "durazno", "limon")

CSS = """
@font-face { font-family: 'Press Start 2P'; src: url('/app/static/PressStart2P.woff2') format('woff2'); font-display: swap; }
@font-face { font-family: 'Pixelify Sans'; font-weight: 400; src: url('/app/static/PixelifySans-400.woff2') format('woff2'); font-display: swap; }
@font-face { font-family: 'Pixelify Sans'; font-weight: 700; src: url('/app/static/PixelifySans-700.woff2') format('woff2'); font-display: swap; }
:root { --crema:#FBF4E9; --tinta:#4A4458; --rosa:#F7C6D9; --menta:#BFE8D4; --celeste:#BFDDF5; --lila:#D9CCF2;
        --durazno:#FFD9B8; --limon:#FBF0B2; --blanco:#FFFFFF; --borde:3px solid var(--tinta); --sombra:4px 4px 0 var(--tinta); }
html, body, .stApp, [class*="st-"], .stMarkdown, p, li, label, input, textarea, select, button {
  font-family: 'Pixelify Sans', ui-monospace, monospace !important; }
.stApp { background: var(--crema); color: var(--tinta); font-size: 19px; }
h1, h2, h3, h4, .stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-family: 'Press Start 2P', ui-monospace, monospace !important; color: var(--tinta); line-height: 1.7 !important;
  letter-spacing: 0; font-weight: 400 !important; }
h1 *, h2 *, h3 *, h4 *, .stApp h1 *, .stApp h2 *, .stApp h3 *, .stApp h4 * { font-family: 'Press Start 2P', ui-monospace, monospace !important; font-weight: 400 !important; }
h1, .stApp h1 { font-size: 20px !important; } h2, .stApp h2 { font-size: 15px !important; } h3, .stApp h3 { font-size: 12px !important; }
[data-testid="stDecoration"], footer, #MainMenu { display: none !important; }
[data-testid="stHeader"] { background: var(--crema); border-bottom: var(--borde); }
[data-testid="stMainBlockContainer"], .block-container { max-width: 880px; padding-top: 5rem; }
[data-testid="stAppDeployButton"], .stAppDeployButton, [data-testid="stToolbarActions"] { display: none !important; }
[data-testid="stIconMaterial"], .material-icons, [class*="material-symbols"] { font-family: 'Material Symbols Rounded' !important; }
code, [data-testid="stMarkdownContainer"] code { font-family: 'Pixelify Sans', monospace !important; background: var(--limon) !important; color: var(--tinta) !important; border: 2px solid var(--tinta); border-radius: 0 !important; padding: 0 .3rem; font-size: .9em; }
a { color: var(--tinta); text-decoration: underline; text-decoration-thickness: 3px; text-underline-offset: 3px; }
a:hover { background: var(--limon); }
:focus-visible { outline: 3px dashed var(--tinta) !important; outline-offset: 3px; }

/* botones */
.stButton > button, .stDownloadButton > button, [data-testid^="stBaseButton"] {
  border: var(--borde) !important; border-radius: 0 !important; box-shadow: var(--sombra); background: var(--menta) !important;
  color: var(--tinta) !important; font-family: 'Press Start 2P', monospace !important; font-size: 11px !important;
  padding: .85rem 1.1rem !important; line-height: 1.6 !important; transition: none !important; }
.stButton > button p, .stDownloadButton > button p, [data-testid^="stBaseButton"] p { font-family: 'Press Start 2P', monospace !important; font-size: 11px !important; }
button[kind="primary"], [data-testid="stBaseButton-primary"] { background: var(--rosa) !important; }
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid^="stBaseButton"]:hover { background: var(--limon) !important; transform: translate(-1px,-1px); box-shadow: 5px 5px 0 var(--tinta); }
.stButton > button:active, .stDownloadButton > button:active, [data-testid^="stBaseButton"]:active { transform: translate(4px,4px); box-shadow: 0 0 0 var(--tinta); }
button:disabled { opacity: .55; box-shadow: none !important; }

[data-testid="stPageLink-NavLink"] { border: var(--borde); box-shadow: var(--sombra); background: var(--limon); border-radius: 0 !important;
  padding: .6rem .9rem; margin: 0 0 1.4rem 0; width: fit-content; text-decoration: none; }
[data-testid="stPageLink-NavLink"]:hover { background: var(--rosa); }
[data-testid="stPageLink-NavLink"] p { font-family: 'Press Start 2P', monospace !important; font-size: 11px !important; line-height: 1.6; }
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] { color: var(--tinta) !important; }
[data-testid="stExpandSidebarButton"] { border: var(--borde); border-radius: 0 !important; background: var(--menta); }

/* campos */
[data-baseweb="textarea"], [data-baseweb="input"], [data-baseweb="select"] > div, [data-testid="stTextArea"] textarea {
  border: var(--borde) !important; border-radius: 0 !important; background: var(--blanco) !important; box-shadow: none !important; }
[data-baseweb="textarea"] textarea, [data-baseweb="input"] input { font-size: 18px !important; }
[data-testid="stFileUploaderDropzone"] { border: 3px dashed var(--tinta) !important; border-radius: 0 !important; background: var(--celeste) !important; }
[data-testid="stSlider"] [role="slider"] { border-radius: 0 !important; border: var(--borde); }
label p, [data-testid="stWidgetLabel"] p { font-size: 18px !important; font-weight: 700; }

/* contenedores */
[data-testid="stExpander"] details { border: var(--borde) !important; border-radius: 0 !important; background: var(--blanco); box-shadow: var(--sombra); }
[data-testid="stExpander"] summary { font-family: 'Press Start 2P', monospace !important; font-size: 11px; line-height: 1.7; }
[data-testid="stExpander"] summary p { font-family: 'Press Start 2P', monospace !important; font-size: 11px !important; }
[data-testid="stAlert"] { border: var(--borde) !important; border-radius: 0 !important; background: var(--durazno) !important; color: var(--tinta) !important; }
[data-testid="stAlert"] * { color: var(--tinta) !important; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 0 !important; }
button[data-baseweb="tab"] { font-family: 'Press Start 2P', monospace !important; font-size: 11px; }
[data-baseweb="tab-highlight"] { background: var(--rosa) !important; height: 5px !important; }
[data-baseweb="tab-border"] { background: var(--tinta) !important; height: 3px !important; }
[data-testid="stProgress"] > div > div { border-radius: 0 !important; border: var(--borde); background: var(--blanco) !important; height: 1.1rem; }
[data-testid="stProgress"] [role="progressbar"] > div { background: var(--menta) !important; border-radius: 0 !important; }

/* piezas propias */
.pix-card { border: var(--borde); box-shadow: var(--sombra); padding: 1.1rem 1.3rem; margin: 0 0 1.4rem 0; background: var(--blanco); }
.pix-card > .pix-card-titulo { font-family: 'Press Start 2P', monospace; font-size: 11px; line-height: 1.7; margin: 0 0 .7rem 0; display: flex; gap: .6rem; align-items: center; }
.pix-card p { margin: 0 0 .6rem 0; } .pix-card p:last-child { margin-bottom: 0; } .pix-card ul { margin: .3rem 0 0 0; padding-left: 1.3rem; }
.pix-crema { background: var(--crema); } .pix-blanco { background: var(--blanco); } .pix-rosa { background: var(--rosa); } .pix-menta { background: var(--menta); }
.pix-celeste { background: var(--celeste); } .pix-lila { background: var(--lila); } .pix-durazno { background: var(--durazno); } .pix-limon { background: var(--limon); }
.pix-head { display: flex; gap: 1rem; align-items: center; margin: 0 0 .4rem 0; }
.pix-head h1 { margin: 0 !important; padding: 0 !important; }
.pix-sub { font-size: 20px; margin: .3rem 0 1.6rem 0; }
.pix-chip { display: inline-block; border: 2px solid var(--tinta); padding: .1rem .55rem; margin: 0 .35rem .35rem 0; font-size: 16px; line-height: 1.4; }
.pix-barra { display: inline-flex; gap: 3px; vertical-align: middle; }
.pix-barra i { width: 14px; height: 16px; border: 2px solid var(--tinta); background: var(--blanco); display: block; }
.pix-barra i.on { background: var(--tinta); }
.pix-num { font-family: 'Press Start 2P', monospace; font-size: 12px; margin-left: .7rem; vertical-align: middle; }
.pix-ico { image-rendering: pixelated; shape-rendering: crispEdges; flex: none; }
.pix-marca { background: var(--rosa); border-bottom: 3px solid var(--tinta); padding: 0 .15rem; }
@media (max-width: 640px) {
  .stApp { font-size: 18px; } h1, .stApp h1 { font-size: 13px !important; } h2, .stApp h2 { font-size: 11px !important; } h3, .stApp h3 { font-size: 10px !important; }
  [data-testid="stMainBlockContainer"], .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 4.2rem; }
  .pix-barra i { width: 10px; height: 14px; } .pix-card { padding: .9rem 1rem; box-shadow: 3px 3px 0 var(--tinta); }
}
"""

# Íconos de 8 x 8 cuadraditos ("#" = relleno).
ICONOS = {
    "estrella": ["...##...", "...##...", ".######.", "########", ".######.", "..####..", ".##..##.", "##....##"],
    "lupa": [".####...", "#....#..", "#....#..", "#....#..", ".####...", "....##..", ".....##.", "......##"],
    "hoja": ["#####...", "#...##..", "#...####", "#......#", "#.####.#", "#......#", "#.####.#", "########"],
    "candado": ["..####..", ".#....#.", ".#....#.", "########", "###..###", "###..###", "########", "########"],
    "check": ["........", "......##", ".....##.", "##..##..", ".####...", "..##....", "........", "........"],
    "alerta": ["...##...", "..####..", "..####..", ".##..##.", ".##..##.", "##.##.##", "########", "........"],
}


def esc(texto) -> str:
    return html.escape(str(texto), quote=True)


def esc_codigo(texto) -> str:
    """Escapa y convierte `así` en <code>así</code> (para mensajes con comandos)."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", esc(texto))


def _compacto(fragmento: str) -> str:
    """Markdown corta los bloques HTML en las líneas vacías y toma como código lo que tiene sangría."""
    return "".join(linea.strip() for linea in fragmento.splitlines())


compacto = _compacto


def icono(nombre: str, px: int = 4, fondo: str | None = None) -> str:
    filas = ICONOS[nombre]
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y, fila in enumerate(filas)
                    for x, c in enumerate(fila) if c == "#")
    svg = (f'<svg class="pix-ico" width="{8 * px}" height="{8 * px}" viewBox="0 0 8 8" '
           f'shape-rendering="crispEdges" aria-hidden="true" fill="#4A4458">{rects}</svg>')
    if fondo:
        svg = (f'<span style="display:inline-flex;padding:6px;background:var(--{fondo});border:3px solid var(--tinta);'
               f'box-shadow:3px 3px 0 var(--tinta)">{svg}</span>')
    return svg


def inyectar_estilo() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def encabezado(titulo: str, subtitulo: str = "", icono_nombre: str | None = "estrella", fondo: str = "rosa") -> None:
    ico = icono(icono_nombre, 4, fondo) if icono_nombre else ""
    sub = f'<p class="pix-sub">{esc(subtitulo)}</p>' if subtitulo else ""
    st.markdown(_compacto(f'<div class="pix-head">{ico}<h1>{esc(titulo)}</h1></div>{sub}'), unsafe_allow_html=True)


def tarjeta_html(cuerpo_html: str, color: str = "blanco", titulo: str | None = None, icono_nombre: str | None = None) -> str:
    if color not in COLORES_TARJETA:
        raise ValueError(f"Color de tarjeta desconocido: {color}")
    cab = ""
    if titulo:
        cab = f'<div class="pix-card-titulo">{icono(icono_nombre, 3) if icono_nombre else ""}<span>{esc(titulo)}</span></div>'
    return _compacto(f'<div class="pix-card pix-{color}">{cab}{cuerpo_html}</div>')


def tarjeta(cuerpo_html: str, color: str = "blanco", titulo: str | None = None, icono_nombre: str | None = None) -> None:
    """`cuerpo_html` debe venir ya escapado (usá `esc()` para cualquier texto de afuera)."""
    st.markdown(tarjeta_html(cuerpo_html, color, titulo, icono_nombre), unsafe_allow_html=True)


def aviso(texto: str, tipo: str = "info", titulo: str | None = None) -> None:
    color, ico = {"info": ("celeste", "lupa"), "ok": ("menta", "check"), "alerta": ("durazno", "alerta"),
                  "error": ("rosa", "alerta"), "privado": ("lila", "candado")}[tipo]
    tarjeta(f"<p>{esc_codigo(texto)}</p>", color, titulo, ico)


def chip(texto: str, color: str = "celeste") -> str:
    return f'<span class="pix-chip pix-{color}">{esc(texto)}</span>'


def chips(textos, color: str = "celeste") -> str:
    return "".join(chip(t, color) for t in textos)


def barra_puntaje(puntaje: int | float | None, bloques: int = 10) -> str:
    """Barra de bloques (cada bloque = 10 puntos) más el número; `None` muestra «s/d»."""
    if puntaje is None:
        return '<span class="pix-barra">' + "<i></i>" * bloques + '</span><span class="pix-num">s/d</span>'
    p = max(0, min(100, round(puntaje)))
    llenos = round(p / 100 * bloques)
    clase = "bajo" if p < 40 else "medio" if p < 70 else ""
    celdas = "".join(f'<i class="on {clase}"></i>' if n < llenos else "<i></i>" for n in range(bloques))
    return (f'<span class="pix-barra" role="img" aria-label="Puntaje {p} de 100">{celdas}</span>'
            f'<span class="pix-num">{p}</span>')


def resaltar(texto: str, fragmentos) -> str:
    """Escapa `texto` y resalta cada fragmento (para marcar lo que el verificador no pudo respaldar)."""
    salida = esc(texto)
    claves = sorted({esc(x) for x in fragmentos if x}, key=len, reverse=True)
    if claves:  # una sola pasada: un fragmento dentro de otro no genera marcas anidadas
        patron = re.compile("|".join(re.escape(c) for c in claves))
        salida = patron.sub(lambda m: f'<mark class="pix-marca">{m.group(0)}</mark>', salida)
    return salida.replace("\n", "<br>")
