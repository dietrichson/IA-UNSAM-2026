"""Recuperador (la R de RAG): de los 40 puestos, elige los más parecidos a un CV.

1. Cada puesto se convierte en un vector (embedding) una sola vez; el índice se guarda en
   `data/indice/` y se rehace solo si cambia el texto de un puesto o el modelo de embeddings.
2. El CV se convierte en un vector y se ordenan los puestos por similitud coseno.
3. Si los embeddings no están disponibles (modelo sin descargar, etc.) se usa un plan B por
   palabras en común, y se avisa para que no parezca el mismo resultado.
"""
from __future__ import annotations

import json
import math
import os
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from servicios.config import INDICE_DIR, Config
from servicios.llm_client import LLMError
from servicios.puestos_repo import Puesto
from servicios.texto import hash_texto, palabras, truncar

LOTE = 8
MAX_CHARS_DOC = 4000
Progreso = Callable[[int, int], None]


@dataclass
class Candidato:
    puesto: Puesto
    similitud: float  # 0 a 1 (coseno o, en el plan B, cobertura de palabras)


@dataclass
class ResultadoBusqueda:
    candidatos: list[Candidato]
    metodo: str  # "embeddings" | "palabras"
    avisos: list[str] = field(default_factory=list)


def consulta_desde_cv(cv, maximo: int) -> str:
    """Texto compacto del CV para buscar: objetivo, experiencia, formación y herramientas
    (sin datos de contacto ni relleno). Acepta un CVProcesado o un texto."""
    if isinstance(cv, str):
        return truncar(cv, maximo)[0]
    e = cv.estructura
    partes = [e.titulo_objetivo]
    for x in e.experiencias:
        partes += [f"{x.puesto} {x.organizacion}".strip(), *x.logros[:4]]
    partes += e.formacion
    if cv.herramientas:
        partes.append("Herramientas: " + ", ".join(cv.herramientas))
    texto = "\n".join(p for p in partes if p and p.strip())
    if len(texto) < 200:  # el modelo no estructuró casi nada: se usa el CV tal cual
        texto = cv.texto
    return truncar(texto, maximo)[0]


class Recuperador:
    def __init__(self, llm, cfg: Config, puestos: list[Puesto], indice_dir: Path | str = INDICE_DIR):
        self.llm, self.cfg, self.puestos = llm, cfg, puestos
        self.dir = Path(indice_dir)
        self._vectores: np.ndarray | None = None

    # ------------------------------------------------------------- índice
    @property
    def _huella_modelo(self) -> str:
        return f"{self.cfg.embeddings_provider}:{self.cfg.modelo_embeddings}"

    def _doc(self, p: Puesto) -> str:
        return truncar(p.texto_embedding, MAX_CHARS_DOC)[0]

    def _cargar(self) -> tuple[dict[str, np.ndarray], bool]:
        """Vectores guardados por id. El segundo valor dice si son del modelo actual."""
        try:
            meta = json.loads((self.dir / "meta.json").read_text(encoding="utf-8"))
            matriz = np.load(self.dir / "vectores.npy")
            ids, hashes = meta["ids"], meta["hashes"]
            if matriz.shape[0] != len(ids):
                raise ValueError("índice inconsistente")
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            return {}, False
        if meta.get("modelo") != self._huella_modelo:
            return {}, False
        return {i: (hashes[i], matriz[n]) for n, i in enumerate(ids)}, True  # type: ignore[return-value]

    def _guardar(self, ids: list[str], hashes: dict[str, str], matriz: np.ndarray) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", dir=self.dir, suffix=".tmp", delete=False) as f:
            np.save(f, matriz)
            tmp_npy = f.name
        os.replace(tmp_npy, self.dir / "vectores.npy")
        meta = {"modelo": self._huella_modelo, "ids": ids, "hashes": hashes}
        tmp_json = self.dir / "meta.json.tmp"
        tmp_json.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp_json, self.dir / "meta.json")

    def asegurar_indice(self, progreso: Progreso | None = None) -> int:
        """Deja el índice al día. Devuelve cuántos puestos hubo que vectorizar (0 si ya estaba listo)."""
        guardados, _ = self._cargar()
        docs = {p.id: self._doc(p) for p in self.puestos}
        hashes = {i: hash_texto(t) for i, t in docs.items()}
        pendientes = [p for p in self.puestos if guardados.get(p.id, (None,))[0] != hashes[p.id]]
        nuevos: dict[str, np.ndarray] = {}
        for ini in range(0, len(pendientes), LOTE):
            lote = pendientes[ini:ini + LOTE]
            vectores = self.llm.embeber([docs[p.id] for p in lote])
            for p, v in zip(lote, vectores):
                nuevos[p.id] = np.asarray(v, dtype=np.float32)
            if progreso:
                progreso(min(ini + LOTE, len(pendientes)), len(pendientes))
        if pendientes or self._vectores is None:
            filas = []
            for p in self.puestos:
                v = nuevos.get(p.id)
                filas.append(v if v is not None else guardados[p.id][1])
            matriz = np.vstack(filas).astype(np.float32)
            normas = np.linalg.norm(matriz, axis=1, keepdims=True)
            matriz = matriz / np.where(normas == 0, 1, normas)
            if pendientes:
                self._guardar([p.id for p in self.puestos], hashes, matriz)
            self._vectores = matriz
        return len(pendientes)

    # ------------------------------------------------------------- búsqueda
    def buscar(self, cv, k: int | None = None, filtro: Callable[[Puesto], bool] | None = None,
               progreso: Progreso | None = None) -> ResultadoBusqueda:
        k = k or self.cfg.recuperar_k
        consulta = consulta_desde_cv(cv, self.cfg.max_cv_chars_embedding)
        try:
            self.asegurar_indice(progreso)
            q = np.asarray(self.llm.embeber([consulta])[0], dtype=np.float32)
            norma = np.linalg.norm(q)
            sims = self._vectores @ (q / (norma if norma else 1))
            puntajes = [float(s) for s in sims]
            metodo, avisos = "embeddings", []
        except LLMError as e:
            puntajes = self._puntajes_palabras(consulta)
            metodo = "palabras"
            avisos = [f"No pude usar embeddings ({e}). Ordené los puestos por palabras en común, que es menos preciso."]
        ranking = sorted(zip(self.puestos, puntajes), key=lambda t: t[1], reverse=True)
        if filtro:
            ranking = [t for t in ranking if filtro(t[0])]
        return ResultadoBusqueda([Candidato(p, s) for p, s in ranking[:k]], metodo, avisos)

    def _puntajes_palabras(self, consulta: str) -> list[float]:
        """Plan B: cuánto de la consulta (ponderado por rareza de cada palabra) aparece en cada puesto."""
        docs = [set(palabras(p.texto_embedding, 4)) for p in self.puestos]
        df = Counter(w for d in docs for w in d)
        n = len(docs)
        q = set(palabras(consulta, 4))
        peso = {w: math.log((n + 1) / (df[w] + 0.5)) for w in q if w in df}
        total = sum(peso.values()) or 1.0
        return [sum(peso[w] for w in q & d if w in peso) / total for d in docs]
