import hashlib
import json

import numpy as np
import pytest

from servicios.config import EJEMPLOS_DIR, cargar_config
from servicios.cv_parser import parsear_cv
from servicios.llm_client import LLMClient, LLMError
from servicios.puestos_repo import cargar_puestos
from servicios.recuperador import Recuperador, consulta_desde_cv
from servicios.schemas import CVEstructurado
from servicios.texto import palabras
from tests.falsos import LLMFalso

CFG = cargar_config({})
PUESTOS = cargar_puestos()
CV_JUNIOR = (EJEMPLOS_DIR / "cv-ejemplo-junior.md").read_text(encoding="utf-8")
CV_SEMI = (EJEMPLOS_DIR / "cv-ejemplo-semisenior.md").read_text(encoding="utf-8")


class Embedder:
    """Embeddings falsos: bolsa de palabras hasheada (sirve para probar el orden y el índice)."""

    def __init__(self, error=None):
        self.llamadas, self.error = [], error

    def embeber(self, textos):
        self.llamadas.append(len(textos))
        if self.error:
            raise self.error
        salida = []
        for t in textos:
            v = np.zeros(512)
            for w in palabras(t, 4):
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % 512] += 1
            salida.append(v.tolist())
        return salida


def cv(texto):
    return parsear_cv(texto, LLMFalso(CVEstructurado()), CFG)


def titulos(res):
    return [c.puesto.titulo.lower() for c in res.candidatos]


def test_indice_se_crea_se_guarda_y_se_reutiliza(tmp_path):
    emb = Embedder()
    r = Recuperador(emb, CFG, PUESTOS, tmp_path)
    assert r.asegurar_indice() == 40
    assert sum(emb.llamadas) == 40 and max(emb.llamadas) <= 8
    assert (tmp_path / "vectores.npy").exists() and json.loads((tmp_path / "meta.json").read_text())["modelo"] == "ollama:bge-m3"
    emb2 = Embedder()
    r2 = Recuperador(emb2, CFG, PUESTOS, tmp_path)
    assert r2.asegurar_indice() == 0 and emb2.llamadas == []


def test_solo_se_rehacen_los_puestos_que_cambiaron(tmp_path):
    Recuperador(Embedder(), CFG, PUESTOS, tmp_path).asegurar_indice()
    modificados = [*PUESTOS]
    from dataclasses import replace
    modificados[3] = replace(PUESTOS[3], cuerpo=PUESTOS[3].cuerpo + "\nNuevo requisito: SEO técnico.")
    emb = Embedder()
    assert Recuperador(emb, CFG, modificados, tmp_path).asegurar_indice() == 1 and emb.llamadas == [1]


def test_cambio_de_modelo_reconstruye_todo(tmp_path):
    Recuperador(Embedder(), CFG, PUESTOS, tmp_path).asegurar_indice()
    otro = cargar_config({"EMBEDDINGS_MODELO": "nomic-embed-text"})
    assert Recuperador(Embedder(), otro, PUESTOS, tmp_path).asegurar_indice() == 40


def test_indice_corrupto_se_reconstruye(tmp_path):
    Recuperador(Embedder(), CFG, PUESTOS, tmp_path).asegurar_indice()
    (tmp_path / "vectores.npy").write_bytes(b"basura")
    assert Recuperador(Embedder(), CFG, PUESTOS, tmp_path).asegurar_indice() == 40


def test_busqueda_devuelve_k_ordenados_y_relevantes(tmp_path):
    r = Recuperador(Embedder(), CFG, PUESTOS, tmp_path)
    res = r.buscar(cv(CV_JUNIOR), k=10)
    assert res.metodo == "embeddings" and not res.avisos and len(res.candidatos) == 10
    sims = [c.similitud for c in res.candidatos]
    assert sims == sorted(sims, reverse=True)
    assert any(("community" in t or "redes" in t or "social" in t) for t in titulos(res)[:10]), titulos(res)


def test_filtro_y_k(tmp_path):
    r = Recuperador(Embedder(), CFG, PUESTOS, tmp_path)
    res = r.buscar(cv(CV_SEMI), k=5, filtro=lambda p: p.modalidad_tipo == "remoto")
    assert 0 < len(res.candidatos) <= 5 and all(c.puesto.modalidad_tipo == "remoto" for c in res.candidatos)


def test_plan_b_por_palabras_si_fallan_los_embeddings(tmp_path):
    r = Recuperador(Embedder(error=LLMError("modelo no descargado")), CFG, PUESTOS, tmp_path)
    res = r.buscar(cv(CV_JUNIOR), k=10)
    assert res.metodo == "palabras" and "palabras en común" in res.avisos[0]
    assert len(res.candidatos) == 10
    assert any(("community" in t or "redes" in t or "social" in t) for t in titulos(res)[:10]), titulos(res)


def test_consulta_no_incluye_contacto_y_se_acota():
    c = cv(CV_JUNIOR)
    c.estructura.experiencias = []
    q = consulta_desde_cv(c, 4000)
    assert "Herramientas" in q or "Canva" in q
    assert len(consulta_desde_cv(c, 300)) <= 300
    assert consulta_desde_cv("texto libre", 4000) == "texto libre"


def test_funciona_con_el_cliente_real_contra_ollama_falso(ollama_falso, tmp_path):
    llm = LLMClient(cargar_config({"OLLAMA_URL": ollama_falso.url}))
    r = Recuperador(llm, CFG, PUESTOS, tmp_path)
    res = r.buscar(CV_JUNIOR, k=3)
    assert res.metodo == "embeddings" and len(res.candidatos) == 3
    pedidos = [p for p in ollama_falso.pedidos if p["ruta"] == "/api/embed"]
    assert sum(len(p["input"]) for p in pedidos) == 41  # 40 puestos + la consulta
