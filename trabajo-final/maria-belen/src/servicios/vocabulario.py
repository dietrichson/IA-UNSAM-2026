"""Vocabulario de herramientas, sinónimos e idiomas.

Sirve para tres cosas: detectar qué herramientas menciona un texto, decidir si un CV
cubre una herramienta que pide un puesto (incluyendo equivalentes básicos) y alimentar
el verificador anti-invención.
"""
from __future__ import annotations

import re

from servicios.texto import contiene_termino, normalizar

HERRAMIENTAS_COMUNES = [
    "Canva", "Photoshop", "Illustrator", "InDesign", "Premiere", "Premiere Pro", "After Effects", "CapCut",
    "Figma", "Final Cut Pro", "Excel", "Word", "PowerPoint", "Google Sheets", "Google Drive", "Google Docs",
    "Google Analytics", "GA4", "Looker Studio", "Search Console", "Google Ads", "Meta Ads", "Facebook Ads",
    "Meta Business Suite", "LinkedIn Ads", "TikTok Ads", "Mailchimp", "HubSpot", "Salesforce", "WordPress",
    "Wix", "Shopify", "Tienda Nube", "Notion", "Trello", "Asana", "Slack", "Microsoft Teams", "Teams", "Zoom",
    "SharePoint", "Microsoft 365", "Hootsuite", "Buffer", "Metricool", "Later", "ChatGPT", "Gemini", "Claude",
    "Perplexity", "Copilot", "SEMrush", "Ahrefs", "Zapier", "n8n", "Make", "Instagram", "Facebook", "TikTok",
    "YouTube", "LinkedIn", "Twitter", "Pinterest", "WhatsApp", "Reddit", "Intranet", "Newsletter", "SEO",
    "Sitecore", "Drupal", "AEM", "Frame.io", "Viva Engage", "Bing Places", "Google Business Profile",
    "Adobe", "Adobe Creative Suite", "Yelp", "Trustpilot", "GoHighLevel", "CRM", "Apps Script", "Metricool", "Adobe Express",
]

# Grupos de equivalencia básicos (todo en forma normalizada: minúsculas, sin tildes).
SINONIMOS: list[set[str]] = [
    {"meta ads", "facebook ads", "instagram ads", "anuncios en meta", "anuncios de facebook"},
    {"ga4", "google analytics 4", "google analytics"},
    {"looker studio", "data studio", "google data studio"},
    {"premiere", "premiere pro", "adobe premiere", "adobe premiere pro"},
    {"adobe", "adobe creative suite", "adobe creative cloud", "creative suite", "creative cloud", "adobe cc",
     "paquete adobe", "suite adobe"},
    {"photoshop", "adobe photoshop"},
    {"illustrator", "adobe illustrator"},
    {"after effects", "adobe after effects"},
    {"excel", "microsoft excel", "planilla de calculo", "planillas de calculo", "hojas de calculo", "google sheets"},
    {"chatgpt", "chat gpt", "gpt"},
    {"microsoft 365", "office 365", "m365", "paquete office", "microsoft office"},
    {"search console", "google search console", "gsc"},
    {"google ads", "adwords", "google adwords"},
    {"tienda nube", "tiendanube"},
    {"capcut", "cap cut"},
    {"seo", "posicionamiento organico", "posicionamiento en buscadores"},
    {"crm", "salesforce", "hubspot", "zoho", "pipedrive"},
    {"newsletter", "newsletters", "boletin", "boletines"},
    {"teams", "microsoft teams"},
]

IDIOMAS = {
    "inglés": ("ingles", "english"),
    "portugués": ("portugues", "portuguese"),
    "francés": ("frances", "french"),
    "italiano": ("italiano", "italian"),
    "alemán": ("aleman", "german"),
}

_PALABRAS_SUELTAS_RUIDOSAS = {"make", "later", "teams", "word", "claude", "gemini"}


def grupo_de(termino_norm: str) -> set[str]:
    for g in SINONIMOS:
        if termino_norm in g:
            return set(g)
    return {termino_norm}


# Una herramienta «de familia» (Adobe) queda cubierta si el CV muestra cualquiera de sus programas.
FAMILIAS: dict[str, set[str]] = {
    "adobe": {"photoshop", "illustrator", "indesign", "premiere", "premiere pro", "after effects", "adobe express",
              "lightroom", "acrobat", "adobe premiere", "adobe photoshop", "adobe illustrator", "adobe after effects"},
}
_PREFIJO = re.compile(r"^(?:diseno(?: grafico)?|manejo|conocimientos?|uso|dominio|experiencia|nivel \w+)"
                      r"(?: (?:de|del|en|con|sobre))?\s+")


def _sin_prefijo(parte_norm: str) -> str:
    """«diseno en canva» -> «canva» (conserva el original si no queda nada)."""
    sin = _PREFIJO.sub("", parte_norm).strip()
    return sin if len(sin) >= 2 else parte_norm


def alternativas(item: str) -> list[str]:
    """Descompone un ítem de la lista de herramientas de un puesto en alternativas normalizadas.

    "Google Analytics 4 (GA4)" -> ["google analytics 4", "ga4"];
    "Diseño en Canva y/o Adobe" -> ["canva", "adobe"];
    "ChatGPT, Claude, Gemini o Perplexity" -> cuatro alternativas (alcanza con una)."""
    item = re.sub(r"\s+[ye]/o\s+", ", ", item, flags=re.I)
    fuera = re.sub(r"\(.*?\)", " ", item)
    dentro = re.findall(r"\((.*?)\)", item)
    salida: list[str] = []
    for bloque in [fuera, *dentro]:
        for parte in re.split(r",|/|;| o | y | u ", bloque):
            p = _sin_prefijo(normalizar(parte))
            if len(p) >= 2 and p not in salida and p not in {"sin especificar", "preferentemente"}:
                salida.append(p)
    return salida


def _terminos(item: str) -> set[str]:
    """Todos los nombres equivalentes de un ítem (sinónimos incluidos), para comparar requisitos entre sí."""
    return {t for alt in alternativas(item) for t in grupo_de(alt)}


def etiqueta_herramienta(item: str) -> str:
    """«Diseño en Canva y/o Adobe» -> «Canva y/o Adobe» (solo para mostrar)."""
    palabras = re.sub(r"\s+", " ", item).strip().split()
    for n in range(min(3, len(palabras) - 1), 0, -1):
        if _PREFIJO.sub("", normalizar(" ".join(palabras[:n])) + " x") == "x":
            return " ".join(palabras[n:])
    return " ".join(palabras)


def herramientas_unicas(items: list[str]) -> list[str]:
    """Quita requisitos de herramienta repetidos o contenidos en otro: «Adobe» = «Adobe Creative Suite»;
    «Canva» ⊂ «Diseño en Canva y/o Adobe» (se conserva el más específico). Mantiene el orden."""
    datos = [(it, _terminos(it)) for it in items]
    salida: list[str] = []
    for i, (it, ts) in enumerate(datos):
        if not ts:
            salida.append(it)
            continue
        redundante = False
        for j, (otro, tj) in enumerate(datos):
            if i == j or not tj:
                continue
            if tj < ts:  # el otro es más específico (un subconjunto de alternativas)
                redundante = True
            elif tj == ts and (len(otro), j) < (len(it), i):  # idénticos: queda el más corto/primero
                redundante = True
        if not redundante:
            salida.append(etiqueta_herramienta(it))
    return salida


def es_generica(item: str) -> bool:
    n = normalizar(item)
    return n.startswith("herramientas de") or n in {"redes sociales", "no figuran en el aviso leido"}


def herramienta_cubierta(item: str, texto_norm: str) -> bool:
    """¿El texto (ya normalizado) menciona la herramienta o algún equivalente básico?"""
    for alt in alternativas(item):
        terminos = set(grupo_de(alt))
        for familia, miembros in FAMILIAS.items():
            if familia in terminos:
                terminos |= miembros
        if any(contiene_termino(texto_norm, t) for t in terminos):
            return True
    return False


def herramientas_en_texto(texto: str, extra: list[str] | None = None) -> list[str]:
    """Herramientas del vocabulario que el texto menciona (se devuelve el nombre canónico)."""
    base = normalizar(texto)
    vistos: set[str] = set()
    salida: list[str] = []
    for nombre in [*HERRAMIENTAS_COMUNES, *(extra or [])]:
        n = normalizar(nombre)
        if n in vistos or len(n) < 2:
            continue
        vistos.add(n)
        if contiene_termino(base, n):
            salida.append(nombre)
    return salida


def vocabulario_desde_puestos(puestos) -> list[str]:
    """Nombres de herramientas de la base de puestos (una por alternativa corta)."""
    nombres: list[str] = []
    for p in puestos:
        for item in p.herramientas:
            if es_generica(item):
                continue
            for alt in re.split(r",|/|;| o ", re.sub(r"\(.*?\)", " ", item)):
                alt = alt.strip()
                if 2 < len(alt) <= 30 and normalizar(alt) not in {normalizar(n) for n in nombres}:
                    nombres.append(alt)
    return nombres


def idiomas_en_texto(texto: str) -> list[str]:
    base = normalizar(texto)
    return [nombre.capitalize() for nombre, claves in IDIOMAS.items() if any(contiene_termino(base, c) for c in claves)]


def es_ruidosa(nombre: str) -> bool:
    """Palabras que pueden ser herramienta o palabra común; el verificador las trata con cuidado."""
    return normalizar(nombre) in _PALABRAS_SUELTAS_RUIDOSAS


# --------------------------------------------------------------------- dominios de experiencia
# Cada dominio agrupa términos que, para este rubro, cuentan como experiencia del mismo tipo
# (p. ej. campañas pagas en Meta Ads son experiencia en publicidad digital).
DOMINIOS: dict[str, list[str]] = {
    "publicidad digital": ["meta ads", "facebook ads", "instagram ads", "google ads", "tiktok ads", "linkedin ads",
                           "campañas pagas", "campana paga", "publicidad paga", "pauta", "pauta publicitaria",
                           "social ads", "sem", "performance", "publicidad digital", "paid media", "paid social",
                           "presupuesto publicitario", "inversion publicitaria", "publicidad", "adtech"],
    "marketing digital": ["marketing digital", "marketing", "growth", "email marketing", "mailing", "newsletter",
                          "embudo", "funnel", "conversion", "campañas", "campanas"],
    "redes sociales": ["redes sociales", "community manager", "community management", "social media", "instagram",
                       "tiktok", "facebook", "linkedin", "comunidad", "comunidades"],
    "contenidos": ["contenidos", "contenido", "copywriting", "redaccion", "redactor", "redactora", "seo", "blog",
                   "storytelling", "edicion", "correccion", "guion"],
    "comunicacion institucional": ["comunicacion institucional", "comunicacion corporativa", "prensa",
                                   "relaciones publicas", "relaciones institucionales", "gacetillas", "eventos"],
    "comunicacion interna": ["comunicacion interna", "cultura organizacional", "employee engagement"],
    "audiovisual": ["audiovisual", "video", "edicion de video", "reels", "fotografia", "produccion audiovisual",
                    "podcast", "youtube"],
    "diseno": ["diseno grafico", "diseno", "disenador", "disenadora", "direccion creativa", "creativo"],
    "periodismo": ["periodismo", "periodista", "produccion periodistica", "medios", "cronica", "noticias"],
}
# Un dominio específico cuenta también para su familia más amplia.
_FAMILIA = {"publicidad digital": {"marketing digital"}, "redes sociales": {"marketing digital"}}


def dominios_en_texto(texto: str) -> list[str]:
    """Dominios de comunicación que el texto menciona (por términos clave). Incluye la familia más amplia."""
    from servicios.texto import contiene_termino, normalizar  # import local: evita ciclos
    n = normalizar(texto)
    encontrados = [d for d, ts in DOMINIOS.items() if any(contiene_termino(n, t) for t in ts)]
    for d in list(encontrados):
        encontrados += [f for f in _FAMILIA.get(d, ()) if f not in encontrados]
    return list(dict.fromkeys(encontrados))


def terminos_de_dominio(texto: str, dominio: str) -> list[str]:
    """Términos de ese dominio que aparecen en el texto (para citarlos como pista)."""
    from servicios.texto import contiene_termino, normalizar
    n = normalizar(texto)
    return [t for t in DOMINIOS.get(dominio, []) if contiene_termino(n, t)][:4]


# --------------------------------------------------------------------- niveles de idioma
_NIVELES = [  # (patrón sobre texto normalizado, valor); más específicos primero
    (r"intermedio alto|intermedio/alto|upper intermediate", 2.5), (r"\bb2\b", 2.5), (r"\bb1\b", 2.0),
    (r"\ba1\b|\ba2\b|basico|elemental|principiante|inicial|beginner", 1.0),
    (r"intermedio|intermediate", 2.0),
    (r"\bc1\b|avanzado|advanced|alto", 3.0),
    (r"fluido|fluent|excelente|\bc2\b", 3.5),
    (r"bilingue|nativo|native|materno|bilingual", 4.0),
]
NOMBRE_NIVEL = {1.0: "básico", 2.0: "intermedio", 2.5: "intermedio alto", 3.0: "avanzado", 3.5: "fluido", 4.0: "nativo"}


def _niveles_en(fragmento: str) -> list[float]:
    from servicios.texto import normalizar
    n = normalizar(fragmento)
    if "intermedio avanzado" in n or "intermedio alto" in n:
        n = n.replace("intermedio avanzado", "intermedio alto")
    vistos = []
    for patron, valor in _NIVELES:
        if re.search(patron, n):
            vistos.append(valor)
            n = re.sub(patron, " ", n, count=1)
    return vistos


def nivel_idioma(texto: str, idioma: str, requerido: bool = False) -> float | None:
    """Nivel (1 básico … 4 nativo) que el texto declara para ese idioma, o None si no dice nivel.
    Si el texto ofrece alternativas («avanzado o bilingüe») para un requisito se toma la más baja (`requerido`);
    en un CV se toma la más alta."""
    from servicios.texto import normalizar
    claves = IDIOMAS.get(idioma.lower(), ())
    todas = [c for v in IDIOMAS.values() for c in v]
    hallados: list[float] = []
    for frag in re.split(r"[;\n|•·]|,\s|\.\s", texto):
        n = normalizar(frag)
        for c in claves:
            for m in re.finditer(rf"(?<![a-z0-9]){re.escape(c)}(?![a-z0-9])", n):
                despues = n[m.end():]
                corte = min([x.start() for t in todas for x in [re.search(rf"(?<![a-z0-9]){t}(?![a-z0-9])", despues)] if x] or [len(despues)])
                ventana = despues[:corte]
                niv = _niveles_en(ventana)
                if not niv:
                    previo = n[:m.start()]
                    ult = max([x.end() for t in todas for x in re.finditer(rf"(?<![a-z0-9]){t}(?![a-z0-9])", previo)] or [0])
                    niv = _niveles_en(previo[ult:])
                hallados += niv
    if not hallados:
        return None
    return min(hallados) if requerido else max(hallados)


# --------------------------------------------------------------------- categorías de herramientas
CATEGORIAS: dict[str, list[str]] = {
    "inteligencia artificial": ["chatgpt", "claude", "gemini", "copilot", "perplexity", "midjourney", "dall e", "runway"],
    "diseño": ["canva", "photoshop", "illustrator", "indesign", "figma", "adobe express", "adobe"],
    "edición de video": ["premiere", "premiere pro", "after effects", "capcut", "final cut pro"],
    "informática": ["excel", "word", "powerpoint", "google sheets", "google docs", "google drive", "microsoft 365"],
    "publicidad digital": ["meta ads", "facebook ads", "google ads", "linkedin ads", "tiktok ads"],
    "analítica": ["google analytics", "ga4", "looker studio", "search console"],
    "gestión de redes sociales": ["meta business suite", "hootsuite", "buffer", "metricool", "later"],
    "email marketing": ["mailchimp"],
    "CRM": ["hubspot", "salesforce", "crm"],
    "gestión de proyectos": ["notion", "trello", "asana", "slack"],
    "sitios web y tiendas online": ["wordpress", "wix", "shopify", "tienda nube"],
    "SEO": ["semrush", "ahrefs", "seo"],
    "automatización": ["zapier", "n8n", "make", "apps script"],
    "redes sociales": ["instagram", "facebook", "tiktok", "youtube", "linkedin", "twitter", "pinterest"],
}
# cómo se nombra cada categoría en un texto («herramientas de IA como…») -> categoría
ALIAS_CATEGORIA: dict[str, str] = {
    "ia": "inteligencia artificial", "inteligencia artificial": "inteligencia artificial", "ia generativa": "inteligencia artificial",
    "diseno": "diseño", "diseno grafico": "diseño", "edicion": "edición de video", "edicion de video": "edición de video",
    "ofimatica": "informática", "informatica": "informática", "oficina": "informática", "analitica": "analítica", "analisis de datos": "analítica",
    "metricas": "analítica", "publicidad": "publicidad digital", "publicidad digital": "publicidad digital",
    "publicidad paga": "publicidad digital", "ads": "publicidad digital", "email marketing": "email marketing",
    "gestion de proyectos": "gestión de proyectos", "gestion": "gestión de proyectos", "automatizacion": "automatización",
    "crm": "CRM", "seo": "SEO", "redes sociales": "redes sociales", "community management": "gestión de redes sociales",
}


def categoria_herramienta(nombre: str) -> str | None:
    n = normalizar(nombre)
    grupo = grupo_de(n) | {n}
    for cat, miembros in CATEGORIAS.items():
        if any(normalizar(m) in grupo for m in miembros):
            return cat
    return None


def herramientas_por_categoria(herramientas: list[str]) -> dict[str, list[str]]:
    salida: dict[str, list[str]] = {}
    for h in herramientas:
        cat = categoria_herramienta(h)
        if cat:
            salida.setdefault(cat, [])
            if h not in salida[cat]:
                salida[cat].append(h)
    return salida
