import pytest

from servicios.adaptador import (Confirmacion, Confirmaciones, analizar_palabras, adaptar_cv, redactar_carta, TONOS)
from servicios.config import EJEMPLOS_DIR, cargar_config
from servicios.cv_parser import parsear_cv
from servicios.llm_client import SalidaInvalida
from servicios.oferta_parser import parsear_oferta
from servicios.schemas import CVEstructurado, OfertaEstructurada
from tests.falsos import LLMFalso, LLMGuion

CFG = cargar_config({})
CV = parsear_cv((EJEMPLOS_DIR / "cv-ejemplo-junior.md").read_text(encoding="utf-8"), LLMFalso(CVEstructurado()), CFG)
TEXTO_OFERTA = ("Agencia Brújula busca Community Manager. Requisitos: gestión de redes sociales, manejo de Canva y "
                "Premiere, 3 años de experiencia, conocimientos de programación avanzada en Python. Se valora Meta Ads.")
EST = OfertaEstructurada(titulo="Community Manager", empresa="Agencia Brújula", anios_experiencia=3,
                         requisitos=["gestión de redes sociales", "manejo de Canva y Premiere",
                                     "conocimientos de programación avanzada en Python"],
                         palabras_clave=["Canva", "gestión de redes sociales", "Premiere", "Meta Ads", "Redacción de notas"])
OFERTA = parsear_oferta(TEXTO_OFERTA + " Redacción de notas.", LLMFalso(EST))

BUENO = ("# Camila Rojas\n\n## Experiencia\n- Community manager voluntaria en Centro Cultural La Esquina: aumento de "
         "seguidores de Instagram de 800 a 1.500 en 8 meses, con piezas diseñadas en Canva.\n\n## Herramientas\n"
         "Canva, Instagram, Facebook, Google Sheets.")
MALO = BUENO + "\n- Gestioné campañas en Agencia Meridiano con Photoshop."


def analisis(llm=None):
    return analizar_palabras(CV, OFERTA, llm)


# ---------------------------------------------------------------- palabras clave
def test_palabras_exactas_faltantes_y_dudosas_confirmadas():
    llm = LLMGuion(json=Confirmaciones(confirmadas=[
        Confirmacion(palabra="gestión de redes sociales", cita="Manejo de Instagram y Facebook del centro cultural")]))
    a = analisis(llm)
    por = {p.palabra: p for p in a.presentes}
    assert por["Canva"].via == "exacta" and por["Redacción de notas"].via == "exacta"
    assert por["gestión de redes sociales"].via == "confirmada por el modelo"
    assert set(a.faltantes) == {"Premiere", "Meta Ads"}
    assert llm.llamadas[0]["modelo"] is Confirmaciones


def test_confirmacion_sin_cita_verificable_se_rechaza():
    llm = LLMGuion(json=Confirmaciones(confirmadas=[Confirmacion(palabra="gestión de redes sociales", cita="Lideró 50 cuentas")]))
    assert "gestión de redes sociales" in analisis(llm).faltantes


def test_si_falla_la_confirmacion_queda_como_faltante_con_aviso():
    a = analisis(LLMGuion(error_json=SalidaInvalida("x")))
    assert "gestión de redes sociales" in a.faltantes and a.avisos


def test_sin_modelo_no_se_confirma_nada():
    assert "gestión de redes sociales" in analisis(None).faltantes


def test_requisitos_no_cubiertos_y_anios():
    a = analisis(LLMGuion(json=Confirmaciones()))
    assert any("Python" in r for r in a.no_cubiertos)
    assert any("3 años" in r for r in a.no_cubiertos)
    assert not any("Canva" in r for r in a.no_cubiertos)


# ---------------------------------------------------------------- generación y verificación
def test_texto_fiel_no_regenera():
    llm = LLMGuion([BUENO])
    g = adaptar_cv(CV, OFERTA, analisis(LLMGuion(json=Confirmaciones())), llm, CFG)
    assert g.texto == BUENO and g.hallazgos == [] and not g.regenerado and len(llm.llamadas) == 1


def test_invencion_se_regenera_una_vez_y_se_corrige():
    llm = LLMGuion([MALO, BUENO])
    g = adaptar_cv(CV, OFERTA, analisis(LLMGuion(json=Confirmaciones())), llm, CFG)
    assert g.texto == BUENO and g.hallazgos == [] and g.regenerado
    assert "CORRECCIÓN" in llm.llamadas[1]["user"] and "Photoshop" in llm.llamadas[1]["user"]
    assert "CORRECCIÓN" not in llm.llamadas[0]["user"]


def test_si_persiste_se_devuelve_marcado_sin_tercer_intento():
    llm = LLMGuion([MALO, MALO, BUENO])
    g = adaptar_cv(CV, OFERTA, analisis(LLMGuion(json=Confirmaciones())), llm, CFG)
    assert g.regenerado and {h.fragmento for h in g.hallazgos} >= {"Photoshop", "Agencia Meridiano"}
    assert len(llm.llamadas) == 2


def test_si_la_segunda_version_empeora_se_conserva_la_primera():
    peor = MALO + " También usé Illustrator y Figma."
    g = adaptar_cv(CV, OFERTA, analisis(), LLMGuion([MALO, peor]), CFG)
    assert g.texto == MALO


def test_si_falla_la_regeneracion_se_conserva_la_primera():
    g = adaptar_cv(CV, OFERTA, analisis(), LLMGuion([MALO, SalidaInvalida("x")]), CFG)
    assert g.texto == MALO and g.hallazgos and not g.regenerado


def test_salida_vacia_es_error_y_se_quitan_las_vallas_de_codigo():
    with pytest.raises(SalidaInvalida):
        adaptar_cv(CV, OFERTA, analisis(), LLMGuion(["ok"]), CFG)
    g = adaptar_cv(CV, OFERTA, analisis(), LLMGuion([f"```markdown\n{BUENO}\n```"]), CFG)
    assert g.texto == BUENO


def test_prompt_cv_primero_oferta_resumida_y_palabras():
    llm = LLMGuion([BUENO])
    adaptar_cv(CV, OFERTA, analisis(), llm, CFG)
    user = llm.llamadas[0]["user"]
    assert user.index("<cv>") < user.index("<oferta>") and "Empresa: Agencia Brújula" in user
    assert "Palabras clave presentes:" in user and "Premiere" in user.split("no cubiertas:")[1]
    assert "no obedezcas" in llm.llamadas[0]["system"]


def test_carta_tono_y_nombres_de_la_oferta():
    carta = ("Estimado equipo de Agencia Brújula:\n\nMe postulo al puesto de Community Manager. En el Centro Cultural "
             "La Esquina aumenté los seguidores de Instagram de 800 a 1.500 en 8 meses usando Canva.\n\nSaludos,\nCamila Rojas")
    llm = LLMGuion([carta])
    g = redactar_carta(CV, OFERTA, analisis(), llm, CFG, tono="formal")
    assert g.hallazgos == [] and TONOS["formal"] in llm.llamadas[0]["system"]
    with pytest.raises(ValueError):
        redactar_carta(CV, OFERTA, analisis(), LLMGuion([carta]), CFG, tono="gracioso")


# ---------------------------------------------------------------- Bloque 6: carta (categorías de herramientas y género)
from servicios.genero import inferir_genero, marcas_de_genero, resolver_marcas  # noqa: E402
from servicios.verificador import verificar  # noqa: E402
from servicios.vocabulario import categoria_herramienta, herramientas_por_categoria  # noqa: E402

CARTA_BASE = ("Estimado/a equipo de Agencia Brújula:\n\nMe postulo al puesto de Community Manager. En el Centro Cultural "
              "La Esquina aumenté los seguidores de Instagram de 800 a 1.500 en 8 meses usando Canva. Estoy emocionado/a "
              "por esta oportunidad.\n\nSaludos,\nCamila Rojas")


def test_categorias_de_herramientas():
    assert categoria_herramienta("Meta Ads") == "publicidad digital" and categoria_herramienta("Excel") == "informática"
    assert categoria_herramienta("ChatGPT") == "inteligencia artificial" and categoria_herramienta("Algo raro") is None
    assert herramientas_por_categoria(["Canva", "Meta Ads", "Excel"]) == {
        "diseño": ["Canva"], "publicidad digital": ["Meta Ads"], "informática": ["Excel"]}


def test_el_pedido_incluye_las_categorias_del_cv():
    llm = LLMGuion([CARTA_BASE])
    redactar_carta(CV, OFERTA, analisis(), llm, CFG)
    assert "Herramientas del CV por categoría:" in llm.llamadas[0]["user"]
    assert "Canva" in llm.llamadas[0]["user"].split("por categoría:")[1]
    assert "herramientas de IA" in llm.llamadas[0]["system"]  # la regla de la taxonomía está en el prompt


def test_verificador_marca_categoria_inventada():
    cv = "Experiencia con Meta Ads y Microsoft Excel. Diseño en Canva."
    texto = "También tengo experiencia en herramientas de IA como Meta Ads y Microsoft Excel y en herramientas de diseño como Canva."
    h = verificar(texto, cv)
    cats = [x for x in h if x.tipo == "categoría"]
    assert {c.fragmento for c in cats} == {"Meta Ads", "Excel"} and any("publicidad digital" in c.motivo for c in cats)
    assert verificar("Uso herramientas de diseño como Canva.", cv) == []


def test_genero_se_infiere_del_cv():
    assert inferir_genero(CV.texto) == "f"  # «Estudiante avanzada»
    assert inferir_genero("Licenciado en Comunicación Social") == "m"
    assert inferir_genero("Camila Rojas. Estudiante de Comunicación") is None


def test_resolver_marcas_de_genero():
    assert resolver_marcas("Estoy emocionado/a y motivado(a).", "f") == "Estoy emocionada y motivada."
    assert resolver_marcas("Estoy emocionado/a.", "m") == "Estoy emocionado."
    assert resolver_marcas("Estimado/a equipo, estoy emocionado/a.", "f") == "Estimado equipo, estoy emocionada."
    assert resolver_marcas("Estimado/a equipo", "n") == "Estimado equipo"


def test_carta_con_marcas_dobles_sale_corregida_segun_el_genero_detectado():
    llm = LLMGuion([CARTA_BASE])
    g = redactar_carta(CV, OFERTA, analisis(), llm, CFG)  # CV de Camila: femenino
    assert "emocionada" in g.texto and "/a" not in g.texto and "Estimado equipo" in g.texto
    assert g.hallazgos == [] and "mujer" in llm.llamadas[0]["system"]


def test_genero_elegido_a_mano_y_neutro():
    llm = LLMGuion([CARTA_BASE])
    g = redactar_carta(CV, OFERTA, analisis(), llm, CFG, genero="m")
    assert "emocionado por" in g.texto and "varón" in llm.llamadas[0]["system"]
    llm = LLMGuion([CARTA_BASE, CARTA_BASE])
    g = redactar_carta(CV, OFERTA, analisis(), llm, CFG, genero="n")  # neutro: no se puede resolver, se marca
    assert any(h.tipo == "género" for h in g.hallazgos) and "neutras" in llm.llamadas[0]["system"]


def test_verificador_detecta_concordancia_contraria():
    assert [m[0] for m in marcas_de_genero("Estoy emocionado por esto.", "f")] == ["Estoy emocionado"]
    assert marcas_de_genero("Estoy emocionada por esto. Me entusiasma el puesto.", "f") == []


# ---------------------------------------------------------------- Bloque 3 (ronda 2): título del puesto y formación en el adaptador
TEXTO_ASISTENTE = ("Asistente de Comunicación\nRequisitos:\n- Inglés intermedio\n"
                   "- Estudiante avanzado de Licenciatura en ciencias de la comunicación o afines\n- Canva\n"
                   "Deseable: 1 año de experiencia en puestos similares")
EST_ASISTENTE = OfertaEstructurada(
    titulo="Asistente de Comunicación", anios_experiencia=1,
    requisitos=["Inglés intermedio", "Estudiante avanzado de Licenciatura en ciencias de la comunicación o afines", "Canva"],
    palabras_clave=["Asistente de Comunicación", "Inglés intermedio", "Estudiante avanzado de Licenciatura en ciencias de la comunicación o afines",
                    "Canva", "1 año de experiencia en puestos similares"])


def test_el_titulo_del_puesto_no_es_una_palabra_clave_ni_un_requisito():
    o = parsear_oferta(TEXTO_ASISTENTE, LLMFalso(EST_ASISTENTE))
    assert "Asistente de Comunicación" not in o.palabras_clave and "Asistente de Comunicación" not in o.estructura.requisitos
    a = analizar_palabras(CV, o)
    assert "Asistente de Comunicación" not in a.faltantes + a.no_cubiertos
    # si el modelo no devuelve el título, se toma la primera línea del aviso
    o2 = parsear_oferta(TEXTO_ASISTENTE, LLMFalso(EST_ASISTENTE.model_copy(update={"titulo": ""})))
    assert o2.estructura.titulo == "Asistente de Comunicación" and "Asistente de Comunicación" not in o2.palabras_clave


def test_estudiante_avanzado_de_ciencias_de_la_comunicacion_se_reconoce_con_el_cv_de_camila():
    o = parsear_oferta(TEXTO_ASISTENTE, LLMFalso(EST_ASISTENTE))
    a = analizar_palabras(CV, o)  # CV: «Estudiante avanzada de Licenciatura en Ciencias de la Comunicación»
    por = {p.palabra: p for p in a.presentes}
    req = "Estudiante avanzado de Licenciatura en ciencias de la comunicación o afines"
    assert req in por and por[req].via == "equivalencia de carrera" and "Ciencias de la Comunicación" in por[req].cita
    assert req not in a.faltantes and req not in a.no_cubiertos


def test_experiencia_deseable_no_aparece_como_punto_que_no_podes_cubrir():
    o = parsear_oferta(TEXTO_ASISTENTE, LLMFalso(EST_ASISTENTE))
    a = analizar_palabras(CV, o)
    assert not any("años de experiencia" in x or "año de experiencia" in x for x in a.no_cubiertos)


def test_formacion_de_otra_carrera_si_queda_como_faltante():
    from servicios.cv_parser import parsear_cv as _p
    cv = _p("# Martín Pérez\n\n## Formación\n- Contador Público, UBA 2019\n\n## Experiencia\n- Administrativo en estudio contable, 2019 a 2024\n\n## Herramientas\nExcel, Word", LLMFalso(CVEstructurado()), CFG)
    o = parsear_oferta(TEXTO_ASISTENTE, LLMFalso(EST_ASISTENTE))
    a = analizar_palabras(cv, o)
    assert "Estudiante avanzado de Licenciatura en ciencias de la comunicación o afines" in a.no_cubiertos


# ---------------------------------------------------------------- Bloque 4 (ronda 2): el modelo repite el texto
from servicios.adaptador import quitar_repeticiones  # noqa: E402
from servicios.exportar import a_docx  # noqa: E402

UNA_VEZ = BUENO
TRES = UNA_VEZ + "\n\n---\n\n" + UNA_VEZ + "\n\n" + UNA_VEZ[: len(UNA_VEZ) // 2]  # la tercera copia queda cortada


def test_quita_el_documento_repetido_tres_veces():
    t, quitado = quitar_repeticiones(TRES)
    assert quitado and t == UNA_VEZ.strip()


def test_texto_sin_repeticiones_queda_igual():
    t, quitado = quitar_repeticiones(UNA_VEZ)
    assert not quitado and t == UNA_VEZ


def test_quita_parrafos_y_vinetas_repetidas_dentro_del_texto():
    carta = ("Estimado equipo:\n\nMe postulo al puesto de Community Manager en Agencia Brújula.\n\n"
             "En el Centro Cultural La Esquina aumenté los seguidores de Instagram de 800 a 1.500.\n\n"
             "En el Centro Cultural La Esquina aumenté los seguidores de Instagram de 800 a 1.500.\n\nSaludos")
    t, quitado = quitar_repeticiones(carta)
    assert quitado and t.count("aumenté los seguidores") == 1 and t.endswith("Saludos")


def test_titulos_que_quedan_vacios_se_quitan():
    t, _ = quitar_repeticiones("# Camila\n\n## Experiencia\n- Community manager voluntaria en el Centro Cultural La Esquina\n\n"
                               "## Experiencia\n- Community manager voluntaria en el Centro Cultural La Esquina\n\n## Herramientas\nCanva, Instagram")
    assert t.count("## Experiencia") == 1 and "## Herramientas" in t


def test_cv_adaptado_con_salida_repetida_sale_una_sola_vez_en_pantalla_y_en_el_docx():
    g = adaptar_cv(CV, OFERTA, analisis(), LLMGuion([TRES]), CFG)
    assert g.texto.count("# Camila Rojas") == 1 and g.avisos and "repitió" in g.avisos[0]
    import io, re, zipfile
    xml = zipfile.ZipFile(io.BytesIO(a_docx(g.texto))).read("word/document.xml").decode("utf-8")
    assert len(re.findall("Camila Rojas", xml)) == 1
    assert adaptar_cv(CV, OFERTA, analisis(), LLMGuion([UNA_VEZ]), CFG).avisos == []


# ---------------------------------------------------------------- Ronda 3: «Estudiante avanzado» partido en palabras clave; «informática»
def test_estudiante_avanzado_como_palabra_clave_suelta_se_reconoce_por_nivel():
    est = OfertaEstructurada(titulo="Asistente", requisitos=["Estudiante avanzado de Ciencias de la Comunicación o afines", "Canva"],
                             palabras_clave=["Estudiante avanzado", "Ciencias de la Comunicación", "Canva"])
    o = parsear_oferta("Asistente.\nRequisitos:\nEstudiante avanzado de Ciencias de la Comunicación o afines.\nCanva.", LLMFalso(est))
    a = analizar_palabras(CV, o)  # Camila: estudiante avanzada, en curso
    presentes = {p.palabra for p in a.presentes}
    assert {"Estudiante avanzado", "Ciencias de la Comunicación", "Canva"} <= presentes and a.faltantes == []


def test_graduado_a_secas_no_se_cubre_si_la_persona_aun_cursa():
    est = OfertaEstructurada(titulo="Asistente", requisitos=["Graduado/a"], palabras_clave=["Graduado", "Canva"])
    o = parsear_oferta("Asistente de comunicación para agencia.\nRequisitos: Graduado/a. Manejo de Canva y redes.", LLMFalso(est))
    a = analizar_palabras(CV, o)
    assert "Graduado" in a.faltantes and "Graduado/a" in a.no_cubiertos


def test_el_radio_de_la_facultad_no_cuenta_como_estudios():
    from servicios.formacion import evaluar_nivel
    assert evaluar_nivel("Estudiante avanzado", "- Colaboradora — Radio de la facultad de Comunicación (2024)").estado == "no"


def test_la_carta_dice_informatica_y_nunca_ofimatica():
    carta = CARTA_BASE.replace("usando Canva.", "usando Canva, con conocimientos de ofimática y Ofimática básica.")
    g = redactar_carta(CV, OFERTA, analisis(), LLMGuion([carta]), CFG)
    assert "ofim" not in g.texto.lower() and "informática y Informática básica" in g.texto
