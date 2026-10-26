#!/usr/bin/env python3
"""servidor.py — sirve el juego y conecta a la jueza (Claude) con un RAG sobre leyes y el caso.

Uso:
    pip install anthropic
    export ANTHROPIC_API_KEY="tu-clave"     (opcional)
    python3 servidor.py

Si no hay clave, usa Ollama (gratis, local) si está encendido; si tampoco, funciona en "modo sin IA".
La clave NUNCA va en el navegador ni en GitHub: el servidor la lee del entorno.
"""
import json, math, os, pathlib, re, unicodedata, urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BASE = pathlib.Path(__file__).parent
MODELO = os.environ.get("MODELO_JUEZA", "claude-haiku-5-5")  # modelo económico; para más calidad: MODELO_JUEZA=claude-sonnet-5-5
RUBRICA = json.loads((BASE / "rubrica.json").read_text(encoding="utf-8"))
OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434")  # modelo local gratuito (el del curso)
BLOQUEADOS = ("/rubrica.json", "/servidor.py", "/corpus")  # lo que el navegador no necesita ver

# ---------------- RAG: búsqueda BM25 sobre los textos de corpus/ ----------------
PARADA = set("de la el en y a los las del que un una por con para es se al su sus lo como mas o pero si no ni ya fue son ser hay esta este esos esas entre sobre sin".split())

def tokens(texto):
    """Minúsculas, sin tildes ni palabras vacías, y con plurales simples."""
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return [w.rstrip("s") for w in re.findall(r"[a-z0-9]+", t) if w not in PARADA and len(w) > 2]

class Indice:
    def __init__(self, carpeta):
        self.trozos = []  # (documento, texto): un trozo por cada sección "## ..."
        for f in sorted(carpeta.glob("*.md")):
            for p in re.split(r"\n(?=## )", f.read_text(encoding="utf-8")):
                if len(p.strip()) > 40:
                    self.trozos.append((f.stem, p.strip()))
        self.docs = [tokens(p) for _, p in self.trozos]
        self.n = len(self.docs)
        self.prom = sum(map(len, self.docs)) / max(self.n, 1)
        self.df = {}
        for d in self.docs:
            for w in set(d):
                self.df[w] = self.df.get(w, 0) + 1

    def buscar(self, consulta, k=4):
        q, res = set(tokens(consulta)), []
        for i, d in enumerate(self.docs):
            s = 0.0
            for w in q:
                f = d.count(w)
                if f:
                    idf = math.log(1 + (self.n - self.df[w] + .5) / (self.df[w] + .5))
                    s += idf * f * 2.2 / (f + 1.2 * (.25 + .75 * len(d) / self.prom))
            res.append((s, i))
        return [self.trozos[i] for s, i in sorted(res, reverse=True)[:k] if s > 0]

INDICE = Indice(BASE / "corpus")

def rotular(trozos):
    """Lista legible del material consultado: 'documento: título de la sección'."""
    return [f"{doc}: {texto.splitlines()[0].lstrip('# ').strip()}" for doc, texto in trozos]

def contexto(trozos):
    return "\n\n".join(f"[{doc}]\n{texto}" for doc, texto in trozos) or "(no se recuperó material)"

# ---------------- La jueza: personalidad y reglas ----------------
SISTEMA = """Sos la jueza de un juzgado civil que resuelve el caso "Salomón contra los medios", en un juego educativo.
Personalidad: serena, formal y exigente. Hablás con "usted" y llamás "doctor/a" a quien la defiende. Valorás el fundamento
y la estrategia, no la simpatía. Sos imparcial: si el argumento es débil, lo decís con claridad y respeto.
Reglas:
1. Fundá lo que decís SOLO en el CONTEXTO recuperado. Si algo no surge de ese material, no lo afirmes ni inventes artículos, fallos, fechas o cifras.
2. Citá las fuentes entre corchetes con el nombre del documento, por ejemplo [03-codigo-civil].
3. No inventes declaraciones de personas reales ni hables en su nombre.
4. No uses las palabras "correcto" ni "incorrecto" y no anticipes la sentencia antes del final.
5. Respondé SIEMPRE con un único objeto JSON válido y nada más."""

def ollama_modelos():
    """Modelos instalados en Ollama (vacío si Ollama no está encendido)."""
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=2) as r:
            return [m["name"] for m in json.load(r).get("models", [])]
    except Exception:
        return []

def ollama_utiles():
    """Modelos de Ollama aptos para la jueza: se descartan los de personajes (Bob Esponja, etc.)."""
    return [m for m in ollama_modelos() if not re.search(r"bob|esponja", m, re.I)]

def proveedor():
    """Claude si hay clave; si no, Ollama (gratis y local) si hay un modelo apto; si no, None (modo sin IA)."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude"
    return "ollama" if (os.environ.get("OLLAMA_MODELO") or ollama_utiles()) else None

def modelo_ollama():
    return os.environ.get("OLLAMA_MODELO") or (ollama_utiles() or [""])[0]

def llamar_ollama(sistema, usuario, max_tokens=800):
    cuerpo = json.dumps({"model": modelo_ollama(), "stream": False, "format": "json",
                         "options": {"temperature": 0.3, "num_predict": max_tokens},
                         "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}]}).encode("utf-8")
    pedido = urllib.request.Request(OLLAMA + "/api/chat", data=cuerpo, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(pedido, timeout=240) as r:
        return json.load(r)["message"]["content"]

def llamar(sistema, usuario, max_tokens=800):
    return (llamar_claude if proveedor() == "claude" else llamar_ollama)(sistema, usuario, max_tokens)

def llamar_claude(sistema, usuario, max_tokens=800):
    import anthropic  # pip install anthropic
    cliente = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno
    r = cliente.messages.create(model=MODELO, max_tokens=max_tokens, system=sistema,
                                messages=[{"role": "user", "content": usuario}])
    return "".join(b.text for b in r.content if b.type == "text")

def extraer_json(t):
    return json.loads(t[t.index("{"): t.rindex("}") + 1])

usa_ia = lambda: proveedor() is not None
nombre_modelo = lambda: MODELO if proveedor() == "claude" else f"Ollama: {modelo_ollama()}"

# ---------------- Endpoints ----------------
def evaluar(d):
    """Valora el argumento del jugador en una pregunta y devuelve un comentario de la jueza."""
    R = RUBRICA[int(d.get("n", 0)) % len(RUBRICA)]
    respuesta = str(d.get("respuesta", ""))[:1200]
    ctx = INDICE.buscar(f"{R['tema']} {R['texto']} {respuesta}", 4)
    fuentes = rotular(ctx)
    if usa_ia():
        previo = "\n".join(f"- {h.get('tema')}: {str(h.get('respuesta'))[:250]} (puntos {h.get('puntos')})" for h in d.get("historial", [])[-7:]) or "(es la primera respuesta)"
        usuario = f"""PREGUNTA QUE USTED FORMULÓ: {R['texto']}
CRITERIO IDEAL (reservado, no lo cite textualmente): {R['ideal']}
RESPUESTAS ANTERIORES DEL LETRADO:\n{previo}
RESPUESTA ACTUAL DEL LETRADO: {respuesta}
CONTEXTO RECUPERADO:\n{contexto(ctx)}

Devuelva JSON: {{"comentario": "2 a 4 oraciones como jueza: qué fortalece y qué debilita el caso, con fuentes entre corchetes; si hay contradicción con respuestas anteriores, señálela", "puntos": 0, 1 o 2}}
Rúbrica de puntos: 2 = cubre lo esencial del criterio ideal con fundamento; 1 = lo cubre en parte o sin fundamento; 0 = ausente, errónea, afirma hechos falsos o ataca a las personas."""
        try:
            j = extraer_json(llamar(SISTEMA, usuario))
            return {"comentario": j["comentario"], "puntos": max(0, min(2, int(j["puntos"]))), "fuentes": fuentes, "modo": "ia"}
        except Exception as e:
            print("La IA falló, se usa el modo local:", e)
    ideal, mio = set(tokens(R["ideal"])), set(tokens(respuesta))
    cob = len(ideal & mio) / max(len(ideal), 1)
    p = 2 if cob >= .35 else 1 if cob >= .18 else 0
    intro = ("Su planteo cubre lo esencial. ", "Su planteo es incompleto. ", "Su planteo no alcanza a sostener el caso. ")[2 - p]
    return {"comentario": intro + R["explicacion"], "puntos": p, "fuentes": fuentes, "modo": "local"}

def sentencia(d):
    """Dicta la sentencia final considerando todas las respuestas del jugador."""
    h = d.get("historial", [])
    pct = round(100 * sum(int(x.get("puntos", 0)) for x in h) / max(2 * len(h), 1))
    ctx = INDICE.buscar(" ".join(str(x.get("respuesta", "")) for x in h)[:1500] + " intimidad libertad de expresion indemnizacion sentencia", 5)
    fuentes = rotular(ctx)
    if usa_ia() and h:
        hist = "\n".join(f"{i+1}. {x.get('tema')} (puntos {x.get('puntos')}/2)\n   Respuesta: {str(x.get('respuesta'))[:500]}\n   Su comentario: {x.get('comentario')}" for i, x in enumerate(h))
        usuario = f"""Es el momento de dictar sentencia. Solidez global de la defensa: {pct} %.
DESARROLLO DEL JUICIO:\n{hist}
CONTEXTO RECUPERADO:\n{contexto(ctx)}

Devuelva JSON: {{"resultado": "favorable" | "parcial" | "rechazada", "titulo": "título breve de la sentencia", "texto": "6 a 9 oraciones: fundamentos con fuentes entre corchetes, valoración de los argumentos de la defensa y si se hace lugar a la demanda en forma total, parcial o se rechaza", "consejo": "una oración sobre qué debería reforzar la defensa"}}
Guía: más de 75 % suele ser favorable, entre 40 y 75 % parcial y menos de 40 % rechazada, salvo que usted fundamente otra cosa."""
        try:
            j = extraer_json(llamar(SISTEMA, usuario, 1100))
            return {**j, "fuentes": fuentes, "modo": "ia"}
        except Exception as e:
            print("La IA falló, se usa el modo local:", e)
    r = "favorable" if pct >= 75 else "parcial" if pct >= 40 else "rechazada"
    textos = {"favorable": "Se hace lugar a la demanda: las emisiones invadieron la intimidad de la actora y de sus hijas sin consentimiento ni interés general [03-codigo-civil].",
              "parcial": "Se hace lugar parcialmente a la demanda: se reconoce parte del daño, pero la defensa no sostuvo con solidez todos los puntos [04-doctrina-libertad-de-expresion].",
              "rechazada": "Se rechaza la demanda: la defensa no logró fundar la responsabilidad de los demandados [04-doctrina-libertad-de-expresion]."}
    return {"resultado": r, "titulo": {"favorable": "Sentencia favorable", "parcial": "Sentencia parcial", "rechazada": "Demanda rechazada"}[r],
            "texto": textos[r] + f" Solidez global de la defensa: {pct} %. (Modo sin IA.)", "consejo": "Repase los puntos con menor puntaje y fundaméntelos en la ley.", "fuentes": fuentes, "modo": "local"}

RUTAS = {"/api/evaluar": evaluar, "/api/sentencia": sentencia}

class Manejador(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(BASE), **k)

    def responder(self, datos, codigo=200):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path == "/api/estado":
            return self.responder({"ia": usa_ia(), "modelo": nombre_modelo()})
        if self.path.startswith(BLOQUEADOS):
            return self.send_error(404)
        super().do_GET()

    def do_POST(self):
        if self.path not in RUTAS:
            return self.send_error(404)
        try:
            n = int(self.headers.get("Content-Length", 0))
            self.responder(RUTAS[self.path](json.loads(self.rfile.read(n) or b"{}")))
        except Exception as e:
            self.responder({"error": str(e)}, 500)

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 8000))
    print(f"Juego en http://localhost:{puerto}  |  Jueza: {'con IA (' + nombre_modelo() + ')' if usa_ia() else 'MODO SIN IA (sin clave de Claude y sin Ollama encendido)'}")
    ThreadingHTTPServer(("0.0.0.0", puerto), Manejador).serve_forever()
