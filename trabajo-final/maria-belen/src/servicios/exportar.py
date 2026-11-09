"""Exportar el CV o la carta a un .docx sin dependencias extra (solo la biblioteca estándar).

Entiende el Markdown básico que genera el modelo: títulos (#), viñetas (- o *) y **negrita**.
"""
from __future__ import annotations

import io
import re
import zipfile
from xml.sax.saxutils import escape

_CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                  '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                  '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                  '<Default Extension="xml" ContentType="application/xml"/>'
                  '<Override PartName="/word/document.xml" '
                  'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                  '</Types>')
_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
         'Target="word/document.xml"/></Relationships>')
_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def _run(texto: str, negrita: bool = False, tamano: int | None = None) -> str:
    props = ("<w:b/>" if negrita else "") + (f'<w:sz w:val="{tamano}"/>' if tamano else "")
    pr = f"<w:rPr>{props}</w:rPr>" if props else ""
    return f'<w:r>{pr}<w:t xml:space="preserve">{escape(texto)}</w:t></w:r>'


def _runs_inline(texto: str, negrita_base: bool = False, tamano: int | None = None) -> str:
    partes = re.split(r"(\*\*[^*]+\*\*)", texto)
    salida = []
    for p in partes:
        if not p:
            continue
        if p.startswith("**") and p.endswith("**") and len(p) > 4:
            salida.append(_run(p[2:-2], True, tamano))
        else:
            salida.append(_run(p.replace("*", ""), negrita_base, tamano))
    return "".join(salida)


def _parrafo(texto: str) -> str:
    t = texto.rstrip()
    if not t.strip():
        return "<w:p/>"
    m = re.match(r"^(#{1,6})\s+(.*)$", t)
    if m:
        tam = {1: 36, 2: 30, 3: 26}.get(len(m.group(1)), 24)
        return f"<w:p>{_runs_inline(m.group(2), True, tam)}</w:p>"
    m = re.match(r"^\s*[-*+]\s+(.*)$", t)
    if m:
        return f'<w:p><w:pPr><w:ind w:left="360" w:hanging="240"/></w:pPr>{_run("• ")}{_runs_inline(m.group(1))}</w:p>'
    return f"<w:p>{_runs_inline(t.strip())}</w:p>"


def a_docx(texto: str) -> bytes:
    cuerpo = "".join(_parrafo(l) for l in texto.replace("\r\n", "\n").split("\n"))
    documento = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {_NS}><w:body>{cuerpo}'
                 '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" '
                 'w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr></w:body></w:document>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CONTENT_TYPES)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("word/document.xml", documento)
    return buf.getvalue()
