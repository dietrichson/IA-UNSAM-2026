"""Evaluador: corre los casos de prueba y mide los criterios del documento de requisitos.

Uso (desde la carpeta del proyecto, con Ollama abierto):
    python -m evaluacion.evaluar                       # todo (puede tardar horas sin GPU)
    python -m evaluacion.evaluar --que recuperacion ranking --cvs cv-01-camila-rojas
    python -m evaluacion.evaluar --simulado            # prueba el evaluador sin modelo (no mide calidad real)

Para comparar proveedores, repetí la corrida cambiando LLM_PROVIDER en el .env: cada resultado
queda registrado con su proveedor, modelo y versión de prompts.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from evaluacion import metricas as M  # noqa: E402
from servicios.adaptador import adaptar_cv, analizar_palabras, redactar_carta  # noqa: E402
from servicios.brechas import brechas_de_puesto  # noqa: E402
from servicios.config import Config, cargar_config  # noqa: E402
from servicios.cv_parser import ErrorArchivo, parsear_cv  # noqa: E402
from servicios.llm_client import LLMClient, LLMError  # noqa: E402
from servicios.oferta_parser import parsear_oferta  # noqa: E402
from servicios.puestos_repo import cargar_puestos  # noqa: E402
from servicios.sugeridor import sugerir  # noqa: E402
from servicios.vocabulario import vocabulario_desde_puestos  # noqa: E402

CASOS = Path(__file__).resolve().parent / "casos"
RESULTADOS = Path(__file__).resolve().parent / "resultados"
PARTES = ("recuperacion", "ranking", "palabras", "veracidad", "brechas")


def cargar_casos() -> tuple[dict[str, str], dict[str, str], dict]:
    cvs = {p.stem: p.read_text(encoding="utf-8") for p in sorted((CASOS / "cvs").glob("*.md"))}
    ofertas = {p.stem: p.read_text(encoding="utf-8") for p in sorted((CASOS / "ofertas").glob("*.md"))}
    esperados = json.loads((CASOS / "esperados.json").read_text(encoding="utf-8")).get("cvs", {})
    return cvs, ofertas, esperados


def evaluar(llm, cfg: Config, puestos, que: set[str], cvs_ids: list[str] | None = None, ofertas_ids: list[str] | None = None,
            n: int | None = None, con_carta: bool = False, indice_dir: Path | None = None, log=print) -> dict:
    cvs, ofertas, esperados = cargar_casos()
    cvs = {k: v for k, v in cvs.items() if not cvs_ids or k in cvs_ids}
    ofertas = {k: v for k, v in ofertas.items() if not ofertas_ids or k in ofertas_ids}
    vocab = vocabulario_desde_puestos(puestos)
    res: dict = {"recuperacion": [], "ranking": [], "palabras": [], "veracidad": [], "brechas": [], "errores": []}
    t0 = time.monotonic()
    necesita_puestos = bool(que & {"recuperacion", "ranking", "brechas"})
    necesita_ofertas = bool(que & {"palabras", "veracidad"})

    ofertas_ok = {}
    if necesita_ofertas:
        for oid, texto in ofertas.items():
            try:
                log(f"Leyendo oferta {oid}")
                ofertas_ok[oid] = parsear_oferta(texto, llm, vocab)
            except (LLMError, ErrorArchivo) as e:
                res["errores"].append({"caso": oid, "paso": "oferta", "error": str(e)})

    for cid, texto_cv in cvs.items():
        esp = esperados.get(cid, {})
        try:
            log(f"[{cid}] leyendo CV")
            cv = parsear_cv(texto_cv, llm, cfg, vocab)
        except (LLMError, ErrorArchivo) as e:
            res["errores"].append({"caso": cid, "paso": "cv", "error": str(e)})
            continue

        if necesita_puestos:
            try:
                log(f"[{cid}] recuperando y puntuando")
                sug = sugerir(cv, llm, cfg, puestos, n=n, cache=None, indice_dir=indice_dir)
                recuperados = [c.puesto.id for c in sug.busqueda.candidatos[: cfg.recuperar_k]]
                top3 = [r.puesto.id for r in sug.resultados][:3]
                elegidos = esp.get("puestos_esperados") or []
                res["recuperacion"].append({"cv": cid, "metodo": sug.busqueda.metodo, "recuperados": recuperados,
                                            "esperados": elegidos, "alguno": M.acierta_alguno(elegidos, recuperados),
                                            "todos": M.acierta_todos(elegidos, recuperados)})
                res["ranking"].append({"cv": cid, "top3": top3, "puntajes": [r.puntaje for r in sug.resultados][:3],
                                       "esperados": elegidos, "acierta": M.acierta_alguno(elegidos, top3)})
                for r in sug.resultados:
                    for b in brechas_de_puesto(r, puestos):
                        res["brechas"].append({"cv": cid, "puesto": r.puesto.id, "titulo": r.puesto.titulo,
                                               "brecha": b.texto, "tipo": b.tipo})
            except LLMError as e:
                res["errores"].append({"caso": cid, "paso": "sugeridor", "error": str(e)})

        for oid, oferta in ofertas_ok.items():
            try:
                log(f"[{cid} x {oid}] palabras clave")
                analisis = analizar_palabras(cv, oferta, llm)
                esperado = (esp.get("faltantes") or {}).get(oid)
                res["palabras"].append({"cv": cid, "oferta": oid, "faltantes": analisis.faltantes,
                                        "esperado": esperado, "comparacion": M.comparar_faltantes(esperado, analisis.faltantes)})
                if "veracidad" in que:
                    generados = [("cv", lambda: adaptar_cv(cv, oferta, analisis, llm, cfg, vocab))]
                    if con_carta:
                        generados.append(("carta", lambda: redactar_carta(cv, oferta, analisis, llm, cfg, "cercano", vocab)))
                    for tipo, f in generados:
                        log(f"[{cid} x {oid}] generando {tipo}")
                        g = f()
                        res["veracidad"].append({
                            "cv": cid, "oferta": oid, "tipo": tipo, "regenerado": g.regenerado,
                            "hallazgos": [{"tipo": h.tipo, "fragmento": h.fragmento, "motivo": h.motivo} for h in g.hallazgos],
                            "ok": not g.hallazgos, "texto": g.texto})
            except LLMError as e:
                res["errores"].append({"caso": f"{cid} x {oid}", "paso": "oferta/generación", "error": str(e)})

    res["resumen"] = {
        "recuperacion_alguno": M.tasa([r["alguno"] for r in res["recuperacion"]]),
        "recuperacion_todos": M.tasa([r["todos"] for r in res["recuperacion"]]),
        "ranking": M.tasa([r["acierta"] for r in res["ranking"]]),
        "palabras": M.tasa([None if r["comparacion"] is None else r["comparacion"]["coincide"] for r in res["palabras"]]),
        "veracidad": M.tasa([r["ok"] for r in res["veracidad"]]),
        "veracidad_regeneradas": sum(r["regenerado"] for r in res["veracidad"]),
    }
    res["meta"] = {"fecha": datetime.now().isoformat(timespec="seconds"), "provider": cfg.provider,
                   "modelo_principal": cfg.modelo_principal, "modelo_embeddings": cfg.modelo_embeddings,
                   "prompts": M.version_prompts(), "partes": sorted(que), "cvs": list(cvs), "ofertas": list(ofertas),
                   "puestos_puntuados": n or cfg.puntuar_n, "con_carta": con_carta,
                   "segundos_totales": round(time.monotonic() - t0, 1), "llm": llm.resumen_metricas()}
    return res


def _muestra(items: list, k: int) -> list:
    if len(items) <= k:
        return items
    paso = len(items) / k
    return [items[int(i * paso)] for i in range(k)]


def informe_md(res: dict) -> str:
    m, r = res["meta"], res["resumen"]
    filas = [
        ("Veracidad (salidas sin datos sin respaldo)", r["veracidad"], "veracidad"),
        ("Palabras clave faltantes (coincidencia con la lista a mano)", r["palabras"], "palabras"),
        ("Ranking (alguno de los 3 primeros coincide)", r["ranking"], "ranking"),
        ("Recuperación (alguno de los esperados entre los 10)", r["recuperacion_alguno"], "recuperacion"),
    ]
    l = ["# Informe de evaluación", ""]
    if m.get("simulado"):
        l += ["> **CORRIDA SIMULADA:** se usó un modelo falso solo para probar el evaluador. Estos números no miden ningún modelo real.", ""]
    l += [
         f"- Fecha: {m['fecha']}", f"- Proveedor y modelo: {m['provider']} / {m['modelo_principal']} (embeddings: {m['modelo_embeddings']})",
         f"- Versión de prompts: `{m['prompts']}`", f"- CV: {len(m['cvs'])} · Ofertas: {len(m['ofertas'])} · Puestos puntuados por CV: {m['puestos_puntuados']}",
         f"- Tiempo total: {m['segundos_totales']} s · Llamadas al modelo: {m['llm']['llamadas']}", "",
         "| Criterio | Casos | Aciertos | Resultado | Umbral | Estado |", "|---|---|---|---|---|---|"]
    for nombre, t, clave in filas:
        pct = "—" if t["porcentaje"] is None else f"{t['porcentaje']} %"
        l.append(f"| {nombre} | {t['casos']} | {t['aciertos']} | {pct} | {M.UMBRALES[clave]:g} % | {M.estado(clave, t)} |")
    l += ["| Brechas (revisión manual de 15 casos) | — | — | — | 80 % | Pendiente: completar `revision-brechas.csv` |", "",
          f"Salidas regeneradas por el verificador: {r['veracidad_regeneradas']}.",
          "La revisión manual de veracidad (10 casos) está en `revision-veracidad.md`.", ""]
    if res["errores"]:
        l += ["## Errores durante la corrida", ""] + [f"- {e['caso']} ({e['paso']}): {e['error']}" for e in res["errores"]]
    return "\n".join(l) + "\n"


def escribir(res: dict, carpeta: Path = RESULTADOS) -> list[Path]:
    carpeta.mkdir(parents=True, exist_ok=True)
    m = res["meta"]
    modelo = re.sub(r"[^a-z0-9.]+", "-", m["modelo_principal"].lower())
    marca = "simulado-" if m.get("simulado") else ""
    base = carpeta / f"{marca}{datetime.now():%Y%m%d-%H%M%S}-{m['provider']}-{modelo}-p{m['prompts']}"
    archivos = []
    p = Path(f"{base}.json")
    p.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    archivos.append(p)
    p = Path(f"{base}.md")
    p.write_text(informe_md(res), encoding="utf-8")
    archivos.append(p)
    if res["brechas"]:
        p = Path(f"{base}-revision-brechas.csv")
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["cv", "puesto", "brecha", "tipo", "correcta (si/no)"])
            for b in _muestra(res["brechas"], 15):
                w.writerow([b["cv"], b["titulo"], b["brecha"], b["tipo"], ""])
        archivos.append(p)
    if res["veracidad"]:
        p = Path(f"{base}-revision-veracidad.md")
        bloques = ["# Revisión manual de veracidad", "",
                   "Para cada caso, compará el texto generado con el CV original (en `evaluacion/casos/cvs/`) y anotá si "
                   "contiene algún dato inventado.", ""]
        for i, v in enumerate(_muestra(res["veracidad"], 10), 1):
            bloques += [f"## Caso {i}: {v['cv']} × {v['oferta']} ({v['tipo']})", "",
                        f"Marcas del verificador: {', '.join(h['fragmento'] for h in v['hallazgos']) or 'ninguna'}", "",
                        "Resultado de la revisión: [ ] sin datos inventados  [ ] con datos inventados — cuáles: ", "",
                        "```", v["texto"], "```", ""]
        p.write_text("\n".join(bloques), encoding="utf-8")
        archivos.append(p)
    return archivos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--que", nargs="+", choices=[*PARTES, "todo"], default=["todo"])
    ap.add_argument("--cvs", nargs="+", help="ids de CV (nombre del archivo sin .md)")
    ap.add_argument("--ofertas", nargs="+", help="ids de oferta")
    ap.add_argument("--n", type=int, help="puestos a puntuar por CV (por defecto el de la configuración)")
    ap.add_argument("--con-carta", action="store_true", help="en veracidad, evaluar también la carta (el doble de tiempo)")
    ap.add_argument("--simulado", action="store_true", help="usar un modelo simulado (solo prueba el evaluador)")
    ap.add_argument("--salida", type=Path, default=RESULTADOS)
    a = ap.parse_args(argv)
    que = set(PARTES) if "todo" in a.que else set(a.que)

    cfg = cargar_config()
    puestos = cargar_puestos()
    tmp = None
    if a.simulado:
        from evaluacion.simulado import LLMSimulado
        llm, tmp = LLMSimulado(), tempfile.TemporaryDirectory()
        indice = Path(tmp.name)
        print("MODO SIMULADO: los resultados no dicen nada sobre la calidad de un modelo real.")
    else:
        llm, indice = LLMClient(cfg), None
        ok, msg = llm.estado()
        if not ok:
            print(msg)
            return 1
    cvs, ofertas, _ = cargar_casos()
    ncv = len([c for c in cvs if not a.cvs or c in a.cvs])
    nof = len([o for o in ofertas if not a.ofertas or o in a.ofertas])
    llamadas = ncv * ((1 + (a.n or cfg.puntuar_n)) if que & {"recuperacion", "ranking", "brechas"} else 1)
    if que & {"palabras", "veracidad"}:
        llamadas += nof + ncv * nof * (1 + (("veracidad" in que) * (2 if a.con_carta else 1) * 2))
    print(f"Llamadas al modelo estimadas: unas {llamadas}. Con qwen2.5:3b sin GPU cada una puede tardar de 1 a 3 minutos.")
    res = evaluar(llm, cfg, puestos, que, a.cvs, a.ofertas, a.n, a.con_carta, indice)
    res["meta"]["simulado"] = a.simulado
    for p in escribir(res, a.salida):
        print("Escrito:", p)
    if tmp:
        tmp.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
