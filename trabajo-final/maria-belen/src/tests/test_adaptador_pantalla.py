import io
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from servicios import config as cfg_mod
from servicios import matcher
from servicios.config import cargar_config
from servicios.exportar import a_docx
from servicios.llm_client import LLMError
from servicios.puestos_repo import cargar_puestos
from tests.falsos import LLMCompleto

CFG = cargar_config({})
RAIZ = Path(__file__).resolve().parent.parent
OFERTA = ("Community Manager en Agencia Brújula. Requisitos: manejo de Canva y Meta Ads; inglés intermedio. "
          "Se valora Premiere. Modalidad híbrida en Buenos Aires.")
BUENO = ("# Camila Rojas\n\n## Experiencia\n- Community manager voluntaria en Centro Cultural La Esquina: aumento de seguidores "
         "de Instagram de 800 a 1.500 en 8 meses, con piezas diseñadas en Canva.\n\n## Herramientas\nCanva, Instagram, Facebook.")
MALO = BUENO + "\n- Gestioné campañas en Agencia Meridiano con Photoshop."


def textos(at):
    return " ".join(m.value for m in at.markdown)


@pytest.fixture
def pantalla(tmp_path, monkeypatch):
    sys.path.insert(0, str(RAIZ / "app"))
    import estado
    monkeypatch.setattr(cfg_mod, "INDICE_DIR", tmp_path / "indice")
    monkeypatch.setattr(matcher, "LOCAL_DIR", tmp_path / "local")
    monkeypatch.setattr(estado, "LOCAL_DIR", tmp_path / "local")
    fake = LLMCompleto()
    monkeypatch.setattr(estado, "servicios", lambda: estado.Servicios(CFG, fake, cargar_puestos(), []))
    at = AppTest.from_file(str(RAIZ / "app" / "main.py"), default_timeout=60)
    at.session_state["aviso_ok"] = True
    at.run()
    at.switch_page("paginas/adaptador.py").run()
    at.radio(key="cv_origen").set_value("Usar un ejemplo").run()
    return at, fake


def analizar(at):
    at.text_area(key="oferta_texto").set_value(OFERTA).run()
    next(b for b in at.button if b.label == "Analizar oferta").click().run()
    assert not at.exception, at.exception


def boton(at, etiqueta):
    return next(b for b in at.button if b.label == etiqueta)


def test_sin_oferta_no_deja_analizar(pantalla):
    at, _ = pantalla
    assert not at.exception and boton(at, "Analizar oferta").disabled


def test_analisis_muestra_palabras_presentes_y_faltantes(pantalla):
    at, _ = pantalla
    analizar(at)
    t = textos(at)
    assert "Ya están en tu CV" in t and "No figuran en tu CV" in t
    assert ">Canva<" in t.replace("</span>", "<") or "Canva" in t
    assert "Meta Ads" in t and "Premiere" in t
    assert any(b.label == "Adaptar mi CV" for b in at.button)


def test_cv_fiel_queda_verificado(pantalla):
    at, fake = pantalla
    analizar(at)
    fake.textos = [BUENO]
    boton(at, "Adaptar mi CV").click().run()
    assert not at.exception, at.exception
    t = textos(at)
    assert "Tu CV adaptado" in t and "Verificado" in t and "Revisá esto" not in t
    assert at.text_area(key="edit_cv").value == BUENO


def test_invencion_persistente_se_marca_y_se_puede_corregir(pantalla):
    at, fake = pantalla
    analizar(at)
    fake.textos = [MALO, MALO]
    boton(at, "Adaptar mi CV").click().run()
    t = textos(at)
    assert "Revisá esto" in t and '<mark class="pix-marca">Photoshop</mark>' in t and "Agencia Meridiano" in t
    at.text_area(key="edit_cv").set_value(BUENO).run()
    boton(at, "Revisar mi edición").click().run()
    t = textos(at)
    assert "Revisá esto" not in t and "Verificado" in t


def test_carta_usa_el_tono_elegido(pantalla):
    at, fake = pantalla
    analizar(at)
    at.selectbox(key="tono").set_value("formal").run()
    fake.textos = ["Estimado equipo de Agencia Brújula:\n\nMe postulo. En el Centro Cultural La Esquina aumenté seguidores "
                   "de 800 a 1.500 con Canva.\n\nSaludos,\nCamila Rojas"]
    boton(at, "Escribir la carta").click().run()
    assert not at.exception and "Tu carta de presentación" in textos(at) and "Verificado" in textos(at)


def test_cambiar_la_oferta_pide_analizar_de_nuevo(pantalla):
    at, _ = pantalla
    analizar(at)
    at.text_area(key="oferta_texto").set_value(OFERTA + " Cambio.").run()
    assert "Cambiaste el CV o la oferta" in textos(at) and not any(b.label == "Adaptar mi CV" for b in at.button)


def test_error_del_modelo_se_muestra_sin_romper(pantalla):
    at, fake = pantalla
    analizar(at)
    fake.chat_texto = lambda *a, **k: (_ for _ in ()).throw(LLMError("Ollama se cayó"))
    boton(at, "Adaptar mi CV").click().run()
    assert not at.exception and "Ollama se cayó" in textos(at)


def test_docx_exportado_se_puede_abrir():
    docx = pytest.importorskip("docx")
    d = docx.Document(io.BytesIO(a_docx("# Título\n\n- **Negrita** y texto & <símbolos>\nLínea normal.")))
    assert [p.text for p in d.paragraphs] == ["Título", "", "• Negrita y texto & <símbolos>", "Línea normal."]
    assert d.paragraphs[0].runs[0].bold is True
