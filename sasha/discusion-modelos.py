#!/usr/bin/env python3
"""Orquesta una discusión entre cinco personas construidas por lxs estudiantes.

Por qué existe este script
--------------------------
Cada estudiante del seminario construyó una persona con un ``Modelfile`` de
Ollama sobre la misma base (``qwen2.5:3b``). La única diferencia entre ellas es
el bloque ``SYSTEM``. Este script las hace debatir por turnos sobre un tema
común para que en clase se pueda leer el transcripto y preguntarse:
*¿se nota el ``SYSTEM`` que escribió cada quien en lo que dice su personaje?*

La segunda lección está en el modo de funcionamiento. En cada turno el modelo
recibe **toda la discusión acumulada**, no solamente el párrafo anterior. El
prompt crece monótonamente turno a turno, hasta que ya no entra en la ventana
de contexto (``num_ctx``) y la corrida se detiene sola. El informe final
muestra en qué turno pasó y con cuántos tokens: el modelo no "se cansó", se
quedó sin ventana de contexto.

Uso rápido
----------
    ollama serve                       # en otra terminal, si no está corriendo
    python3 sasha/discusion-modelos.py --dry-run
    python3 sasha/discusion-modelos.py --tema "IA en Educación" --seed 42

Convención de idioma
--------------------
Docstrings, mensajes de consola y salida Markdown: **español**.
Identificadores de código (variables, funciones, clases): **inglés**.

Dependencias: sólo biblioteca estándar de Python 3.12+. No hace falta instalar
nada más allá de Ollama.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Final

# ─────────────────────────────────────────────────────────────────────────────
#  EL ROSTER. Esto es lo único que hay que editar para cambiar quién participa:
#  agregar, sacar o reordenar entradas no requiere tocar nada de la lógica.
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Persona:
    """Una persona del debate: su tag en Ollama, su Modelfile y su autoría.

    Attributes:
        tag: Nombre con el que el modelo queda registrado en Ollama.
        modelfile: Ruta al Modelfile, **relativa a la raíz del repositorio**.
        display_name: Nombre legible del personaje, usado en el transcripto.
        student_folder: Carpeta de quien escribió el Modelfile (para dar crédito).
    """

    tag: str
    modelfile: str
    display_name: str
    student_folder: str


ROSTER: Final[list[Persona]] = [
    Persona(
        tag="unsam-pepeargento",
        modelfile="Dolores-Mujica/pepeargento-Modelfile",
        display_name="Pepe Argento",
        student_folder="Dolores-Mujica",
    ),
    Persona(
        tag="unsam-bugsbunny",
        modelfile="thiago/BugsBunny-Modelfile",
        display_name="Bugs Bunny",
        student_folder="thiago",
    ),
    Persona(
        tag="unsam-bobesponja",
        modelfile="BritezDiego/BobEsponja-modelfile",
        display_name="Bob Esponja",
        student_folder="BritezDiego",
    ),
    Persona(
        tag="unsam-batman",
        modelfile="rosario/batman-modelfile",
        display_name="Batman",
        student_folder="rosario",
    ),
    Persona(
        tag="unsam-estudiante",
        modelfile="Erika/estudiante_cansado.md",
        display_name="Estudiante cansado",
        student_folder="Erika",
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Constantes de infraestructura.
# ─────────────────────────────────────────────────────────────────────────────

#: Tema por defecto y su archivo de salida por defecto. Se los nombra juntos
#: porque el segundo es el nombre canónico del primero: si se cambia `--tema`,
#: el nombre del archivo pasa a derivarse con :func:`slugify`.
DEFAULT_TOPIC: Final[str] = "IA en Educación"
DEFAULT_OUTPUT: Final[str] = "sasha/discusion-IA-en-educacion.md"

OLLAMA_HOST: Final[str] = "http://localhost:11434"
GENERATE_URL: Final[str] = f"{OLLAMA_HOST}/api/generate"
TAGS_URL: Final[str] = f"{OLLAMA_HOST}/api/tags"

#: Raíz del repositorio: este archivo vive en ``<raíz>/sasha/``.
REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent

#: Segundos de espera para una generación. Un modelo de 3B en CPU puede tardar.
GENERATE_TIMEOUT_S: Final[int] = 300

#: Segundos de espera para ``ollama create``.
BUILD_TIMEOUT_S: Final[int] = 300

#: Segundos de espera para el chequeo de disponibilidad de Ollama.
PING_TIMEOUT_S: Final[int] = 10

#: Estimación inicial de caracteres por token en español antes de tener datos
#: reales. Se recalibra sola con el primer ``prompt_eval_count`` que devuelve
#: Ollama, así que el valor exacto no es crítico.
INITIAL_CHARS_PER_TOKEN: Final[float] = 3.6

#: Cuántos tokens reserva el estimador para la respuesta que todavía no existe.
RESPONSE_HEADROOM_TOKENS: Final[int] = 320

MESSAGE_OLLAMA_DOWN: Final[str] = (
    "\n[ERROR] No se pudo conectar con Ollama en "
    f"{OLLAMA_HOST}.\n"
    "        Ollama no está corriendo o está escuchando en otro puerto.\n"
    "        Abrí otra terminal y ejecutá:\n\n"
    "            ollama serve\n\n"
    "        Después volvé a correr este script.\n"
)

logger = logging.getLogger("discusion")


# ─────────────────────────────────────────────────────────────────────────────
#  Errores del dominio.
# ─────────────────────────────────────────────────────────────────────────────


class DiscussionError(Exception):
    """Error esperable de la corrida, con un mensaje ya legible en español."""


class OllamaUnavailableError(DiscussionError):
    """Ollama no responde en ``OLLAMA_HOST``."""


# ─────────────────────────────────────────────────────────────────────────────
#  Contabilidad de tokens.
# ─────────────────────────────────────────────────────────────────────────────


def system_overhead_tokens(persona: Persona) -> int:
    """Aproxima los tokens del bloque ``SYSTEM`` por el tamaño del Modelfile.

    Por qué: es la única estimación de la sobrecarga disponible **antes** de
    hablar con el modelo, y hace falta para descartar de entrada a una persona
    cuyo ``SYSTEM`` no entra en la ventana pedida. Después de su primer turno,
    :meth:`TokenEstimator.record` la reemplaza por el valor medido.
    """
    try:
        size = len((REPO_ROOT / persona.modelfile).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return 0
    return int(size / INITIAL_CHARS_PER_TOKEN)


@dataclass
class TokenEstimator:
    """Estima los tokens de un prompt como sobrecarga fija + texto variable.

    Por qué: para frenar **antes** de mandar un prompt que no entra hay que
    estimar su tamaño sin llamar al modelo, y Ollama no expone un tokenizador
    por HTTP. La trampa está en que ``prompt_eval_count`` no mide sólo el texto
    que manda este script: incluye el bloque ``SYSTEM`` del Modelfile, que en
    estas personas pesa entre 900 y 2.400 tokens. Estimar por caracteres del
    prompt visible subestima el arranque y descalibra cualquier ratio.

    Qué hace: modela los tokens del prompt como
    ``sobrecarga(persona) + len(texto) / CHARS_PER_TOKEN``. La sobrecarga
    arranca con un valor a priori derivado del tamaño del Modelfile y se
    reemplaza por el valor medido en cuanto esa persona habla por primera vez.

    Ojo: esto es una **estimación**, usada sólo como freno preventivo. El dato
    autoritativo es el ``prompt_eval_count`` que devuelve Ollama, y es el que
    manda en la tabla de consumo y en el corte medido.
    """

    #: tag de Ollama -> tokens de sobrecarga (a priori, o medidos).
    overheads: dict[str, int] = field(default_factory=dict)
    #: tags cuya sobrecarga ya fue medida contra Ollama.
    measured: set[str] = field(default_factory=set)

    @staticmethod
    def text_tokens(text: str) -> int:
        """Tokens estimados del texto visible del prompt."""
        return int(len(text) / INITIAL_CHARS_PER_TOKEN)

    def prime(self, persona: Persona) -> int:
        """Fija la sobrecarga a priori de ``persona`` a partir de su Modelfile.

        El Modelfile es casi todo bloque ``SYSTEM``, así que su tamaño en
        caracteres es una aproximación razonable antes de la primera medición.
        """
        if persona.tag not in self.overheads:
            self.overheads[persona.tag] = system_overhead_tokens(persona)
        return self.overheads[persona.tag]

    def overhead(self, persona: Persona) -> int:
        """Sobrecarga en tokens del ``SYSTEM`` de ``persona``."""
        return self.prime(persona)

    def project(self, persona: Persona, prompt: str) -> int:
        """Estima cuántos tokens de prompt va a contar Ollama para este turno."""
        return self.overhead(persona) + self.text_tokens(prompt)

    def record(self, persona: Persona, prompt: str, prompt_tokens: int) -> None:
        """Reemplaza la sobrecarga a priori por la medida realmente observada."""
        if prompt_tokens <= 0:
            return
        self.overheads[persona.tag] = max(0, prompt_tokens - self.text_tokens(prompt))
        self.measured.add(persona.tag)


@dataclass(frozen=True)
class TurnRecord:
    """Lo que pasó en un turno: quién habló, qué dijo y cuánto contexto costó.

    ``prompt_tokens`` es de por sí acumulativo: en modo contexto acumulado el
    prompt de cada turno contiene toda la discusión previa.
    """

    number: int
    persona: Persona
    text: str
    prompt_tokens: int
    response_tokens: int

    @property
    def total_tokens(self) -> int:
        """Tokens que el modelo tuvo en la ventana al terminar el turno."""
        return self.prompt_tokens + self.response_tokens


@dataclass(frozen=True)
class Termination:
    """Por qué terminó la corrida, en forma legible para el informe.

    Attributes:
        code: Etiqueta corta y estable (``contexto-proyectado``, ``max-turnos``…).
        headline: Frase de una línea para el bloque de metadatos.
        explanation: Párrafo didáctico para el cierre del Markdown.
    """

    code: str
    headline: str
    explanation: str


@dataclass
class BuildOutcome:
    """Resultado de construir el roster con ``ollama create``."""

    built: list[Persona] = field(default_factory=list)
    failures: list[tuple[Persona, str]] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
#  Utilidades de formato.
# ─────────────────────────────────────────────────────────────────────────────


def format_number(value: int) -> str:
    """Formatea un entero con punto como separador de miles (uso rioplatense).

    >>> format_number(3847)
    '3.847'
    """
    return f"{value:,}".replace(",", ".")


def slugify(text: str) -> str:
    """Convierte un texto a un fragmento apto para nombre de archivo."""
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n",
        "Á": "a", "É": "e", "Í": "i", "Ó": "o", "Ú": "u", "Ü": "u", "Ñ": "n",
    }
    lowered = "".join(replacements.get(char, char) for char in text).lower()
    kept = [char if char.isalnum() else "-" for char in lowered]
    slug = "".join(kept)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "discusion"


def resolve_path(raw: str) -> Path:
    """Resuelve una ruta: las relativas cuelgan de la raíz del repositorio.

    Por qué: así ``--salida sasha/algo.md`` significa lo mismo sin importar
    desde qué directorio se invoque el script.
    """
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        return candidate
    return (REPO_ROOT / candidate).resolve()


def one_paragraph(raw: str, display_name: str) -> str:
    """Aplana la respuesta del modelo a un único párrafo limpio.

    Por qué: el profesor pidió una entrada = un párrafo, y los modelos suelen
    devolver saltos de línea, viñetas o un prefijo con su propio nombre.
    Qué hace: junta las líneas en una sola, colapsa espacios y saca el prefijo
    ``Nombre:`` inicial si aparece.
    """
    flattened = " ".join(line.strip() for line in raw.strip().splitlines())
    flattened = " ".join(flattened.split())
    for prefix in (f"{display_name}:", f"[{display_name}]:", f"**{display_name}:**"):
        if flattened.lower().startswith(prefix.lower()):
            flattened = flattened[len(prefix):].strip()
    return flattened


# ─────────────────────────────────────────────────────────────────────────────
#  Capa Ollama.
# ─────────────────────────────────────────────────────────────────────────────


def ping_ollama() -> list[str]:
    """Verifica que Ollama responda y devuelve los tags ya instalados.

    Raises:
        OllamaUnavailableError: si no hay nadie escuchando o la respuesta no es
            un JSON válido.
    """
    request = urllib.request.Request(TAGS_URL, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=PING_TIMEOUT_S) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise OllamaUnavailableError(MESSAGE_OLLAMA_DOWN) from exc
    except (TimeoutError, OSError) as exc:
        raise OllamaUnavailableError(MESSAGE_OLLAMA_DOWN) from exc
    except json.JSONDecodeError as exc:
        raise OllamaUnavailableError(
            f"\n[ERROR] Ollama respondió algo que no es JSON en {TAGS_URL}: {exc}\n"
        ) from exc
    return [model.get("name", "") for model in payload.get("models", [])]


def generate(
    tag: str,
    prompt: str,
    *,
    num_ctx: int,
    temperature: float,
    seed: int | None = None,
) -> dict[str, object]:
    """Llama a ``POST /api/generate`` sin streaming y devuelve el JSON crudo.

    Qué interesa del JSON: ``response`` (el texto), ``prompt_eval_count``
    (tokens que ocupó el prompt) y ``eval_count`` (tokens generados). Esos dos
    contadores son la materia prima de la tabla de consumo de contexto.

    ``seed`` se reenvía a Ollama cuando no es ``None``. Sin eso, fijar la
    semilla del script haría reproducible el orden de los oradores pero no el
    texto que generan, y como el largo de cada respuesta decide cuándo se agota
    el contexto, la demo terminaría en un turno distinto en cada corrida.

    Raises:
        OllamaUnavailableError: si Ollama dejó de responder.
        DiscussionError: si Ollama devuelve un error HTTP o un JSON inválido.
    """
    options: dict[str, object] = {"num_ctx": num_ctx, "temperature": temperature}
    if seed is not None:
        options["seed"] = seed
    body = json.dumps(
        {"model": tag, "prompt": prompt, "stream": False, "options": options}
    ).encode("utf-8")
    request = urllib.request.Request(
        GENERATE_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=GENERATE_TIMEOUT_S) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise DiscussionError(
            f"Ollama rechazó la generación de '{tag}' "
            f"(HTTP {exc.code}): {detail}"
        ) from exc
    except urllib.error.URLError as exc:
        raise OllamaUnavailableError(MESSAGE_OLLAMA_DOWN) from exc
    except (TimeoutError, OSError) as exc:
        raise DiscussionError(
            f"Se agotó el tiempo de espera generando con '{tag}': {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DiscussionError(
            f"Ollama devolvió un JSON inválido para '{tag}': {exc}"
        ) from exc


def build_roster(personas: list[Persona]) -> BuildOutcome:
    """Construye cada persona con ``ollama create``, tolerando fallas parciales.

    Por qué tolerante: si el Modelfile de un estudiante tiene un error de
    sintaxis, la clase no debería quedarse sin demo. Se informa cuál falló, se
    lo saca del roster y la discusión sigue con el resto.

    Returns:
        Un :class:`BuildOutcome` con las personas construidas y las fallidas.
    """
    outcome = BuildOutcome()
    for persona in personas:
        path = REPO_ROOT / persona.modelfile
        print(f"  → construyendo {persona.tag} desde {persona.modelfile} …")
        try:
            completed = subprocess.run(
                ["ollama", "create", persona.tag, "-f", str(path)],
                capture_output=True,
                text=True,
                timeout=BUILD_TIMEOUT_S,
                check=False,
            )
        except FileNotFoundError:
            outcome.failures.append(
                (persona, "no se encontró el ejecutable 'ollama' en el PATH")
            )
            continue
        except subprocess.TimeoutExpired:
            outcome.failures.append(
                (persona, f"la construcción superó {BUILD_TIMEOUT_S} segundos")
            )
            continue

        if completed.returncode == 0:
            outcome.built.append(persona)
            print(f"    ✓ {persona.tag} listo")
        else:
            reason = (completed.stderr or completed.stdout or "").strip()
            reason = " ".join(reason.split())[:300] or "sin detalle de Ollama"
            outcome.failures.append((persona, reason))
            print(f"    ✗ {persona.tag} falló: {reason}", file=sys.stderr)
    return outcome


# ─────────────────────────────────────────────────────────────────────────────
#  Construcción del prompt.
# ─────────────────────────────────────────────────────────────────────────────


def build_prompt(topic: str, turns: list[TurnRecord], speaker: Persona) -> str:
    """Arma el prompt del turno: encuadre + discusión acumulada + consigna.

    Por qué acumulativo: es el modo elegido para la clase. El modelo recibe
    **toda** la discusión previa, no sólo el último párrafo, así que el prompt
    crece turno a turno y en algún momento agota ``num_ctx``. Ese agotamiento
    es exactamente lo que la demo quiere mostrar.
    """
    if turns:
        transcript = "\n\n".join(
            f"[{turn.persona.display_name}]: {turn.text}" for turn in turns
        )
        transcript_block = (
            "=== DISCUSIÓN HASTA AHORA ===\n"
            f"{transcript}\n"
            "=== FIN DE LA DISCUSIÓN ===\n"
        )
        instruction = (
            "reaccionando a lo que dijeron los demás (nombralos si querés, "
            "acordá o discutí con ellos)"
        )
    else:
        transcript_block = (
            "=== DISCUSIÓN HASTA AHORA ===\n"
            "(Todavía no habló nadie. Abrís vos el debate.)\n"
            "=== FIN DE LA DISCUSIÓN ===\n"
        )
        instruction = "abriendo el debate con tu postura"

    return (
        "Estás participando en una mesa de debate junto a otros personajes.\n"
        f'El tema del debate es: "{topic}".\n\n'
        f"{transcript_block}\n"
        f"Ahora te toca hablar a vos, {speaker.display_name}.\n"
        "Consignas para tu intervención:\n"
        f"- Respondé {instruction}.\n"
        "- Escribí UN SOLO PÁRRAFO, sin títulos, sin viñetas y sin saltos de línea.\n"
        "- Mantenete siempre en personaje.\n"
        "- Escribí en español rioplatense, usando voseo (vos, tenés, decís).\n"
        "- No repitas literalmente lo que ya dijeron los demás.\n"
        "- No escribas tu propio nombre al principio.\n"
    )


def pick_speaker(
    personas: list[Persona], previous: Persona | None, rng: random.Random
) -> Persona:
    """Elige al azar quién habla, prohibiendo repetir al orador anterior."""
    candidates = [p for p in personas if p is not previous] or personas
    return rng.choice(candidates)


# ─────────────────────────────────────────────────────────────────────────────
#  Render del Markdown.
# ─────────────────────────────────────────────────────────────────────────────


def render_markdown(
    *,
    topic: str,
    personas: list[Persona],
    failures: list[tuple[Persona, str]],
    turns: list[TurnRecord],
    termination: Termination | None,
    num_ctx: int,
    seed: int | None,
    base_model: str,
    temperature: float,
    started_at: datetime,
) -> str:
    """Genera el transcripto completo en Markdown.

    Se reconstruye entero después de cada turno y se reescribe el archivo, de
    modo que un Ctrl-C deja igual un documento válido y legible.
    """
    lines: list[str] = [f"# Discusión: {topic}", ""]

    # ── Metadatos ────────────────────────────────────────────────────────────
    lines += ["## Datos de la corrida", ""]
    lines += ["| Parámetro | Valor |", "| --- | --- |"]
    lines.append(f"| Fecha | {started_at.strftime('%Y-%m-%d %H:%M:%S')} |")
    lines.append(f"| Tema | {topic} |")
    lines.append(f"| Modelo base | `{base_model}` |")
    lines.append(f"| `num_ctx` | {format_number(num_ctx)} tokens |")
    lines.append(f"| `temperature` | {temperature} |")
    lines.append(f"| Semilla (`--seed`) | {seed if seed is not None else 'sin semilla'} |")
    lines.append(f"| Turnos generados | {len(turns)} |")
    lines.append(
        f"| Motivo de finalización | {termination.headline if termination else 'en curso'} |"
    )
    lines.append("")
    if seed is not None:
        lines += [
            f"> La semilla {seed} fija el orden de los oradores de forma exacta y se "
            "le reenvía a Ollama, pero Ollama no garantiza texto idéntico entre "
            "corridas: la primera llamada después de cargar un modelo suele diferir "
            "de las siguientes. Como el largo de cada respuesta decide cuándo se "
            "llena la ventana, el turno final puede moverse de una corrida a otra.",
            "",
        ]

    lines += ["## Participantes", ""]
    lines += [
        "| Personaje | Modelo en Ollama | Modelfile | Estudiante |",
        "| --- | --- | --- | --- |",
    ]
    for persona in personas:
        lines.append(
            f"| {persona.display_name} | `{persona.tag}` | "
            f"`{persona.modelfile}` | {persona.student_folder} |"
        )
    lines.append("")

    if failures:
        lines += ["### Personas que quedaron afuera", ""]
        for persona, reason in failures:
            lines.append(
                f"- **{persona.display_name}** (`{persona.tag}`, "
                f"carpeta `{persona.student_folder}`): {reason}"
            )
        lines.append("")

    # ── La discusión ─────────────────────────────────────────────────────────
    lines += ["## La discusión", ""]
    if not turns:
        lines += ["_No se generó ningún turno._", ""]
    for turn in turns:
        lines.append(f"### {turn.number}. {turn.persona.display_name}")
        lines.append("")
        lines.append(turn.text)
        lines.append("")

    # ── Consumo de contexto ──────────────────────────────────────────────────
    lines += ["## Consumo de contexto", ""]
    lines += [
        "Cada fila es un turno. El **prompt** ya es acumulativo: en este modo, "
        "cada personaje recibe toda la discusión previa, así que la columna "
        "crece sola. La última columna muestra qué porcentaje de la ventana "
        f"(`num_ctx` = {format_number(num_ctx)}) quedó ocupado al terminar el turno.",
        "",
    ]
    lines += [
        "| Turno | Personaje | Prompt (tokens) | Respuesta (tokens) | "
        "Acumulado en la ventana | % de `num_ctx` |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for turn in turns:
        percentage = (turn.total_tokens / num_ctx * 100) if num_ctx else 0.0
        lines.append(
            f"| {turn.number} | {turn.persona.display_name} "
            f"| {format_number(turn.prompt_tokens)} "
            f"| {format_number(turn.response_tokens)} "
            f"| {format_number(turn.total_tokens)} "
            f"| {percentage:.1f} % |"
        )
    lines.append("")

    # ── Cierre didáctico ─────────────────────────────────────────────────────
    lines += ["## Por qué se detuvo la discusión", ""]
    if termination is not None:
        lines += [termination.explanation, ""]
    else:
        lines += ["_La corrida todavía no terminó._", ""]

    return "\n".join(lines)


def flush_markdown(path: Path, content: str) -> None:
    """Escribe el transcripto en disco en UTF-8, creando el directorio si falta."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
#  Motivos de finalización.
# ─────────────────────────────────────────────────────────────────────────────


#: El párrafo didáctico que cierra cualquier final por agotamiento de contexto.
#: Vive aparte porque lo comparten el corte proyectado, el medido y el truncado.
CONTEXT_LESSON: Final[str] = (
    "Conviene subrayarlo en clase: el modelo no se aburrió ni se cansó. En este "
    "modo cada turno recibe **toda** la discusión anterior, así que el prompt "
    "crece sin parar mientras la ventana de contexto sigue midiendo lo mismo. A "
    "eso hay que sumarle el bloque `SYSTEM` de cada personaje, que se paga "
    "entero en cada llamada y nunca se achica. Cuando lo que hay que leer no "
    "entra en la ventana, no queda lugar para un turno más: o se corta el "
    "principio de la conversación, o se frena. Este script frena a propósito, "
    "para que el límite se vea. Subir `--num-ctx` corre el límite más lejos, "
    "pero no lo elimina, y cuesta memoria."
)


def context_termination(
    *, turn_number: int, tokens: int, num_ctx: int, threshold: float, projected: bool
) -> Termination:
    """Arma el motivo de finalización por agotamiento de la ventana de contexto."""
    limit = int(num_ctx * threshold)
    kind = "proyectado" if projected else "medido"
    return Termination(
        code="contexto-proyectado" if projected else "contexto-medido",
        headline=(
            f"ventana de contexto agotada en el turno {turn_number} "
            f"({format_number(tokens)}/{format_number(num_ctx)} tokens)"
        ),
        explanation=(
            f"La discusión se detuvo en el turno {turn_number} porque el prompt "
            f"acumulado ({kind}) alcanzó {format_number(tokens)} tokens sobre un "
            f"`num_ctx` de {format_number(num_ctx)}, superando el umbral de "
            f"seguridad del {threshold:.0%} ({format_number(limit)} tokens).\n\n"
            f"{CONTEXT_LESSON}"
        ),
    )


TERMINATION_INTERRUPTED: Final[Termination] = Termination(
    code="interrumpido",
    headline="interrumpido a mano (Ctrl-C)",
    explanation=(
        "La corrida se interrumpió con Ctrl-C antes de agotar la ventana de "
        "contexto. El transcripto de arriba está completo hasta el último turno "
        "que sí llegó a generarse."
    ),
)


def max_turns_termination(max_turns: int) -> Termination:
    """Motivo de finalización por alcanzar el tope de turnos."""
    return Termination(
        code="max-turnos",
        headline=f"se alcanzó el tope de {max_turns} turnos",
        explanation=(
            f"La discusión llegó al tope de `--max-turns` ({max_turns}) sin agotar "
            "la ventana de contexto. Para ver el agotamiento de contexto en vivo, "
            "corré de nuevo con un `--num-ctx` más chico (por ejemplo 2048) o con "
            "un `--max-turns` más alto."
        ),
    )


def error_termination(message: str) -> Termination:
    """Motivo de finalización por un error de la corrida."""
    return Termination(
        code="error",
        headline="la corrida se cortó por un error",
        explanation=(
            "La discusión se cortó por un error, no por agotamiento de contexto: "
            f"{message}"
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  El bucle principal de la discusión.
# ─────────────────────────────────────────────────────────────────────────────


def run_discussion(
    *,
    personas: list[Persona],
    failures: list[tuple[Persona, str]],
    args: argparse.Namespace,
    output_path: Path,
    started_at: datetime,
) -> tuple[list[TurnRecord], Termination]:
    """Corre la discusión turno a turno hasta agotar contexto, turnos o paciencia.

    Cada turno: elige orador (distinto del anterior), estima si el prompt entra,
    llama al modelo, guarda la respuesta y reescribe el Markdown en disco. El
    volcado por turno es lo que hace que un Ctrl-C deje un archivo usable.

    Returns:
        La lista de turnos generados y el motivo por el que se terminó.
    """
    rng = random.Random(args.seed)
    estimator = TokenEstimator()
    turns: list[TurnRecord] = []
    previous: Persona | None = None
    termination: Termination | None = None

    def snapshot(current: Termination | None) -> None:
        """Vuelca el estado actual a disco."""
        flush_markdown(
            output_path,
            render_markdown(
                topic=args.tema,
                personas=personas,
                failures=failures,
                turns=turns,
                termination=current,
                num_ctx=args.num_ctx,
                seed=args.seed,
                base_model=args.modelo_base,
                temperature=args.temperature,
                started_at=started_at,
            ),
        )

    try:
        for turn_number in range(1, args.max_turns + 1):
            speaker = pick_speaker(personas, previous, rng)
            prompt = build_prompt(args.tema, turns, speaker)

            # Freno preventivo: ¿entra el prompt más un margen para la respuesta?
            projected = estimator.project(speaker, prompt) + RESPONSE_HEADROOM_TOKENS
            budget = int(args.num_ctx * args.context_threshold)
            logger.debug(
                "turno %d: %s, prompt estimado %d tokens (presupuesto %d)",
                turn_number, speaker.display_name, projected, budget,
            )
            if projected > budget:
                termination = context_termination(
                    turn_number=turn_number,
                    tokens=projected,
                    num_ctx=args.num_ctx,
                    threshold=args.context_threshold,
                    projected=True,
                )
                break

            print(f"[turno {turn_number}] {speaker.display_name} está pensando …")
            payload = generate(
                speaker.tag,
                prompt,
                num_ctx=args.num_ctx,
                temperature=args.temperature,
                # Semilla distinta por turno: reproducible entre corridas, pero
                # sin correlacionar un turno con el siguiente.
                seed=None if args.seed is None else args.seed + turn_number,
            )

            prompt_tokens = int(payload.get("prompt_eval_count") or 0)
            response_tokens = int(payload.get("eval_count") or 0)
            estimator.record(speaker, prompt, prompt_tokens)

            text = one_paragraph(str(payload.get("response", "")), speaker.display_name)
            if not text:
                logger.warning(
                    "turno %d: %s devolvió una respuesta vacía; se descarta el turno",
                    turn_number, speaker.tag,
                )
                previous = speaker
                continue

            turns.append(
                TurnRecord(
                    number=len(turns) + 1,
                    persona=speaker,
                    text=text,
                    prompt_tokens=prompt_tokens,
                    response_tokens=response_tokens,
                )
            )
            previous = speaker
            snapshot(None)

            used = prompt_tokens + response_tokens
            print(
                f"    {format_number(prompt_tokens)} tokens de prompt + "
                f"{format_number(response_tokens)} de respuesta "
                f"= {used / args.num_ctx:.0%} de la ventana"
            )

            # Freno medido: lo que Ollama realmente contó ya roza el límite. Si
            # prompt_eval_count llegó o pasó num_ctx, Ollama truncó el prompt y
            # la discusión ya perdió su principio.
            if prompt_tokens >= args.num_ctx:
                termination = context_termination(
                    turn_number=turn_number,
                    tokens=prompt_tokens,
                    num_ctx=args.num_ctx,
                    threshold=args.context_threshold,
                    projected=False,
                )
                termination = Termination(
                    code="contexto-truncado",
                    headline=termination.headline,
                    explanation=(
                        f"En el turno {turn_number} Ollama informó "
                        f"{format_number(prompt_tokens)} tokens de prompt contra un "
                        f"`num_ctx` de {format_number(args.num_ctx)}: el prompt ya no "
                        "entraba y fue truncado, es decir que el modelo dejó de ver "
                        f"el comienzo de la discusión.\n\n{CONTEXT_LESSON}"
                    ),
                )
                break
            if used > budget:
                termination = context_termination(
                    turn_number=turn_number,
                    tokens=used,
                    num_ctx=args.num_ctx,
                    threshold=args.context_threshold,
                    projected=False,
                )
                break
        else:
            termination = max_turns_termination(args.max_turns)

    except KeyboardInterrupt:
        print("\n[aviso] Interrumpido a mano. Guardando lo que haya …", file=sys.stderr)
        termination = TERMINATION_INTERRUPTED
    except DiscussionError as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        termination = error_termination(str(exc))

    if termination is None:  # pragma: no cover - red de seguridad
        termination = max_turns_termination(args.max_turns)

    snapshot(termination)
    return turns, termination


# ─────────────────────────────────────────────────────────────────────────────
#  Validación previa y modo --dry-run.
# ─────────────────────────────────────────────────────────────────────────────


def validate_modelfiles(personas: list[Persona]) -> list[tuple[Persona, str]]:
    """Comprueba que cada Modelfile exista y se pueda leer.

    Returns:
        Lista de ``(persona, motivo)`` por cada Modelfile que no sirve. Vacía si
        están todos bien.
    """
    problems: list[tuple[Persona, str]] = []
    for persona in personas:
        path = REPO_ROOT / persona.modelfile
        if not path.is_file():
            problems.append((persona, f"no existe el archivo {path}"))
            continue
        try:
            path.read_text(encoding="utf-8")
        except OSError as exc:
            problems.append((persona, f"no se pudo leer {path}: {exc}"))
        except UnicodeDecodeError as exc:
            problems.append((persona, f"{path} no es UTF-8 válido: {exc}"))
    return problems


def filter_by_context(
    personas: list[Persona], num_ctx: int, threshold: float
) -> tuple[list[Persona], list[tuple[Persona, str]]]:
    """Descarta las personas cuyo ``SYSTEM`` no entra en la ventana pedida.

    Por qué: el bloque ``SYSTEM`` de estas personas pesa entre 900 y 2.400
    tokens y se cobra **en cada** llamada, antes de cualquier texto de la
    discusión. Con un ``num_ctx`` chico hay personas que directamente no pueden
    hablar: Ollama truncaría su propio ``SYSTEM`` y el personaje se perdería.
    Es preferible avisarlo y dejarla afuera que generar en silencio un
    personaje mutilado.

    Returns:
        Las personas que sí entran y la lista de ``(persona, motivo)`` de las
        descartadas.
    """
    budget = int(num_ctx * threshold)
    keep: list[Persona] = []
    dropped: list[tuple[Persona, str]] = []
    for persona in personas:
        overhead = system_overhead_tokens(persona)
        if overhead + RESPONSE_HEADROOM_TOKENS >= budget:
            dropped.append(
                (
                    persona,
                    f"su bloque SYSTEM ocupa unos {format_number(overhead)} tokens y "
                    f"no entra en un num_ctx de {format_number(num_ctx)} "
                    f"(presupuesto útil: {format_number(budget)} tokens). "
                    "Subí --num-ctx para que pueda participar.",
                )
            )
        else:
            keep.append(persona)
    return keep, dropped


def print_plan(
    args: argparse.Namespace,
    personas: list[Persona],
    output_path: Path,
    installed_tags: list[str],
) -> None:
    """Imprime el plan de la corrida sin ejecutar nada."""
    print("\n=== PLAN DE LA CORRIDA (dry-run: no se construye ni se genera nada) ===\n")
    print(f"  Tema            : {args.tema}")
    print(f"  Modelo base     : {args.modelo_base}")
    print(f"  num_ctx         : {format_number(args.num_ctx)} tokens")
    print(f"  Umbral de corte : {args.context_threshold:.0%} "
          f"({format_number(int(args.num_ctx * args.context_threshold))} tokens)")
    print(f"  Máx. de turnos  : {args.max_turns}")
    print(f"  Temperature     : {args.temperature}")
    print(f"  Semilla         : {args.seed if args.seed is not None else 'sin semilla'}")
    print(f"  Salida          : {output_path}")
    print(f"  Ollama          : {OLLAMA_HOST} (accesible)")
    print(f"\n  Personas a construir ({len(personas)}):\n")
    for index, persona in enumerate(personas, start=1):
        already = "ya instalado" if any(
            tag.split(":")[0] == persona.tag for tag in installed_tags
        ) else "se construirá"
        print(f"    {index}. {persona.display_name}")
        print(f"       tag        : {persona.tag}  ({already})")
        print(f"       modelfile  : {persona.modelfile}  (legible)")
        print(f"       estudiante : {persona.student_folder}")
        overhead = system_overhead_tokens(persona)
        print(
            f"       SYSTEM     : ~{format_number(overhead)} tokens fijos por turno "
            f"({overhead / args.num_ctx:.0%} de la ventana)"
        )
    print("\n  Modo: contexto acumulado — cada turno recibe toda la discusión previa.")
    print("  La corrida se detendrá al agotar la ventana de contexto o al llegar")
    print("  al tope de turnos, lo que pase primero.\n")
    print("=== Todo listo. Sacá --dry-run para correrlo de verdad. ===\n")


# ─────────────────────────────────────────────────────────────────────────────
#  CLI.
# ─────────────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos, con ayuda en español."""
    parser = argparse.ArgumentParser(
        prog="discusion-modelos.py",
        description=(
            "Hace discutir por turnos a cinco personas de Ollama construidas por "
            "lxs estudiantes y guarda el transcripto en Markdown. Cada turno "
            "recibe toda la discusión acumulada, así que el prompt crece hasta "
            "agotar la ventana de contexto: esa es la demostración."
        ),
        epilog=(
            "Ejemplos:\n"
            "  python3 sasha/discusion-modelos.py --dry-run\n"
            "  python3 sasha/discusion-modelos.py --seed 42 --num-ctx 2048\n"
            '  python3 sasha/discusion-modelos.py --tema "Sesgos algorítmicos"\n'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--tema",
        default=DEFAULT_TOPIC,
        help="Tema del debate (por defecto: %(default)s).",
    )
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=4096,
        help=(
            "Ventana de contexto en tokens que se le impone a cada modelo. "
            "Cuanto más chica, antes se agota y antes termina la demo "
            "(por defecto: %(default)s)."
        ),
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=50,
        help="Tope duro de turnos, como red de seguridad (por defecto: %(default)s).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help=(
            "Semilla del sorteo de turnos, que además se le reenvía a Ollama. "
            "Fija de forma exacta el orden de los oradores y acerca mucho el "
            "texto entre corridas. Ojo: Ollama no garantiza salidas idénticas "
            "(la primera llamada después de cargar un modelo suele diferir de "
            "las siguientes), así que el turno en el que se agota el contexto "
            "puede variar (por defecto: sin semilla)."
        ),
    )
    parser.add_argument(
        "--salida",
        "--output",
        dest="salida",
        default=None,
        help=(
            "Archivo Markdown de salida. Las rutas relativas cuelgan de la raíz "
            f"del repositorio (por defecto: {DEFAULT_OUTPUT}, o "
            "sasha/discusion-<tema>.md si cambiás --tema)."
        ),
    )
    parser.add_argument(
        "--modelo-base",
        default="qwen2.5:3b",
        help=(
            "Modelo base del que salen todas las personas. Es informativo: sirve "
            "para el encabezado del informe (por defecto: %(default)s)."
        ),
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.8,
        help="Temperatura de generación (por defecto: %(default)s).",
    )
    parser.add_argument(
        "--context-threshold",
        type=float,
        default=0.9,
        help=(
            "Fracción de num_ctx que se puede ocupar antes de frenar "
            "(por defecto: %(default)s, o sea el 90%%)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Valida todo (Modelfiles legibles, Ollama accesible) e imprime el "
            "plan, sin construir modelos ni generar texto."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra detalle de diagnóstico por consola.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada. Devuelve el código de salida del proceso."""
    args = build_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="[%(levelname)s] %(message)s",
        stream=sys.stderr,
    )

    if args.num_ctx < 256:
        print("[ERROR] --num-ctx tiene que ser al menos 256 tokens.", file=sys.stderr)
        return 2
    if args.max_turns < 1:
        print("[ERROR] --max-turns tiene que ser al menos 1.", file=sys.stderr)
        return 2
    if not 0.1 <= args.context_threshold <= 1.0:
        print(
            "[ERROR] --context-threshold tiene que estar entre 0.1 y 1.0.",
            file=sys.stderr,
        )
        return 2

    if args.salida:
        raw_output = args.salida
    elif args.tema == DEFAULT_TOPIC:
        raw_output = DEFAULT_OUTPUT
    else:
        raw_output = f"sasha/discusion-{slugify(args.tema)}.md"
    output_path = resolve_path(raw_output)

    # ── Validación de los Modelfiles ─────────────────────────────────────────
    problems = validate_modelfiles(ROSTER)
    usable = [p for p in ROSTER if p not in {bad for bad, _ in problems}]
    for persona, reason in problems:
        print(
            f"[aviso] {persona.display_name} ({persona.tag}): {reason}",
            file=sys.stderr,
        )
    if len(usable) < 2:
        print(
            "\n[ERROR] Quedan menos de 2 personas con Modelfile válido: no hay "
            "discusión posible. Revisá las rutas del roster.",
            file=sys.stderr,
        )
        return 1

    # ── ¿Entra el SYSTEM de cada persona en la ventana pedida? ───────────────
    usable, too_big = filter_by_context(usable, args.num_ctx, args.context_threshold)
    for persona, reason in too_big:
        print(f"[aviso] {persona.display_name} queda afuera: {reason}", file=sys.stderr)
    problems += too_big
    if len(usable) < 2:
        print(
            f"\n[ERROR] Con --num-ctx {args.num_ctx} quedan menos de 2 personas que "
            "entren en la ventana de contexto. Subí --num-ctx y volvé a intentar.",
            file=sys.stderr,
        )
        return 1

    # ── Ollama tiene que estar arriba ────────────────────────────────────────
    try:
        installed_tags = ping_ollama()
    except OllamaUnavailableError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.dry_run:
        print_plan(args, usable, output_path, installed_tags)
        return 0

    # ── Construcción de las personas ─────────────────────────────────────────
    print(f"\n=== Construyendo {len(usable)} personas en Ollama ===\n")
    outcome = build_roster(usable)
    failures = [(persona, reason) for persona, reason in problems]
    failures += outcome.failures

    if len(outcome.built) < 2:
        print(
            f"\n[ERROR] Sólo se construyeron {len(outcome.built)} personas y hacen "
            "falta al menos 2 para que haya discusión. Revisá los Modelfiles que "
            "fallaron más arriba.",
            file=sys.stderr,
        )
        return 1
    if outcome.failures:
        print(
            f"\n[aviso] Se sigue con {len(outcome.built)} personas; "
            f"{len(outcome.failures)} quedaron afuera.",
            file=sys.stderr,
        )

    # ── La discusión ─────────────────────────────────────────────────────────
    started_at = datetime.now()
    print(f'\n=== Discusión sobre "{args.tema}" ===\n')
    turns, termination = run_discussion(
        personas=outcome.built,
        failures=failures,
        args=args,
        output_path=output_path,
        started_at=started_at,
    )

    print(f"\n=== Fin: {termination.headline} ===")
    print(f"Turnos generados : {len(turns)}")
    print(f"Transcripto      : {output_path}")
    return 0 if termination.code != "error" else 1


if __name__ == "__main__":
    sys.exit(main())
