from servicios.config import EJEMPLOS_DIR
from servicios.verificador import verificar

CV = (EJEMPLOS_DIR / "cv-ejemplo-junior.md").read_text(encoding="utf-8")
OFERTA = "Agencia Brújula busca Community Manager con manejo de Canva."


def tipos(texto, oferta=""):
    return [(h.tipo, h.fragmento) for h in verificar(texto, CV, oferta)]


def test_texto_fiel_al_cv_no_marca_nada():
    texto = """# Camila Rojas
## Experiencia
- **Community manager voluntaria — Centro Cultural La Esquina** (marzo 2025 – actualidad)
- Aumento de seguidores de Instagram de 800 a 1.500 en 8 meses, con Canva y Google Sheets.
## Formación
1. Licenciatura en Ciencias de la Comunicación, UBA (en curso).
Inglés intermedio (B1)."""
    assert tipos(texto) == []


def test_marca_cifras_inventadas():
    t = tipos("Aumenté los seguidores de 800 a 3.000 y tengo dos años de experiencia.")
    assert ("cifra", "3.000") in t and ("cifra", "dos años") in t
    assert ("cifra", "800") not in t


def test_formato_de_miles_equivalente():
    assert tipos("Llegué a 1500 seguidores.") == []


def test_marca_herramientas_que_el_cv_no_tiene():
    t = tipos("Manejo Canva, Photoshop y Premiere Pro.")
    assert ("herramienta", "Photoshop") in t and not any(f == "Canva" for _, f in t)


def test_marca_empleadores_inventados_pero_acepta_los_del_cv():
    t = tipos("Trabajé en Agencia Meridiano y en el Centro Cultural La Esquina.")
    assert ("nombre propio", "Agencia Meridiano") in t
    assert not any("Esquina" in f for _, f in t)


def test_nombres_de_la_oferta_se_aceptan_solo_si_se_pasa_la_oferta():
    carta = "Estimado equipo de Agencia Brújula: me entusiasma postularme."
    assert tipos(carta) != [] and tipos(carta, OFERTA) == []


def test_marca_titulos_que_no_figuran():
    t = tipos("Soy graduada en Comunicación.")
    assert ("título", "graduada") in t and tipos("Licenciatura en Comunicación en curso.") == []


def test_palabra_inicial_de_oracion_no_se_toma_por_nombre_propio():
    assert tipos("Trabajé con Instagram. Aprendí mucho sobre redes sociales.") == []


def test_contexto_y_fragmento_sirven_para_resaltar():
    texto = "Gestioné campañas en Globant con 9 personas."
    for h in verificar(texto, CV):
        assert h.fragmento in texto and h.fragmento in h.contexto
