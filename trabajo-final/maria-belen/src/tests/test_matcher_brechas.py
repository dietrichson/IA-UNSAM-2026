import pytest

from servicios.brechas import (brechas_de_puesto, clave_herramienta, frecuencias_herramientas,
                               herramientas_mas_pedidas, resumen_agregado, sugerencia)
from servicios.config import EJEMPLOS_DIR, cargar_config
from servicios.cv_parser import parsear_cv
from servicios.llm_client import SalidaInvalida
from servicios.matcher import (CachePuntajes, EvaluacionLLM, evaluar_herramientas, puntuar_candidatos,
                               puntuar_puesto)
from servicios.puestos_repo import Puesto, cargar_puestos
from servicios.recuperador import Candidato
from servicios.schemas import CVEstructurado, Criterio
from tests.falsos import LLMFalso

CFG = cargar_config({})
PUESTOS = cargar_puestos()
CV = parsear_cv((EJEMPLOS_DIR / "cv-ejemplo-junior.md").read_text(encoding="utf-8"), LLMFalso(CVEstructurado()), CFG)

CUERPO = "# Diseñador/a\n\n## Requisitos\n- Manejo de Photoshop y Canva\n- Experiencia en redes sociales\n- Portfolio de trabajos\n"


def puesto(**kw):
    base = dict(id="p1", titulo="Diseñador/a", cuerpo=CUERPO, herramientas=["Canva", "Photoshop"],
                titulo_universitario="Estudiante avanzado o graduado de Comunicación", requiere_titulo="sí", seniority="junior",
                experiencia="Mínimo 1 año en redes sociales", idiomas=["Inglés intermedio"])
    base.update(kw)
    return Puesto(**base)


def evaluacion(**kw):
    base = dict(
        experiencia=Criterio(puntaje=80, evidencia=["Diseño de piezas gráficas en Canva"], comentario="ok"),
        formacion=Criterio(puntaje=100, evidencia=["Licenciatura en Ciencias de la Comunicación"], comentario="ok"),
                brechas=["Portfolio de trabajos", "Dominio de Blender"], resumen="Buen ajuste.")
    base.update(kw)
    return EvaluacionLLM(**base)


def test_puntaje_combinado_con_pesos_y_tope_sin_cita():
    r = puntuar_puesto(CV, puesto(), LLMFalso(evaluacion()), CFG)
    por = {i.clave: i for i in r.items}
    assert por["herramientas"].puntaje == 50 and por["otros"].puntaje == 100
    assert "seniority" not in por  # Seniority ya no es un criterio: lo cubre Experiencia
    assert por["experiencia"].evidencia == ["Diseño de piezas gráficas en Canva"]
    # (0,30*50 + 0,35*80 + 0,15*100 + 0,10*100) / 0,90 = 75,6
    assert r.puntaje == 76 and not r.parcial
    assert r.herramientas_cubiertas == ["Canva"] and r.herramientas_faltantes == ["Photoshop"]
    assert r.brechas_modelo == ["Portfolio de trabajos"]  # "Blender" no está en el puesto: inventado
    assert sum(i.peso for i in r.items) == pytest.approx(1)


def test_cita_inventada_limita_el_puntaje():
    ev = evaluacion(experiencia=Criterio(puntaje=95, evidencia=["Dirigió la campaña del Mundial 2022"]))
    p = puesto(cuerpo="# Analista\n- Planillas de cálculo y reportes", titulo="Analista")
    r = puntuar_puesto(CV, p, LLMFalso(ev), CFG)
    assert r.item("experiencia").puntaje == 40 and r.item("experiencia").evidencia == []


def test_criterios_que_el_puesto_no_especifica_se_excluyen_y_el_peso_se_reparte():
    p = puesto(herramientas=[], titulo_universitario="no figura", requiere_titulo="no figura", seniority="no figura",
               idiomas=[], experiencia="Experiencia previa en redes sociales")
    r = puntuar_puesto(CV, p, LLMFalso(evaluacion()), CFG)
    assert [i.clave for i in r.items] == ["experiencia"]
    assert r.puntaje == 80 and sum(i.peso for i in r.items) == pytest.approx(1)


def test_herramientas_genericas_y_alternativas():
    cv_norm = "uso canva y ga4"
    p, cub, falt = evaluar_herramientas(puesto(herramientas=["Google Analytics 4 (GA4)", "Photoshop o Illustrator",
                                                             "Herramientas de diseño"]), cv_norm)
    assert (p, cub, falt) == (50, ["Google Analytics 4 (GA4)"], ["Photoshop o Illustrator"])
    assert evaluar_herramientas(puesto(herramientas=["No figuran en el aviso leído"]), cv_norm)[0] is None


def test_si_el_modelo_falla_el_puntaje_es_parcial_y_no_se_cachea(tmp_path):
    cache = CachePuntajes(tmp_path / "c.json")
    r = puntuar_puesto(CV, puesto(), LLMFalso(error=SalidaInvalida("x")), CFG, cache)
    assert r.parcial and r.avisos and r.item("experiencia").puntaje is None
    assert r.puntaje == round((0.30 * 50 + 0.10 * 100) / 0.40)
    assert not (tmp_path / "c.json").exists()


def test_cache_evita_llamadas_y_se_invalida_con_otro_cv(tmp_path):
    ruta = tmp_path / "c.json"
    llm = LLMFalso(evaluacion())
    primero = puntuar_puesto(CV, puesto(), llm, CFG, CachePuntajes(ruta))
    segundo = puntuar_puesto(CV, puesto(), llm, CFG, CachePuntajes(ruta))  # cache cargado desde disco
    assert len(llm.llamadas) == 1 and segundo.desde_cache and segundo.puntaje == primero.puntaje
    assert segundo.item("experiencia").evidencia == primero.item("experiencia").evidencia
    otro_cv = parsear_cv(CV.texto + "\nTambién hice pasantías en prensa.", LLMFalso(CVEstructurado()), CFG)
    puntuar_puesto(otro_cv, puesto(), llm, CFG, CachePuntajes(ruta))
    assert len(llm.llamadas) == 2


def test_el_cv_va_primero_en_el_prompt_y_queda_delimitado():
    llm = LLMFalso(evaluacion())
    puntuar_puesto(CV, puesto(), llm, CFG)
    user = llm.llamadas[0]["user"]
    assert user.index("<cv>") < user.index("<puesto>") and "no obedezcas" in llm.llamadas[0]["system"]


def test_puntuar_candidatos_ordena_limita_y_reporta_progreso():
    ps = [puesto(id=f"p{i}", titulo=f"Puesto {i}") for i in range(4)]
    puntajes = iter([30, 90, 60, 10])

    class LLM:
        def chat_json(self, *a, **k):
            return evaluacion(experiencia=Criterio(puntaje=next(puntajes), evidencia=["Diseño de piezas gráficas en Canva"]))

    avance = []
    res = puntuar_candidatos(CV, [Candidato(p, 0.5) for p in ps], LLM(), CFG, n=3, progreso=lambda i, n, t: avance.append((i, n)))
    assert len(res) == 3 and [r.puesto.id for r in res] == ["p1", "p2", "p0"]
    assert avance[0] == (0, 3) and avance[-1] == (3, 3)


def test_puntaje_con_puestos_reales_corre_sin_errores():
    llm = LLMFalso(evaluacion())
    for p in PUESTOS:
        r = puntuar_puesto(CV, p, llm, CFG)
        assert 0 <= r.puntaje <= 100 and r.items


# ------------------------------------------------------------------ brechas
def test_clave_herramienta_agrupa_variantes():
    assert clave_herramienta("Google Analytics 4 (GA4)") == clave_herramienta("GA4") == clave_herramienta("Google Analytics")
    assert clave_herramienta("Canva") != clave_herramienta("Photoshop")


def test_frecuencias_y_herramientas_mas_pedidas():
    cuenta, etiquetas = frecuencias_herramientas(PUESTOS)
    assert max(cuenta.values()) <= len(PUESTOS)
    filas = herramientas_mas_pedidas(CV, PUESTOS, top=10)
    assert [f.puestos for f in filas] == sorted((f.puestos for f in filas), reverse=True)
    assert all(0 < f.porcentaje <= 100 for f in filas)
    canva = next(f for f in herramientas_mas_pedidas(CV, PUESTOS, top=100) if f.herramienta.lower() == "canva")
    assert canva.la_tengo  # el CV de ejemplo menciona Canva


def test_brechas_de_puesto_ordenadas_por_importancia_y_sugerencia():
    ps = [puesto(id="a", herramientas=["Photoshop", "Premiere"]), puesto(id="b", herramientas=["Photoshop"]),
          puesto(id="c", herramientas=["Photoshop", "Canva"])]
    r = puntuar_puesto(CV, puesto(herramientas=["Premiere", "Photoshop"]), LLMFalso(evaluacion()), CFG)
    br = brechas_de_puesto(r, ps)
    assert [b.texto for b in br][:2] == ["Photoshop", "Premiere"] and br[0].frecuencia == 3
    assert br[-1].tipo == "requisito"
    assert "Photoshop" in sugerencia(br, 3) and "3 de los 3" in sugerencia(br, 3)
    assert "No detecté" in sugerencia([], 3)


def test_resumen_agregado_cuenta_repeticiones():
    ev = evaluacion(formacion=Criterio(puntaje=20, evidencia=[]))
    rs = [puntuar_puesto(CV, puesto(id=f"p{i}", titulo_universitario="Licenciatura en Contabilidad"), LLMFalso(ev), CFG)
          for i in range(3)]
    filas = resumen_agregado(rs)
    por = {(f.texto, f.tipo): f for f in filas}
    assert por[("Photoshop", "herramienta")].veces == 3 and por[("Photoshop", "herramienta")].de == 3
    assert por[("Formación por debajo de 50", "criterio")].veces == 3


# ---------- Bloque 1: la experiencia no penaliza si el puesto no la exige
from servicios.puestos_repo import exigencia_experiencia, puesto_desde_oferta  # noqa: E402
from servicios.schemas import OfertaEstructurada  # noqa: E402


@pytest.mark.parametrize("exp,esperado", [
    ("no figura", "no"), ("No se requiere experiencia", "no"), ("0 a 2 años", "no"),
    ("No exige años; suma tener experiencia en SEO", "deseable"), ("Mínimo 2 años en posiciones similares", "si"),
    ("Experiencia comprobable en prensa", "si"),
    ("Al menos 5 años (deseable); agenda propia (excluyente)", "si"), ("Se valora experiencia en agencias", "deseable"),
])
def test_exigencia_de_experiencia(exp, esperado):
    assert exigencia_experiencia(puesto(experiencia=exp, seniority="no figura")) == esperado


def test_oferta_pegada_sin_experiencia_o_que_la_niega():
    est = OfertaEstructurada(titulo="Asistente")
    p = puesto_desde_oferta("Buscamos asistente de redes. Requisitos: Canva.", est)
    assert exigencia_experiencia(p) == "no"
    p = puesto_desde_oferta("Buscamos asistente. No se requiere experiencia. Canva.", est)
    assert exigencia_experiencia(p) == "no"
    p = puesto_desde_oferta("Buscamos asistente. Se requieren 2 años de experiencia previa.", est)
    assert exigencia_experiencia(p) == "si"


def test_sin_exigencia_la_experiencia_no_suma_ni_resta_ni_aparece_en_brechas_ni_resumen():
    ev = evaluacion(experiencia=Criterio(puntaje=0, comentario="no tiene"), seniority=Criterio(puntaje=0),
                    brechas=["Portfolio de trabajos", "Experiencia en redes sociales"],
                    resumen="El CV no muestra experiencia relevante. Buen manejo de Canva.")
    r = puntuar_puesto(CV, puesto(experiencia="No se requiere experiencia", seniority="no figura"), LLMFalso(ev), CFG)
    exp = r.item("experiencia")
    assert exp.puntaje is None and exp.peso == 0 and "no exige experiencia" in exp.comentario
    assert r.item("seniority") is None and not r.parcial  # Seniority ya no existe
    assert r.brechas_modelo == ["Portfolio de trabajos"]
    assert "experiencia" not in r.resumen.lower() and "Canva" in r.resumen
    # el puntaje se reparte entre los demás criterios (experiencia = 0 no lo arrastra)
    assert r.puntaje >= 60


def test_nota_de_exigencia_llega_al_modelo():
    llm = LLMFalso(evaluacion())
    puntuar_puesto(CV, puesto(experiencia="no figura", seniority="no figura"), llm, CFG)
    assert "Exigencia de experiencia: NO" in llm.llamadas[0]["user"]


def test_dominio_meta_ads_cuenta_como_publicidad_digital():
    from servicios.vocabulario import dominios_en_texto
    assert "publicidad digital" in dominios_en_texto("Campañas pagas en Meta Ads con presupuestos de hasta USD 3.000")
    assert "marketing digital" in dominios_en_texto("Gestión de Google Ads")
    cv = type("CV", (), {"texto": "Analista de contenidos. Campañas pagas en Meta Ads con presupuesto de USD 3.000 por mes.",
                         "idiomas": []})()
    p = puesto(cuerpo="# Publicista\n- Experiencia en publicidad digital", herramientas=[], idiomas=[],
               titulo_universitario="no figura", requiere_titulo="no figura", seniority="no figura",
               experiencia="2 años en publicidad digital")
    ev = evaluacion(experiencia=Criterio(puntaje=10, evidencia=[]))
    llm = LLMFalso(ev)
    r = puntuar_puesto(cv, p, llm, CFG)
    assert r.item("experiencia").puntaje == 50 and "publicidad digital" in r.item("experiencia").comentario
    assert "Pista: el CV menciona" in llm.llamadas[0]["user"]


# ---------- Bloque 8: excluyentes (por defecto) vs deseables (solo si el texto lo dice)
from servicios.brechas import brechas_de_puesto, sugerencia  # noqa: E402
from servicios.oferta_parser import clasificar_requisitos  # noqa: E402
from servicios.puestos_repo import es_deseable, lineas_con_tipo  # noqa: E402


def test_por_defecto_todo_es_excluyente_y_solo_marcas_explicitas_son_deseables():
    assert not es_deseable("Manejo de Canva")
    assert not es_deseable("2 años de experiencia, idealmente en consumo masivo")  # matiz, no opcional
    assert es_deseable("Inglés avanzado (deseable)") and es_deseable("Se valora Meta Ads")
    assert es_deseable("Photoshop, no excluyente") and es_deseable("Suma: experiencia en agencias")
    assert not es_deseable("Photoshop (excluyente)")
    pares = dict(lineas_con_tipo("- Dominio de Premiere; suma After Effects\nDeseable:\n- Meta Ads\n- Excel"))
    assert pares["Dominio de Premiere"] is False and pares["suma After Effects"] is True
    assert pares["Meta Ads"] is True and pares["Excel"] is True


def test_clasificar_requisitos_manda_el_aviso_sobre_el_modelo():
    texto = "Requisitos:\n- Manejo de Canva\n- Redacción de notas\nSe valora:\n- Meta Ads\n- Inglés intermedio"
    exc, des = clasificar_requisitos(texto, ["Manejo de Canva", "Meta Ads"], ["Redacción de notas", "Inglés intermedio"])
    assert exc == ["Manejo de Canva", "Redacción de notas"] and des == ["Meta Ads", "Inglés intermedio"]
    # sin poder ubicarlo en el aviso, queda donde lo puso el modelo
    assert clasificar_requisitos("texto sin nada", ["Algo raro"], ["Otro"]) == (["Algo raro"], ["Otro"])


CUERPO_DES = ("# Diseñador/a\n\n## Requisitos\n- Manejo de Canva\n- Se valora Photoshop\n- Inglés intermedio (deseable)\n")


def test_herramienta_deseable_no_resta_y_suma_plus():
    cv_con = type("CV", (), {"texto": "Uso Canva y Photoshop todos los días. Inglés intermedio.", "idiomas": ["Inglés intermedio"]})()
    cv_sin = type("CV", (), {"texto": "Uso Canva todos los días.", "idiomas": []})()
    p = puesto(cuerpo=CUERPO_DES, idiomas=["Inglés intermedio (deseable)"], experiencia="no figura", seniority="no figura",
               titulo_universitario="no figura", requiere_titulo="no figura")
    assert evaluar_herramientas(p, "uso canva") == (100, ["Canva"], [])  # Photoshop es deseable: no cuenta
    ev = evaluacion(formacion=Criterio(puntaje=50, evidencia=[]), brechas=[])
    p.titulo_universitario = "Licenciatura en Comunicación"
    sin = puntuar_puesto(cv_sin, p, LLMFalso(ev), CFG)
    con = puntuar_puesto(cv_con, p, LLMFalso(ev), CFG)
    assert sin.item("herramientas").puntaje == 100 and sin.item("otros") is None  # idioma solo deseable: no puntúa
    assert sin.bonus == 0 and sin.deseables_faltantes == ["Photoshop", "Inglés (idioma)"]
    assert con.plus == ["Photoshop", "Inglés (idioma)"] and con.bonus == 6 and con.puntaje == sin.puntaje + 6
    # las faltantes deseables no son brechas obligatorias ni "por dónde empezar"
    br = brechas_de_puesto(sin, [p])
    assert [b.tipo for b in br if b.tipo == "herramienta"] == []
    assert {b.texto for b in br if b.tipo == "deseable"} == {"Photoshop", "Inglés (idioma)"}
    assert sugerencia([b for b in br if b.tipo == "deseable"], 1).startswith("No detecté brechas obligatorias")


def test_bonus_con_tope_y_sin_pasar_de_100():
    p = puesto(cuerpo="# X\n\n## Requisitos\n- Canva\n- Se valora Photoshop, Premiere, Illustrator, After Effects, Excel",
               herramientas=["Canva", "Photoshop", "Premiere", "Illustrator", "After Effects", "Excel"], idiomas=[],
               experiencia="no figura", seniority="no figura", titulo_universitario="no figura", requiere_titulo="no figura")
    cv = type("CV", (), {"texto": "Canva Photoshop Premiere Illustrator After Effects Excel", "idiomas": []})()
    r = puntuar_puesto(cv, p, LLMFalso(evaluacion(brechas=[])), CFG)
    assert len(r.plus) == 5 and r.bonus == 10 or r.puntaje == 100


def test_brecha_del_modelo_deseable_se_separa():
    p = puesto(cuerpo="# X\n\n## Requisitos\n- Portfolio de trabajos\n- Se valora Dominio de motion graphics\n",
               experiencia="no figura", seniority="no figura")
    ev = evaluacion(brechas=["Portfolio de trabajos", "Dominio de motion graphics"])
    r = puntuar_puesto(CV, p, LLMFalso(ev), CFG)
    assert r.brechas_modelo == ["Portfolio de trabajos"] and "Dominio de motion graphics" in r.deseables_faltantes


def test_formacion_y_experiencia_deseables_no_restan_pero_suman():
    p = puesto(requiere_titulo="deseable", titulo_universitario="Estudiante de Comunicación (deseable)",
               experiencia="Se valora experiencia en redes", seniority="no figura", herramientas=[], idiomas=[])
    r = puntuar_puesto(CV, p, LLMFalso(evaluacion()), CFG)
    assert r.item("formacion").puntaje is None and r.item("experiencia").puntaje is None
    assert set(r.plus) == {"Formación", "Experiencia"} and r.bonus >= 0
    malo = evaluacion(formacion=Criterio(puntaje=0), experiencia=Criterio(puntaje=0))
    r2 = puntuar_puesto(_cv("Contador Público, UBA 2019. Excel.", []), p, LLMFalso(malo), CFG)
    assert r2.plus == [] and set(r2.deseables_faltantes) >= {"Formación", "Experiencia"}


# ---------- Bloque 2: brechas coherentes y niveles de idioma
from servicios.matcher import brechas_de_idioma, evaluar_idiomas  # noqa: E402
from servicios.vocabulario import nivel_idioma  # noqa: E402


@pytest.mark.parametrize("texto,idioma,req,esperado", [
    ("Inglés avanzado (C1); Portugués básico", "Inglés", False, 3.0),
    ("Inglés avanzado (C1); Portugués básico", "Portugués", False, 1.0),
    ("Inglés intermedio", "Inglés", True, 2.0), ("Inglés avanzado o bilingüe", "Inglés", True, 3.0),
    ("Inglés", "Inglés", False, None), ("Español nativo, inglés avanzado", "Inglés", False, 3.0),
])
def test_nivel_de_idioma(texto, idioma, req, esperado):
    assert nivel_idioma(texto, idioma, req) == esperado


def _cv(texto, idiomas):
    return type("CV", (), {"texto": texto, "idiomas": idiomas})()


def test_ingles_avanzado_cubre_intermedio_sin_brecha():
    p = puesto(idiomas=["Inglés intermedio"])
    cv = _cv("Idiomas: Inglés avanzado", ["Inglés avanzado"])
    assert evaluar_idiomas(p, cv)[0] == 100 and brechas_de_idioma(p, cv) == []


def test_idioma_por_debajo_o_ausente_es_brecha_y_sin_nivel_no_lo_es():
    p = puesto(idiomas=["Inglés avanzado"])
    assert brechas_de_idioma(p, _cv("Inglés básico", ["Inglés básico"])) == ["Inglés avanzado (tu CV muestra nivel básico)"]
    assert evaluar_idiomas(p, _cv("Inglés básico", ["Inglés básico"]))[0] == 50
    assert brechas_de_idioma(p, _cv("Sin idiomas", [])) == ["Inglés avanzado"]
    assert brechas_de_idioma(p, _cv("Inglés", ["Inglés"])) == []  # nivel no declarado: no se inventa una brecha


def test_brecha_del_modelo_sobre_idioma_o_herramienta_cubierta_se_descarta():
    cv = _cv("Estudiante avanzada de Licenciatura en Comunicación\nDiseño en Canva y Meta Business Suite todos los días. Inglés avanzado.", ["Inglés avanzado"])
    cv.estructura = None
    p = puesto(herramientas=["Canva", "Meta Business Suite"], idiomas=["Inglés intermedio"],
               cuerpo="# X\n\n## Requisitos\n- Conocimientos en Canva, Meta Business Suite\n- Inglés intermedio\n- Portfolio de trabajos\n",
               experiencia="no figura", seniority="no figura")
    ev = evaluacion(brechas=["Conocimientos en Canva, Meta Business Suite", "Inglés intermedio", "Portfolio de trabajos"])
    r = puntuar_puesto(cv, p, LLMFalso(ev), CFG)
    assert r.item("herramientas").puntaje == 100
    assert r.brechas_modelo == ["Portfolio de trabajos"] and r.brechas_idioma == []
    textos = [b.texto for b in brechas_de_puesto(r, [p])]
    assert not any("Canva" in t or "Meta" in t or "Inglés" in t for t in textos)
    assert "Canva" not in sugerencia(brechas_de_puesto(r, [p]), 1)


def test_defensa_en_brechas_de_puesto_con_resultado_viejo():
    cv = _cv("Canva", [])
    p = puesto(herramientas=["Canva"], idiomas=[], experiencia="no figura", seniority="no figura")
    r = puntuar_puesto(cv, p, LLMFalso(evaluacion(brechas=[])), CFG)
    r.brechas_modelo = ["Conocimientos en Canva"]  # como si viniera de un caché anterior
    assert [b for b in brechas_de_puesto(r, [p]) if b.tipo == "requisito"] == []


# ---------- Bloque 3: herramientas duplicadas y sinónimos
from servicios.vocabulario import (alternativas, etiqueta_herramienta, herramienta_cubierta,  # noqa: E402
                                   herramientas_unicas)


def test_y_o_y_prefijos_en_alternativas():
    assert alternativas("Diseño en Canva y/o Adobe") == ["canva", "adobe"]
    assert alternativas("Manejo de Excel") == ["excel"]
    assert etiqueta_herramienta("Diseño en Canva y/o Adobe") == "Canva y/o Adobe"
    assert etiqueta_herramienta("Canva") == "Canva"


def test_herramientas_unicas_quita_repetidas_y_contenidas():
    assert herramientas_unicas(["Canva", "Diseño en Canva y/o Adobe", "Adobe", "Adobe Creative Suite"]) == ["Canva", "Adobe"]
    assert herramientas_unicas(["Google Analytics 4 (GA4)", "GA4"]) == ["GA4"]
    assert herramientas_unicas(["Premiere", "Adobe Premiere Pro"]) == ["Premiere"]
    assert herramientas_unicas(["Photoshop", "Illustrator"]) == ["Photoshop", "Illustrator"]  # distintas: se conservan


def test_adobe_se_cubre_con_cualquier_programa_de_la_familia_pero_no_al_reves():
    assert herramienta_cubierta("Adobe Creative Suite", "uso photoshop y premiere")
    assert herramienta_cubierta("Diseño en Canva y/o Adobe", "uso illustrator")
    assert not herramienta_cubierta("Photoshop", "uso adobe")


def test_requisitos_duplicados_no_inflan_ni_distorsionan_el_puntaje():
    p = puesto(herramientas=["Canva", "Diseño en Canva y/o Adobe", "Adobe", "Adobe Creative Suite"], idiomas=[],
               experiencia="no figura", seniority="no figura")
    cv = _cv("Diseño en Canva todos los días", [])
    puntaje, cub, falt = evaluar_herramientas(p, "diseno en canva todos los dias")
    assert cub == ["Canva"] and falt == ["Adobe"] and puntaje == 50  # 2 requisitos reales, no 4
    r = puntuar_puesto(_cv("Canva y Photoshop", []), p, LLMFalso(evaluacion(brechas=[])), CFG)
    assert r.herramientas_cubiertas == ["Canva", "Adobe"] and r.herramientas_faltantes == []


# ---------- Bloque 4: equivalencias de carreras
from servicios.formacion import carreras_en_texto, evaluar_equivalencia  # noqa: E402

PIDE = "Estudiante avanzado o graduado de Marketing, Ciencias de la comunicación o carreras afines"


def test_comunicacion_social_equivale_a_ciencias_de_la_comunicacion():
    assert carreras_en_texto("Licenciado en Comunicación Social") == carreras_en_texto("Ciencias de la Comunicación")
    p = puesto(titulo_universitario=PIDE)
    eq = evaluar_equivalencia(p, "## Formación\n- Licenciado en Comunicación Social, UNLP (2021)")
    assert eq.estado == "cumple" and eq.nivel_cv == "graduado" and "Comunicación Social" in eq.cita


def test_afines_incluye_carreras_vecinas_y_excluye_las_ajenas():
    p = puesto(titulo_universitario=PIDE)
    assert evaluar_equivalencia(p, "Tecnicatura en Diseño Gráfico").estado == "cumple"
    assert evaluar_equivalencia(p, "Contador público, UBA 2019").estado == "no"
    assert evaluar_equivalencia(puesto(titulo_universitario="Profesional de Comunicaciones (el aviso no indica carrera)"),
                                "Contador público") is not None  # nombra comunicaciones, no «afines»
    assert evaluar_equivalencia(puesto(titulo_universitario="no figura", cuerpo="# X\n- Redes"), "Licenciado en Comunicación") is None


def test_estudiante_cuando_se_pide_graduado_es_parcial():
    p = puesto(titulo_universitario="Graduado/a de Comunicación Social, Publicidad o carreras afines")
    eq = evaluar_equivalencia(p, "- Licenciatura en Ciencias de la Comunicación, UBA (en curso).")
    assert eq.estado == "parcial"


def test_formacion_no_queda_baja_si_la_carrera_coincide_y_lleva_cita_verificable():
    cv = _cv("Licenciado en Comunicación Social, UNLP (2021)\nCanva", [])
    p = puesto(titulo_universitario=PIDE, herramientas=[], idiomas=[], experiencia="no figura", seniority="no figura")
    ev = evaluacion(formacion=Criterio(puntaje=10, evidencia=[]), brechas=["Título en Marketing o Ciencias de la comunicación"])
    llm = LLMFalso(ev)
    r = puntuar_puesto(cv, p, llm, CFG)
    f = r.item("formacion")
    assert f.puntaje == 85 and f.evidencia == ["Licenciado en Comunicación Social, UNLP (2021)"] and "Ajustado" in f.comentario
    assert r.brechas_modelo == [] and "Pista de formación" in llm.llamadas[0]["user"]


def test_formacion_sin_coincidencia_no_se_toca():
    cv = _cv("Contador público, UBA 2019", [])
    p = puesto(titulo_universitario=PIDE, herramientas=[], idiomas=[], experiencia="no figura", seniority="no figura")
    r = puntuar_puesto(cv, p, LLMFalso(evaluacion(formacion=Criterio(puntaje=10, evidencia=[]), brechas=[])), CFG)
    assert r.item("formacion").puntaje == 10


# ---------- Seniority eliminado y coherencia entre puntajes, brechas y resumen
def test_seniority_ya_no_es_criterio_ni_pesa():
    from servicios.matcher import PESOS
    assert "seniority" not in PESOS and abs(sum(PESOS.values()) - 1) < 1e-9
    r = puntuar_puesto(CV, puesto(seniority="Pasantía"), LLMFalso(evaluacion()), CFG)
    assert r.item("seniority") is None and {i.clave for i in r.items} == {"herramientas", "experiencia", "formacion", "otros"}


def test_brecha_de_experiencia_del_rubro_que_el_cv_ya_muestra_se_descarta():
    cv = _cv("Analista de contenidos. Campañas pagas en Meta Ads con presupuesto de USD 3.000. Diseño en Canva.", [])
    p = puesto(cuerpo="# Publicista\n## Requisitos\n- Experiencia en puestos de publicidad\n- Portfolio de trabajos\n",
               herramientas=[], idiomas=[], titulo_universitario="no figura", requiere_titulo="no figura",
               experiencia="2 años en publicidad digital")
    ev = evaluacion(experiencia=Criterio(puntaje=20, evidencia=[]), brechas=["Experiencia en puestos de publicidad", "Portfolio de trabajos"])
    r = puntuar_puesto(cv, p, LLMFalso(ev), CFG)
    assert r.item("experiencia").puntaje == 50
    assert r.brechas_modelo == ["Portfolio de trabajos"]
    assert "publicidad" not in sugerencia(brechas_de_puesto(r, [p]), 1)


def test_resumen_no_dice_que_faltan_herramientas_si_cubre_todas():
    p = puesto(herramientas=["Canva"], idiomas=[], cuerpo="# X\n## Requisitos\n- Canva\n")
    ev = evaluacion(resumen="La candidata carece de conocimientos en herramientas específicas del puesto. Buena formación.", brechas=[])
    r = puntuar_puesto(CV, p, LLMFalso(ev), CFG)
    assert r.item("herramientas").puntaje == 100
    assert "herramienta" not in r.resumen.lower() and "carece" not in r.resumen and "formación" in r.resumen


# ---------- Ofertas pegadas a mano: la formación se lee del texto
from servicios.flujo import puesto_desde_texto  # noqa: E402
from servicios.puestos_repo import formacion_de_texto  # noqa: E402
from tests.falsos import LLMGuion  # noqa: E402


@pytest.mark.parametrize("texto,titulo,req", [
    ("Buscamos redactor/a.\nRequisitos:\n- Licenciado en Publicidad, Comunicación o afines\n- Canva", "Licenciado en Publicidad, Comunicación o afines", "sí"),
    ("Se requiere licenciatura en Publicidad, Ciencias de la Comunicación o afines. Excel.", "licenciatura en Publicidad, Ciencias de la Comunicación o afines", "sí"),
    ("Requisitos: Tecnicatura superior en imagen fotográfica; manejo de Lightroom", "Tecnicatura superior en imagen fotográfica", "sí"),
    ("Requisitos:\n- Canva\nSe valora:\n- Estudiante de Comunicación", "Estudiante de Comunicación", "deseable"),
    ("Ofrecemos plan de carrera y capacitación. Requisitos: Canva", "no figura", "no figura"),
])
def test_formacion_de_texto(texto, titulo, req):
    t, r = formacion_de_texto(texto)
    assert (titulo in t or t == titulo) and r == req


@pytest.mark.parametrize("pegado,cv_texto,estado", [
    ("Se requiere licenciatura en Publicidad, Ciencias de la Comunicación o afines", "Licenciado en Comunicación Social, UNLP (2021)", "cumple"),
    ("Tecnicatura superior en imagen fotográfica", "Tecnicatura en Fotografía, ISFT (2022)", "cumple"),
    ("Licenciado en Publicidad, Comunicación o afines", "Contador público, UBA 2019", "no"),
])
def test_oferta_pegada_con_formacion_se_puntua_como_requisito(pegado, cv_texto, estado):
    p, _ = puesto_desde_texto(f"Asistente de Comunicación\nRequisitos:\n- {pegado}\n", LLMGuion(json=OfertaEstructurada()))
    assert p.requiere_titulo == "sí" and p.titulo_universitario != "no figura"
    assert evaluar_equivalencia(p, cv_texto).estado == estado
    r = puntuar_puesto(_cv(cv_texto, []), p, LLMFalso(evaluacion(formacion=Criterio(puntaje=10, evidencia=[]), brechas=[])), CFG)
    assert r.item("formacion") is not None  # el criterio aplica (antes se omitía en ofertas pegadas)
    if estado == "cumple":
        assert r.item("formacion").puntaje == 85


def test_oferta_pegada_conserva_experiencia_leida_del_texto():
    p, _ = puesto_desde_texto("Analista de datos para agencia\nSe requieren 2 años de experiencia previa. Manejo de Canva y Excel.", LLMGuion(json=OfertaEstructurada()))
    assert exigencia_experiencia(p) == "si"


# ---------- Ronda 3: graduado vs. estudiante, carreras no afines y cursos que no cuentan como estudios
CV_CAMILA = CV  # «Estudiante avanzada de Licenciatura en Ciencias de la Comunicación (en curso)» + «Curso de Marketing Digital (2025)»


def _formacion(pide, cv=CV_CAMILA, llm_puntaje=81, resumen="Cumple de sobra con la formación solicitada."):
    p = puesto(titulo_universitario=pide, requiere_titulo="sí", herramientas=[], idiomas=[], experiencia="no figura")
    ev = evaluacion(formacion=Criterio(puntaje=llm_puntaje, evidencia=["Curso de Marketing Digital"], comentario="cumple"),
                    resumen=resumen, brechas=[])
    return puntuar_puesto(cv, p, LLMFalso(ev), CFG)


@pytest.mark.parametrize("pide", ["Licenciado en Publicidad, Comunicación o afines",
                                  "Graduado en Licenciatura en Publicidad o carreras afines",
                                  "Se requiere licenciatura en Publicidad, Ciencias de la Comunicación o afines"])
def test_si_se_pide_graduado_una_estudiante_no_cumple_de_sobra(pide):
    r = _formacion(pide)
    f = r.item("formacion")
    assert 35 <= f.puntaje <= 50 and "parcialmente" in f.comentario
    assert "de sobra" not in r.resumen and "parcialmente" in r.resumen
    assert r.brechas_modelo[0].startswith("Título de grado")


@pytest.mark.parametrize("pide", ["Estudiante avanzado o graduado de Comunicación", "Estudiante de Publicidad o afines"])
def test_si_se_acepta_estudiante_cumple(pide):
    assert _formacion(pide).item("formacion").puntaje >= 85


@pytest.mark.parametrize("pide", ["Tecnicatura superior en imagen fotográfica", "Estudiante de Contador Público",
                                  "Estudiante de Ingeniería en Sistemas", "Estudiante de Veterinaria",
                                  "Estudiante de Abogacía", "Licenciado en Nutrición"])
def test_carrera_ajena_queda_baja_y_los_cursos_o_herramientas_no_son_estudios(pide):
    r = _formacion(pide)
    f = r.item("formacion")
    assert f.puntaje <= 20 and f.evidencia == [] and "no coinciden" in f.comentario
    assert "de sobra" not in r.resumen and r.brechas_modelo[0].startswith("Formación:")


def test_carrera_fuera_del_diccionario_se_busca_literalmente_en_los_estudios():
    cv = _cv("Estudiante de Sociología, UBA (en curso)\nCurso de Contabilidad básica (2024)", [])
    assert _formacion("Estudiante de Contador Público", cv).item("formacion").puntaje <= 20  # un curso no es estudios
    assert _formacion("Estudiante de Sociología", cv).item("formacion").puntaje >= 85


def test_un_curso_con_anio_ya_no_cuenta_como_graduado():
    eq = evaluar_equivalencia(puesto(titulo_universitario="Licenciado en Marketing"),
                              "## Formación\n- Curso de Marketing Digital, Fundación Ejemplo (2025, 40 horas)")
    assert eq.estado == "no"


# ---------- Ronda 3: cursos como requisito e idiomas «Suma …»
from servicios.formacion import es_curso, evaluar_cursos  # noqa: E402
from servicios.oferta_parser import parsear_oferta  # noqa: E402

CV_CURSO = _cv("## Formación\n- Estudiante avanzada de Licenciatura en Ciencias de la Comunicación (UBA, en curso)\n"
               "- Curso de Marketing Digital, Fundación Ejemplo (2025, 40 horas)\n- Diplomatura en Redes Sociales (2024)\nCanva", [])


def _puntuar_oferta(texto, est=None, cv=CV_CURSO):
    est = est or OfertaEstructurada()
    o = parsear_oferta(texto + " Buscamos asistente para agencia de comunicación.", LLMFalso(est))
    e = o.estructura
    e.herramientas, e.idiomas = o.herramientas, o.idiomas
    return puntuar_puesto(cv, puesto_desde_oferta(o.texto, e), LLMFalso(evaluacion(brechas=[])), CFG)


@pytest.mark.parametrize("pide", ["Curso de Marketing Digital", "Diplomatura en Marketing Digital", "Certificación en Marketing Digital"])
def test_curso_diplomatura_y_certificacion_son_equivalentes(pide):
    assert es_curso(pide) and evaluar_cursos([pide], CV_CURSO.texto).puntaje == 100


def test_curso_pedido_se_evalua_con_poco_peso_y_cuenta():
    est = OfertaEstructurada(requisitos=["Curso de Marketing Digital", "Canva"])
    r = _puntuar_oferta("Asistente.\nRequisitos:\nCurso de Marketing Digital.\nCanva.", est)
    c = r.item("cursos")
    assert c.puntaje == 100 and "Marketing Digital" in c.evidencia[0] and 0 < c.peso < 0.2
    assert 0.05 < __import__("servicios.matcher", fromlist=["PESOS"]).PESOS["cursos"] < 0.1  # pesa menos que una carrera
    est2 = OfertaEstructurada(requisitos=["Curso de Community Management", "Canva"])
    r2 = _puntuar_oferta("Asistente.\nRequisitos:\nCurso de Community Management.\nCanva.", est2)
    assert r2.item("cursos").puntaje == 0 and r2.puntaje < r.puntaje
    assert any(b.startswith("Curso o certificación") for b in r2.brechas_modelo)


def test_curso_deseable_no_resta_y_ofrecer_capacitacion_no_es_requisito():
    est = OfertaEstructurada(requisitos=["Canva", "Curso de Community Management"])
    r = _puntuar_oferta("Asistente.\nRequisitos:\nCanva.\nSe valora: Curso de Community Management.", est)
    assert r.item("cursos") is None and "Curso: Curso de Community Management" in r.deseables_faltantes
    r = _puntuar_oferta("Asistente.\nRequisitos: Canva. Ofrecemos cursos y capacitaciones constantes.", OfertaEstructurada(requisitos=["Canva"]))
    assert r.item("cursos") is None


def test_suma_ingles_es_deseable_no_obligatorio():
    est = OfertaEstructurada(requisitos=["Canva", "Inglés intermedio"], idiomas=["Inglés intermedio"])
    cv = _cv("Estudiante avanzada de Comunicación\nCanva", [])
    r = _puntuar_oferta("Asistente.\nRequisitos:\nCanva.\nSuma ingles intermedio.", est, cv)
    assert r.item("otros") is None and r.deseables_faltantes == ["Inglés (idioma)"] and r.brechas_idioma == []
    cv2 = _cv("Estudiante avanzada de Comunicación\nCanva\nInglés intermedio", ["Inglés intermedio"])
    assert _puntuar_oferta("Asistente.\nRequisitos:\nCanva.\nSuma ingles intermedio.", est, cv2).plus == ["Inglés (idioma)"]
    # en cambio, sin «suma» es obligatorio
    assert _puntuar_oferta("Asistente.\nRequisitos:\nCanva.\nIngles intermedio.", est, cv).item("otros").puntaje == 0


# ---------- Ronda 3c: el curso cubierto no puede figurar como brecha; sin duplicados ni idiomas como herramientas
def test_curso_cubierto_da_100_sin_brechas_aunque_el_texto_lo_repita_y_el_modelo_lo_liste():
    est = OfertaEstructurada(requisitos=["Curso de Marketing Digital", "Canva"], idiomas=["Inglés intermedio"],
                             herramientas=["Canva", "Inglés"])
    texto = "Asistente.\nRequisitos: Curso de Marketing Digital. Canva. Suma ingles intermedio."
    o = parsear_oferta(texto + " Buscamos asistente para agencia de comunicación.", LLMFalso(est))
    e = o.estructura
    e.herramientas, e.idiomas = o.herramientas, o.idiomas
    p = puesto_desde_oferta(o.texto, e)
    ev = evaluacion(brechas=["Curso de Marketing Digital"])
    r = puntuar_puesto(CV_CURSO, p, LLMFalso(ev), CFG)
    assert r.item("cursos").puntaje == 100 and "no muestra" not in r.item("cursos").comentario
    assert not any("urso" in b for b in r.brechas_modelo)
    assert r.plus == ["Inglés (idioma)"] or "Inglés" not in r.plus  # el idioma no se cuenta también como herramienta
    assert "Inglés" not in [i for i in r.herramientas_cubiertas + r.herramientas_faltantes]


def test_diplomatura_en_publicidad_y_marketing_digital_cubre_curso_de_marketing_digital():
    cv = _cv("DIPLOMATURA EN PUBLICIDAD Y MARKETING DIGITAL Universidad de Buenos Aires\nCanva", [])
    assert evaluar_cursos(["Curso de Marketing Digital"], cv.texto).puntaje == 100
    assert evaluar_cursos(["Requisitos: Curso de Marketing Digital"], cv.texto).puntaje == 100


def test_sugerencia_para_curso_faltante_no_habla_de_experiencia():
    est = OfertaEstructurada(requisitos=["Curso de Community Management", "Canva"])
    r = _puntuar_oferta("Asistente.\nRequisitos:\nCurso de Community Management.\nCanva.", est)
    txt = sugerencia(brechas_de_puesto(r, [r.puesto]), 1)
    assert "curso pedido" in txt and "experiencia concreta" not in txt
