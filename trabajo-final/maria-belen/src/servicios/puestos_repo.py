"""Carga de la base de puestos (archivos `.md` con encabezado en `data/puestos/`)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from servicios.config import PUESTOS_DIR
from servicios.texto import normalizar, truncar

CLAVES = [
    "id", "titulo", "empresa", "area", "seniority", "experiencia", "titulo_universitario", "requiere_titulo",
    "modalidad", "modalidad_tipo", "ubicacion", "herramientas", "idiomas", "lectura", "fuente", "publicado",
    "relevado", "notas",
]
NO_FIGURA = "no figura"


@dataclass
class Puesto:
    id: str
    titulo: str
    cuerpo: str
    empresa: str = NO_FIGURA
    area: str = NO_FIGURA
    seniority: str = NO_FIGURA
    experiencia: str = NO_FIGURA
    titulo_universitario: str = NO_FIGURA
    requiere_titulo: str = NO_FIGURA
    modalidad: str = NO_FIGURA
    modalidad_tipo: str = NO_FIGURA
    ubicacion: str = NO_FIGURA
    herramientas: list[str] = field(default_factory=list)
    idiomas: list[str] = field(default_factory=list)
    lectura: str = "aviso completo"
    fuente: list[str] = field(default_factory=list)
    publicado: str = NO_FIGURA
    relevado: str = NO_FIGURA
    notas: list[str] = field(default_factory=list)

    @property
    def texto_embedding(self) -> str:
        """Lo que se convierte en vector: todo el cuerpo (las notas viven en el encabezado)."""
        return self.cuerpo

    def requisitos_por_tipo(self) -> tuple[list[str], list[str]]:
        """(excluyentes, deseables) según el texto. Regla por defecto: todo lo que figura como requisito es
        excluyente, salvo que el texto lo marque expresamente como deseable/plus."""
        texto = _seccion(self.cuerpo, ("requisitos", "deseables", "requisitos deseables", "se valora", "plus",
                                       "texto de la oferta"))
        exc, des = [], []
        for linea, deseable in lineas_con_tipo(texto):
            if normalizar(linea) in ("requisitos", "deseables", "texto de la oferta"):
                continue
            (des if deseable else exc).append(linea)
        return exc, des

    def herramientas_deseables(self) -> set[str]:
        """Herramientas (de `self.herramientas`) que el texto presenta solo como deseables."""
        from servicios.vocabulario import herramienta_cubierta
        # La sección «Herramientas» es un listado derivado: no prueba que sean excluyentes; los requisitos sí.
        texto = _seccion(self.cuerpo, ("requisitos", "deseables", "requisitos deseables", "se valora", "plus",
                                       "herramientas", "texto de la oferta"))
        pares = lineas_con_tipo(texto)
        lista = {normalizar(x) for x in _seccion(self.cuerpo, ("herramientas",)).splitlines()}
        pares = [(l, d) for l, d in pares if d or normalizar("- " + l) not in lista and normalizar(l) not in lista]
        salida = set()
        for h in self.herramientas:
            en_des = any(herramienta_cubierta(h, normalizar(l)) for l, d in pares if d)
            en_exc = any(herramienta_cubierta(h, normalizar(l)) for l, d in pares if not d)
            if en_des and not en_exc:
                salida.add(h)
        return salida

    def idiomas_deseables(self) -> set[str]:
        """Idiomas que el texto presenta solo como deseables («Suma inglés intermedio», «Inglés (deseable)»)."""
        from servicios.vocabulario import idiomas_en_texto
        des = {i for t in self.idiomas if es_deseable(t) for i in idiomas_en_texto(t)}
        texto = _seccion(self.cuerpo, ("requisitos", "deseables", "requisitos deseables", "se valora", "plus",
                                       "idiomas", "texto de la oferta"))
        pares = lineas_con_tipo(texto)
        for idioma in {i for t in self.idiomas for i in idiomas_en_texto(t)}:
            en_des = any(idioma in idiomas_en_texto(l) for l, d in pares if d)
            en_exc = any(idioma in idiomas_en_texto(l) for l, d in pares if not d)
            if en_des and not en_exc:
                des.add(idioma)
        return des

    def para_prompt(self, maximo: int = 3000) -> str:
        """Texto compacto del puesto para el modelo (los datos del encabezado que importan + el cuerpo)."""
        lineas = [f"Puesto: {self.titulo}"]
        for etiqueta, valor in (("Seniority", self.seniority), ("Experiencia", self.experiencia),
                                ("Formación", self.titulo_universitario), ("Modalidad", self.modalidad)):
            if valor and valor.lower() != NO_FIGURA:
                lineas.append(f"{etiqueta}: {valor}")
        if self.idiomas:
            lineas.append("Idiomas: " + "; ".join(self.idiomas))
        cuerpo = re.sub(r"^# .*\n+", "", self.cuerpo.strip(), count=1)
        texto, _ = truncar("\n".join(lineas) + "\n\n" + cuerpo, maximo)
        return texto


_NEG_EXP = re.compile(r"\b(no (se )?(requiere|necesita|exige|pide|solicita)n? (tener )?(experiencia|antecedentes)|"
                      r"sin experiencia|no es necesari[ao] (tener )?experiencia|no exige anos|"
                      r"primer empleo|sin experiencia previa)\b")
# Marcas que convierten un requisito en deseable. "idealmente/preferentemente" NO cuentan: suelen matizar un
# detalle ("2 años, idealmente en consumo masivo"), no volver opcional todo el requisito.
_MARCA_DESEABLE = re.compile(r"\b(plus|deseables?|valorables?|opcional(es)?|se valora(n)?|valorad[ao]s?|suma(n)? (puntos )?tener|"
                             r"suma|no excluyentes?|no es excluyente|no es indispensable|no indispensable|"
                             r"es un diferencial|diferencial|nice to have)\b")
_MARCA_EXCLUYENTE = re.compile(r"\b(excluyentes?|indispensables?|obligatori[ao]s?|imprescindibles?)\b")
_SUMA_EXP = _MARCA_DESEABLE


def es_deseable(texto: str) -> bool:
    """¿El texto marca de forma explícita algo como deseable/plus? Por defecto todo requisito es excluyente."""
    n = normalizar(texto)
    if _MARCA_EXCLUYENTE.search(n) and not re.search(r"\bno excluyente|no es excluyente", n):
        return False
    return bool(_MARCA_DESEABLE.search(n))


def _clausulas(linea: str) -> list[tuple[str, bool]]:
    """Parte una línea en cláusulas (por «;» y paréntesis con marca) y marca cuáles son deseables.
    «Dominio de Premiere; suma After Effects» -> excluyente + deseable. «Formación afín (deseable)» -> deseable."""
    salida: list[tuple[str, bool]] = []
    for parte in re.split(r";|(?<=[a-záéíóúñ0-9\)])\.\s+(?=[A-ZÁÉÍÓÚ])|\s+[-–]\s+(?=(?:se valora|suma|plus|deseable))", linea):
        parte = parte.strip()
        if not parte:
            continue
        extra: list[str] = []
        marca_total = False

        def _paren(m):
            nonlocal marca_total
            dentro = m.group(1)
            if not es_deseable(dentro):
                return m.group(0)
            if not re.sub(_MARCA_DESEABLE, "", normalizar(dentro)).strip():
                marca_total = True  # «(deseable)» a secas: marca toda la cláusula
            else:
                extra.append(dentro)
            return " "
        resto = re.sub(r"\((.*?)\)", _paren, parte).strip(" .,:")
        if resto:
            salida.append((resto, marca_total or es_deseable(resto)))
        salida += [(e.strip(), True) for e in extra]
    return salida


def lineas_con_tipo(texto: str) -> list[tuple[str, bool]]:
    """[(cláusula, es_deseable)]. Un encabezado como «Deseable:» o «## Se valora» vuelve deseables las viñetas
    que le siguen; una marca propia («(deseable)», «suma …») alcanza para esa cláusula."""
    salida: list[tuple[str, bool]] = []
    heading = False
    for crudo in texto.splitlines():
        linea = crudo.strip()
        if not linea:
            continue
        viñeta = bool(re.match(r"^([-*•]|\d+[.)])\s+", linea))
        limpia = re.sub(r"^([-*•]|\d+[.)])\s+|^#+\s*", "", linea)
        if not viñeta and (linea.startswith("#") or linea.endswith(":") or len(limpia) <= 40):
            heading = es_deseable(limpia)
            continue
        if not viñeta:
            heading = False
        for cl, d in _clausulas(limpia):
            salida.append((cl, d or (viñeta and heading)))
    return salida


def _seccion(cuerpo: str, titulos: tuple[str, ...]) -> str:
    partes = re.split(r"(?m)^## ", cuerpo)
    return "\n".join("## " + p for p in partes[1:] if normalizar(p.splitlines()[0]) in titulos)


def exigencia_experiencia(puesto: "Puesto") -> str:
    """¿Exige el puesto experiencia previa? 'si' | 'deseable' | 'no' (no la pide o no la menciona).
    Solo 'si' puede restar puntaje por experiencia."""
    exp = normalizar(puesto.experiencia or "")
    sen = normalizar(puesto.seniority or "")
    if not exp or exp.startswith("no figura"):
        # sin dato en el encabezado: solo cuenta si el propio texto la pide explícitamente
        cuerpo = normalizar(puesto.cuerpo)
        if _NEG_EXP.search(cuerpo):
            return "no"
        if re.search(r"\b\d+ (anos?|meses) (de )?experiencia|experiencia (previa |minima |comprobable )?(de )?\d+ anos?",
                     cuerpo):
            return "si"
        return "no"
    if _NEG_EXP.search(exp) or re.match(r"^0 a \d", exp):
        return "deseable" if es_deseable(exp) or re.search(r"\bsuma\b|se valora|se prefiere", exp) else "no"
    if es_deseable(exp) and not re.search(r"\d", exp):
        return "deseable"
    if re.search(r"pasant|trainee|becari", sen) and not re.search(r"\d+ (anos?|meses)", exp):
        return "no"
    return "si"


def parsear_puesto(texto: str, origen: str = "") -> Puesto:
    m = re.match(r"---\n(.*?)\n---\n\n?(.*)", texto, re.S)
    if not m:
        raise ValueError(f"{origen}: el archivo no empieza con un encabezado entre '---'")
    datos: dict = {}
    for linea in m.group(1).splitlines():
        if ": " not in linea:
            raise ValueError(f"{origen}: línea de encabezado inválida: {linea[:60]!r}")
        clave, valor = linea.split(": ", 1)
        try:
            datos[clave] = json.loads(valor)
        except json.JSONDecodeError as e:
            raise ValueError(f"{origen}: el valor de '{clave}' no es JSON válido ({e.msg})") from e
    faltan = [c for c in CLAVES if c not in datos]
    if faltan:
        raise ValueError(f"{origen}: faltan campos en el encabezado: {', '.join(faltan)}")
    return Puesto(cuerpo=m.group(2).strip() + "\n", **{c: datos[c] for c in CLAVES})


def cargar_puestos(carpeta: Path | str = PUESTOS_DIR) -> list[Puesto]:
    carpeta = Path(carpeta)
    puestos = []
    for ruta in sorted(carpeta.glob("*.md")):
        puestos.append(parsear_puesto(ruta.read_text(encoding="utf-8"), ruta.name))
    ids = [p.id for p in puestos]
    if len(set(ids)) != len(ids):
        raise ValueError("Hay ids de puestos repetidos en la base")
    return puestos


def _experiencia_de_texto(texto: str) -> str:
    """Frase del texto pegado que habla de experiencia exigida (o 'no figura' si no se menciona)."""
    for linea in re.split(r"[\n.;]", texto):
        n = normalizar(linea)
        if "experiencia" in n and (_NEG_EXP.search(n) or re.search(r"\d+ (anos?|meses)|requer|requiere|previa|minim|comprobable|exig", n)):
            return linea.strip(" -*•\t")[:200]
    return NO_FIGURA


_FORMACION = re.compile(r"\b(licenciad[oa]s?|licenciatura|tecnicatura|tecnic[oa]s? superior|tecnic[oa]s?|titulo|titulad[oa]s?|"
                        r"estudiante|graduad[oa]s?|egresad[oa]s?|universitari[oa]s?|terciari[oa]s?|carreras?|ingenier[oa]|"
                        r"profesorado|posgrado|estudios (?:universitarios|superiores|terciarios|en curso))\b")


_NO_ES_FORMACION = re.compile(r"plan de carrera|desarrollo de (tu )?carrera|crecimiento|oportunidades? de carrera|carrera profesional|"
                              r"linea de carrera|capacitaci")


def es_clausula_formacion(texto: str) -> bool:
    n = normalizar(texto)
    return bool(_FORMACION.search(n)) and not _NO_ES_FORMACION.search(n)


def formacion_de_texto(texto: str, requisitos: list[str] | None = None) -> tuple[str, str]:
    """(titulo_universitario, requiere_titulo) leídos del texto de una oferta pegada.
    Busca cláusulas que hablan de estudios («Licenciado en Publicidad, Comunicación o afines», «Tecnicatura
    superior en imagen fotográfica»). requiere_titulo: «sí» o «deseable» (si todas las cláusulas son opcionales)."""
    candidatas: list[tuple[str, bool]] = []
    for linea, des in lineas_con_tipo(texto):
        if _FORMACION.search(normalizar(linea)) and not _NO_ES_FORMACION.search(normalizar(linea)):
            candidatas.append((linea, des))
    for r in requisitos or []:
        if _FORMACION.search(normalizar(r)) and not any(normalizar(r) in normalizar(c) or normalizar(c) in normalizar(r)
                                                          for c, _ in candidatas):
            candidatas.append((r, es_deseable(r)))
    candidatas = [(re.sub(r"^(se requiere|requisitos?:|buscamos|requerimos|excluyente:?)\s+", "", c.strip(" -*•."), flags=re.I), d)
                  for c, d in candidatas if len(c) <= 220]
    if not candidatas:
        return NO_FIGURA, NO_FIGURA
    obligatorias = [c for c, d in candidatas if not d]
    elegidas = obligatorias[:2] or [c for c, _ in candidatas[:2]]
    return "; ".join(elegidas), ("sí" if obligatorias else "deseable")


def puesto_desde_oferta(texto: str, oferta) -> Puesto:
    """Arma un `Puesto` temporal a partir de una oferta pegada y su extracción estructurada."""
    titulo = (oferta.titulo or "Puesto pegado").strip()
    cuerpo = [f"# {titulo}", ""]
    if oferta.requisitos:
        cuerpo += ["## Requisitos", *[f"- {r}" for r in oferta.requisitos], ""]
    if oferta.deseables:
        cuerpo += ["## Deseables", *[f"- {r}" for r in oferta.deseables], ""]
    texto_corto, _ = truncar(texto.strip(), 2500)
    cuerpo += ["## Texto de la oferta", texto_corto, ""]
    exp = _experiencia_de_texto(texto)
    formacion, req_titulo = formacion_de_texto(texto, list(oferta.requisitos) + list(oferta.deseables))
    return Puesto(
        id="oferta-pegada", experiencia=exp, titulo_universitario=formacion, requiere_titulo=req_titulo, titulo=titulo, cuerpo="\n".join(cuerpo),
        empresa=oferta.empresa or NO_FIGURA, herramientas=list(oferta.herramientas),
        idiomas=list(oferta.idiomas), lectura="aviso completo", fuente=["Texto pegado por la persona"],
    )
