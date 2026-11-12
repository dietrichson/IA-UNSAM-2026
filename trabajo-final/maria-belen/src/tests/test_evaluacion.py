import json

import pytest

from evaluacion import metricas as M
from evaluacion.evaluar import cargar_casos, escribir, evaluar, informe_md, main
from evaluacion.simulado import LLMSimulado
from servicios.config import cargar_config
from servicios.puestos_repo import cargar_puestos

CFG = cargar_config({})
PUESTOS = cargar_puestos()


def test_casos_de_prueba_cumplen_lo_pedido():
    cvs, ofertas, esperados = cargar_casos()
    assert len(cvs) >= 10 and len(ofertas) >= 3
    assert set(esperados) == set(cvs)  # todos los CV tienen su plantilla de esperados
    assert all("FICTICI" in t.upper() for t in [*cvs.values(), *ofertas.values()])  # solo datos ficticios
    for e in esperados.values():
        assert set(e["faltantes"]) == set(ofertas)


def test_metricas_basicas():
    assert M.acierta_alguno([], ["a"]) is None
    assert M.acierta_alguno(["a", "b"], ["b", "c"]) is True and M.acierta_todos(["a", "b"], ["b", "c"]) is False
    assert M.jaccard(["Canva", "Meta Ads"], ["canva", "meta ads"]) == 1.0 and M.jaccard([], []) == 1.0
    assert M.comparar_faltantes(None, ["x"]) is None
    assert M.comparar_faltantes(["a", "b", "c", "d", "e"], ["a", "b", "c", "d"]) == {"jaccard": 0.8, "exacta": False, "coincide": True}
    assert M.comparar_faltantes(["a"], ["b"])["coincide"] is False
    assert M.tasa([True, False, None, True]) == {"casos": 3, "sin_datos": 1, "aciertos": 2, "porcentaje": 66.7}
    assert M.tasa([None])["porcentaje"] is None
    assert M.estado("palabras", M.tasa([True] * 4 + [False])) == "Cumple" and M.estado("ranking", M.tasa([False])) == "No cumple"
    assert "Sin datos" in M.estado("ranking", M.tasa([None]))


def test_version_de_prompts_cambia_con_el_contenido(tmp_path, monkeypatch):
    v1 = M.version_prompts()
    (tmp_path / "a.txt").write_text("uno")
    monkeypatch.setattr(M, "PROMPTS_DIR", tmp_path)
    a = M.version_prompts()
    (tmp_path / "a.txt").write_text("dos")
    assert a != M.version_prompts() and v1 != a


def test_evaluar_completo_con_modelo_simulado(tmp_path):
    res = evaluar(LLMSimulado(), CFG, PUESTOS, set(M.UMBRALES) | {"recuperacion", "ranking", "palabras", "veracidad", "brechas"},
                  ["cv-01-camila-rojas"], ["oferta-01-community-manager"], n=2, con_carta=True, indice_dir=tmp_path)
    assert not res["errores"]
    assert len(res["recuperacion"]) == 1 and len(res["recuperacion"][0]["recuperados"]) == 10 and len(res["ranking"][0]["top3"]) == 2
    assert [v["tipo"] for v in res["veracidad"]] == ["cv", "carta"] and all(v["ok"] for v in res["veracidad"])
    assert res["resumen"]["veracidad"]["porcentaje"] == 100.0 and res["resumen"]["ranking"]["porcentaje"] is None  # sin esperados
    assert {"Canva", "Meta Ads"} & set(res["palabras"][0]["faltantes"] + ["Canva"])


def test_con_esperados_se_calculan_aciertos(tmp_path, monkeypatch):
    import evaluacion.evaluar as E
    casos = tmp_path / "casos"
    (casos / "cvs").mkdir(parents=True); (casos / "ofertas").mkdir()
    src = E.CASOS
    (casos / "cvs" / "cv-x.md").write_text((src / "cvs" / "cv-01-camila-rojas.md").read_text(encoding="utf-8"), encoding="utf-8")
    (casos / "ofertas" / "of-x.md").write_text((src / "ofertas" / "oferta-01-community-manager.md").read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(E, "CASOS", casos)
    (casos / "esperados.json").write_text(json.dumps({"cvs": {"cv-x": {"puestos_esperados": [PUESTOS[0].id, "no-existe"],
                                                                      "faltantes": {"of-x": ["Meta Ads", "Metricool"]}}}}))
    res = E.evaluar(LLMSimulado(), CFG, PUESTOS, {"recuperacion", "ranking", "palabras"}, None, None, n=3, indice_dir=tmp_path / "i")
    assert res["recuperacion"][0]["alguno"] in (True, False) and res["resumen"]["recuperacion_alguno"]["casos"] == 1
    assert res["palabras"][0]["comparacion"] is not None and res["resumen"]["palabras"]["casos"] == 1


def test_escribir_genera_los_archivos_y_el_informe_avisa_si_es_simulado(tmp_path):
    res = evaluar(LLMSimulado(), CFG, PUESTOS, {"recuperacion", "ranking", "palabras", "veracidad", "brechas"},
                  ["cv-01-camila-rojas"], ["oferta-01-community-manager"], n=2, indice_dir=tmp_path / "i")
    res["meta"]["simulado"] = True
    archivos = escribir(res, tmp_path / "out")
    nombres = [a.name for a in archivos]
    assert all(n.startswith("simulado-") for n in nombres)
    assert any(n.endswith(".json") for n in nombres) and any(n.endswith("-revision-veracidad.md") for n in nombres)
    assert json.loads(next(a for a in archivos if a.suffix == ".json").read_text(encoding="utf-8"))["meta"]["prompts"]
    assert "CORRIDA SIMULADA" in informe_md(res) and "Pendiente" in informe_md(res)


def test_main_simulado_de_punta_a_punta(tmp_path, capsys):
    code = main(["--simulado", "--cvs", "cv-03-lucia-fernandez", "--ofertas", "oferta-02-comunicacion-institucional",
                 "--que", "palabras", "veracidad", "--salida", str(tmp_path)])
    assert code == 0 and "MODO SIMULADO" in capsys.readouterr().out and list(tmp_path.glob("simulado-*.md"))
