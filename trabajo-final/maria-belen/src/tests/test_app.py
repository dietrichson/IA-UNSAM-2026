import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "app"))

import estado  # noqa: E402
import estilo  # noqa: E402
from servicios.llm_client import LLMClient  # noqa: E402

MAIN = str(RAIZ / "app" / "main.py")


def app(ollama_ok: bool, monkeypatch):
    monkeypatch.setattr(LLMClient, "estado", lambda self: (True, "Listo.") if ollama_ok else (False, "No encuentro Ollama. Ejecutá `ollama serve`."))
    return AppTest.from_file(MAIN, default_timeout=30).run()


def textos(at):
    return " ".join(m.value for m in at.markdown)


# ---------------------------------------------------------------- pantallas
def test_primera_pantalla_sin_ollama_bloquea_el_inicio(monkeypatch):
    at = app(False, monkeypatch)
    assert not at.exception
    assert "Falta algo para empezar" in textos(at) and "<code>ollama serve</code>" in textos(at)
    entendido = next(b for b in at.button if b.label == "Entendido, empezar")
    assert entendido.disabled
    assert any(b.label == "Continuar de todos modos" for b in at.button)


def test_aceptar_el_aviso_habilita_la_app(monkeypatch):
    at = app(True, monkeypatch)
    assert "Todo listo" in textos(at) and "qwen2.5:3b" in textos(at)
    next(b for b in at.button if b.label == "Entendido, empezar").click().run()
    assert at.session_state["aviso_ok"] is True and not at.exception
    assert "Sugeridor de puestos" in textos(at) and "Adaptador de CV y carta" in textos(at)


def test_modo_nube_advierte_que_se_envia_texto(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    estado.servicios.clear()
    try:
        at = app(True, monkeypatch)
        assert "Modo nube" in textos(at) and "se envía a" in textos(at)
    finally:
        monkeypatch.delenv("LLM_PROVIDER"); monkeypatch.delenv("GEMINI_API_KEY")
        estado.servicios.clear()


@pytest.mark.parametrize("pagina", ["paginas/sugeridor.py", "paginas/adaptador.py"])
def test_las_pantallas_piden_leer_el_aviso_primero(monkeypatch, pagina):
    at = app(True, monkeypatch)
    at.switch_page(pagina).run()
    assert not at.exception and "Primero leé el aviso" in textos(at)


# ---------------------------------------------------------------- estado
def test_borrar_datos_locales(tmp_path, monkeypatch):
    local = tmp_path / "local"
    local.mkdir()
    (local / "cache_puntajes.json").write_text("{}")
    (local / "cv.txt").write_text("x")
    monkeypatch.setattr(estado, "LOCAL_DIR", local)
    assert estado.borrar_datos_locales() == 2 and not local.exists()
    assert estado.borrar_datos_locales() == 0


# ---------------------------------------------------------------- estilo
def test_barra_de_puntaje():
    b = estilo.barra_puntaje(72)
    assert b.count('<i class="on') == 7 and b.count("<i></i>") == 3 and ">72<" in b and 'aria-label="Puntaje 72 de 100"' in b
    assert "bajo" in estilo.barra_puntaje(20) and "medio" in estilo.barra_puntaje(55) and "medio" not in estilo.barra_puntaje(90)
    assert "s/d" in estilo.barra_puntaje(None)
    assert ">100<" in estilo.barra_puntaje(250) and ">0<" in estilo.barra_puntaje(-5)


def test_el_texto_externo_se_escapa():
    malo = '<script>alert(1)</script>"&'
    assert "<script>" not in estilo.chip(malo) and "<script>" not in estilo.tarjeta_html(f"<p>{estilo.esc(malo)}</p>", "rosa", malo)
    r = estilo.resaltar('Trabajé en <b>Globant</b> y Globant', ["Globant", "<b>Globant</b>"])
    assert "<b>" not in r.replace("<mark", "").replace("</mark>", "") or "&lt;b&gt;" in r
    assert r.count('<mark class="pix-marca">') == 2 and "&lt;b&gt;Globant&lt;/b&gt;</mark>" in r


def test_tarjeta_no_tiene_lineas_vacias_ni_sangria():
    h = estilo.tarjeta_html("<p>a</p>\n\n    <p>b</p>", "menta", "Título", "check")
    assert "\n" not in h and 'class="pix-card pix-menta"' in h
    with pytest.raises(ValueError):
        estilo.tarjeta_html("x", "violeta")


def test_iconos_son_de_8x8_y_nitidos():
    for nombre, filas in estilo.ICONOS.items():
        assert len(filas) == 8 and all(len(f) == 8 for f in filas), nombre
        assert 'shape-rendering="crispEdges"' in estilo.icono(nombre)


def test_esc_codigo():
    assert estilo.esc_codigo("Ejecutá `ollama pull x` <ya>") == "Ejecutá <code>ollama pull x</code> &lt;ya&gt;"
