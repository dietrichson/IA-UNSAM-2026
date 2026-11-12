import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from servicios import config as cfg_mod
from servicios import matcher
from servicios.config import EJEMPLOS_DIR, cargar_config
from servicios.cv_parser import parsear_cv
from servicios.matcher import CachePuntajes
from servicios.puestos_repo import cargar_puestos
from servicios.schemas import CVEstructurado
from servicios.sugeridor import analizar_puesto, sugerir
from tests.falsos import LLMCompleto, LLMFalso

CFG = cargar_config({})
PUESTOS = cargar_puestos()
RAIZ = Path(__file__).resolve().parent.parent
CV = parsear_cv((EJEMPLOS_DIR / "cv-ejemplo-junior.md").read_text(encoding="utf-8"), LLMFalso(CVEstructurado()), CFG)


def test_sugerir_recupera_puntua_y_resume(tmp_path):
    llm = LLMCompleto()
    etapas = []
    s = sugerir(CV, llm, CFG, PUESTOS, n=3, indice_dir=tmp_path, progreso=lambda e, i, t, d: etapas.append(e))
    assert len(s.resultados) == 3 and len(s.busqueda.candidatos) == 10  # K=10 recuperados, 3 puntuados
    assert llm.llamadas.count("EvaluacionLLM") == 3
    assert {"indice", "buscar", "puntuar", "listo"} <= set(etapas) and etapas[-1] == "listo"
    assert s.herramientas and all(0 <= r.puntaje <= 100 for r in s.resultados)


def test_sugerir_con_filtro_de_modalidad_y_cache(tmp_path):
    cache = CachePuntajes(tmp_path / "c.json")
    llm = LLMCompleto()
    s = sugerir(CV, llm, CFG, PUESTOS, n=2, filtro=lambda p: p.modalidad_tipo == "remoto", cache=cache, indice_dir=tmp_path)
    assert all(r.puesto.modalidad_tipo == "remoto" for r in s.resultados)
    antes = llm.llamadas.count("EvaluacionLLM")
    s2 = sugerir(CV, llm, CFG, PUESTOS, n=2, filtro=lambda p: p.modalidad_tipo == "remoto", cache=cache, indice_dir=tmp_path)
    assert llm.llamadas.count("EvaluacionLLM") == antes and all(r.desde_cache for r in s2.resultados)


def test_analizar_puesto_devuelve_brechas_y_consejo():
    p = next(x for x in PUESTOS if x.herramientas and any("Photoshop" in h for h in x.herramientas))
    a = analizar_puesto(CV, p, LLMCompleto(), CFG, PUESTOS)
    assert a.resultado.puesto is p and a.sugerencia.startswith("Por dónde empezar")
    assert any(b.texto == "Photoshop" for b in a.brechas)


# ---------------------------------------------------------------- la pantalla, de punta a punta con modelo falso
@pytest.fixture
def pantalla(tmp_path, monkeypatch):
    sys.path.insert(0, str(RAIZ / "app"))
    import estado
    monkeypatch.setattr(cfg_mod, "INDICE_DIR", tmp_path / "indice")
    monkeypatch.setattr(matcher, "LOCAL_DIR", tmp_path / "local")
    monkeypatch.setattr(estado, "LOCAL_DIR", tmp_path / "local")
    fake = LLMCompleto()
    monkeypatch.setattr(estado, "servicios", lambda: estado.Servicios(CFG, fake, PUESTOS, []))
    at = AppTest.from_file(str(RAIZ / "app" / "main.py"), default_timeout=60)
    at.session_state["aviso_ok"] = True
    at.run()
    at.switch_page("paginas/sugeridor.py").run()
    return at, fake


def textos(at):
    return " ".join(m.value for m in at.markdown)


def test_pantalla_sin_cv_no_deja_buscar(pantalla):
    at, _ = pantalla
    assert not at.exception
    assert next(b for b in at.button if b.label == "Buscar puestos").disabled


def test_pantalla_busqueda_completa(pantalla):
    at, fake = pantalla
    at.radio(key="cv_origen").set_value("Usar un ejemplo").run()
    at.slider[0].set_value(3)
    next(b for b in at.button if b.label == "Buscar puestos").click().run()
    assert not at.exception, at.exception
    t = textos(at)
    assert "Puestos sugeridos" in t and t.count("#1 ") >= 1 and "#3 " in t and "#4 " not in t
    assert fake.llamadas.count("EvaluacionLLM") == 3
    assert len(at.expander) >= 4  # detalle de cada puesto + extras


def test_pantalla_muestra_error_si_el_modelo_falla(pantalla, monkeypatch):
    from servicios.llm_client import LLMError
    at, fake = pantalla
    fake.chat_json = lambda *a, **k: (_ for _ in ()).throw(LLMError("Ollama se cayó"))
    at.radio(key="cv_origen").set_value("Usar un ejemplo").run()
    next(b for b in at.button if b.label == "Buscar puestos").click().run()
    assert not at.exception and "Ollama se cayó" in textos(at)


def test_pantalla_brechas_de_un_puesto(pantalla):
    at, _ = pantalla
    at.radio(key="cv_origen").set_value("Usar un ejemplo").run()
    at.selectbox(key="brechas_puesto").set_value(at.selectbox(key="brechas_puesto").options[0]).run()
    next(b for b in at.button if b.label == "Ver brechas").click().run()
    assert not at.exception, at.exception
    assert "Por dónde empezar" in textos(at) or "No detecté brechas" in textos(at)
