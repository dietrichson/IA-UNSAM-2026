import pytest

from servicios.config import cargar_config
from servicios.llm_client import (ContextoExcedido, LLMClient, LLMError, ModeloNoDisponible, SalidaInvalida,
                                  extraer_json)
from servicios.schemas import CVEstructurado, Criterio, OfertaEstructurada


def cliente(url, **extra):
    return LLMClient(cargar_config({"OLLAMA_URL": url, **extra}))


# ---------- config
def test_config_por_defecto():
    c = cargar_config({})
    assert (c.provider, c.modelo_principal, c.modelo_embeddings, c.num_ctx) == ("ollama", "qwen2.5:3b", "bge-m3", 4096)
    assert c.es_local


def test_config_proveedor_invalido():
    with pytest.raises(ValueError):
        cargar_config({"LLM_PROVIDER": "otro"})


def test_config_claude_usa_embeddings_locales():
    c = cargar_config({"LLM_PROVIDER": "claude"})
    assert c.embeddings_provider == "ollama" and not c.es_local


# ---------- extraer_json y esquemas
def test_extraer_json_con_vallas_y_texto():
    assert extraer_json('Acá va:\n```json\n{"a": 1}\n```\nlisto') == '{"a": 1}'
    assert extraer_json('texto {"a": {"b": 2}} fin') == '{"a": {"b": 2}}'


def test_esquema_corrige_errores_tipicos():
    cv = CVEstructurado.model_validate({"herramientas": "Canva", "idiomas": None, "anios_experiencia": "2,5 años",
                                        "experiencias": [{"puesto": "Redactora", "logros": None}], "extra": 1})
    assert cv.herramientas == ["Canva"] and cv.idiomas == [] and cv.anios_experiencia == 2.5
    assert cv.experiencias[0].logros == []
    assert OfertaEstructurada.model_validate({"titulo": None}).titulo == ""


def test_criterio_acota_puntaje():
    assert Criterio.model_validate({"puntaje": 250}).puntaje == 100
    assert Criterio.model_validate({"puntaje": "80.4"}).puntaje == 80
    assert Criterio.model_validate({"puntaje": "mucho"}).puntaje == 0


# ---------- cliente contra el Ollama falso
def test_chat_json_ok_y_envia_esquema(ollama_falso):
    ollama_falso.respuestas = ['{"titulo": "Community Manager", "herramientas": ["Canva"]}']
    r = cliente(ollama_falso.url).chat_json("sistema", "usuario", OfertaEstructurada)
    assert r.titulo == "Community Manager" and r.herramientas == ["Canva"]
    pedido = ollama_falso.pedidos[0]
    assert pedido["model"] == "qwen2.5:3b" and pedido["stream"] is False
    assert pedido["format"]["type"] == "object" and pedido["options"]["num_ctx"] == 4096


def test_chat_json_reintenta_una_vez(ollama_falso):
    ollama_falso.respuestas = ["no es json", '{"titulo": "X"}']
    assert cliente(ollama_falso.url).chat_json("s", "u", OfertaEstructurada).titulo == "X"
    assert len(ollama_falso.pedidos) == 2
    assert "no es un JSON válido" in ollama_falso.pedidos[1]["messages"][-1]["content"]


def test_chat_json_falla_tras_reintento(ollama_falso):
    ollama_falso.respuestas = ["basura", "más basura"]
    with pytest.raises(SalidaInvalida):
        cliente(ollama_falso.url).chat_json("s", "u", OfertaEstructurada)
    assert len(ollama_falso.pedidos) == 2


def test_chat_texto(ollama_falso):
    ollama_falso.respuestas = ["Hola"]
    assert cliente(ollama_falso.url).chat_texto("s", "u") == "Hola"
    assert "format" not in ollama_falso.pedidos[0]


def test_modelo_no_descargado(ollama_falso):
    with pytest.raises(ModeloNoDisponible, match="ollama pull inexistente"):
        cliente(ollama_falso.url, LLM_MODELO_PRINCIPAL="inexistente").chat_texto("s", "u")


def test_embeber(ollama_falso):
    v = cliente(ollama_falso.url).embeber(["ab", "abcd"])
    assert v == [[2.0, 1.0], [4.0, 1.0]]
    assert ollama_falso.pedidos[0]["ruta"] == "/api/embed"


def test_contexto_excedido_no_llama_al_modelo(ollama_falso):
    with pytest.raises(ContextoExcedido):
        cliente(ollama_falso.url).chat_texto("s", "x" * 20000)
    assert ollama_falso.pedidos == []


def test_ollama_apagado():
    c = cliente("http://127.0.0.1:1")
    with pytest.raises(LLMError, match="No encuentro Ollama"):
        c.chat_texto("s", "u")
    ok, msg = c.estado()
    assert not ok and "Ollama" in msg


def test_estado_detecta_modelos_faltantes(ollama_falso):
    assert cliente(ollama_falso.url).estado() == (True, "Listo.")
    ollama_falso.modelos = ["qwen2.5:3b"]
    ok, msg = cliente(ollama_falso.url).estado()
    assert not ok and "ollama pull bge-m3" in msg


# ---------- proveedores en la nube: solo se comprueba el armado del pedido (sin red)
def test_claude_arma_pedido_y_valida_json():
    vistos = []

    def http(url, payload, headers, timeout):
        vistos.append((url, payload, headers))
        return {"content": [{"type": "text", "text": '{"titulo": "Redactor"}'}]}

    c = LLMClient(cargar_config({"LLM_PROVIDER": "claude", "ANTHROPIC_API_KEY": "k"}), http=http)
    assert c.chat_json("sis", "usu", OfertaEstructurada).titulo == "Redactor"
    url, payload, headers = vistos[0]
    assert url.endswith("/v1/messages") and headers["x-api-key"] == "k"
    assert "esquema" in payload["system"] and payload["messages"][0]["role"] == "user"


def test_gemini_arma_pedido():
    vistos = []

    def http(url, payload, headers, timeout):
        vistos.append((url, payload))
        return {"candidates": [{"content": {"parts": [{"text": "{}"}]}}]}

    c = LLMClient(cargar_config({"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "k", "LLM_MIN_INTERVALO_S": "0"}), http=http)
    c.chat_json("sis", "usu", OfertaEstructurada)
    assert "generateContent" in vistos[0][0]
    assert vistos[0][1]["generationConfig"]["responseMimeType"] == "application/json"


def test_metricas_cuentan_llamadas_sin_guardar_contenido(ollama_falso):
    c = cliente(ollama_falso.url)
    ollama_falso.respuestas = ['{"titulo": "X"}', "texto"]
    c.chat_json("s", "SECRETO del CV", OfertaEstructurada)
    c.chat_texto("s", "u")
    c.embeber(["a"])
    r = c.resumen_metricas()
    assert r["llamadas"] == 3 and set(r["por_tipo"]) == {"chat_json", "chat_texto", "embeddings"} and r["segundos"] >= 0
    assert "SECRETO" not in str(c.metricas)


def test_metricas_registran_errores(ollama_falso):
    c = cliente(ollama_falso.url, LLM_MODELO_PRINCIPAL="inexistente")
    with pytest.raises(ModeloNoDisponible):
        c.chat_texto("s", "u")
    assert c.resumen_metricas()["por_tipo"]["chat_texto"]["errores"] == 1
