"""Cliente para Perplexity Sonar Pro API.

Função principal: send_sonar_query(question: str, context: dict | None = None, **kwargs) -> dict
- Reutilizável para múltiplos tipos de queries
- Carrega chave via SONAR_API_KEY (env)
- Faz POST seguro usando requests
- Faz logging sem expor segredos

Referência de endpoint (sujeito a mudanças):
- POST {SONAR_API_BASE}/chat/completions
- Headers: Authorization: Bearer <SONAR_API_KEY>, Content-Type: application/json
"""
from __future__ import annotations
from typing import Any, Dict, Optional
import time
import requests
from requests import Response

from src.settings import (
    SONAR_API_BASE,
    SONAR_API_KEY,
    SONAR_DEFAULT_MODEL,
)
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class SonarAPIError(RuntimeError):
    pass


def _build_messages(question: str, context: Optional[dict]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if context:
        # Inclui contexto como mensagem do sistema para guiar o modelo
        sys_content = f"Você é um assistente que responde com base no contexto fornecido. Contexto: {context}"
        messages.append({"role": "system", "content": sys_content})
    messages.append({"role": "user", "content": question})
    return messages


def send_sonar_query(
    question: str,
    context: Optional[dict] = None,
    *,
    model: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.2,
    top_p: float = 0.9,
    timeout: int = 30,
    extra_headers: Optional[Dict[str, str]] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> dict:
    """Envia uma consulta para a Sonar Pro API e retorna o JSON de resposta.

    Parâmetros:
        question: pergunta do usuário
        context: dicionário com informações adicionais para orientar a resposta
        model: nome do modelo (default em settings SONAR_DEFAULT_MODEL)
        max_tokens, temperature, top_p: parâmetros de geração
        timeout: tempo máximo (s) para a requisição HTTP
        extra_headers: cabeçalhos adicionais
        extra_params: parâmetros extras para o payload JSON

    Retorno:
        dict com resposta crua da API; em caso de erro, lança SonarAPIError
    """
    if not SONAR_API_KEY:
        raise SonarAPIError(
            "SONAR_API_KEY não configurada. Defina em configs/.env ou variável de ambiente."
        )

    url = f"{SONAR_API_BASE.rstrip('/')}/chat/completions"
    payload: Dict[str, Any] = {
        "model": model or SONAR_DEFAULT_MODEL,
        "messages": _build_messages(question, context),
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "stream": False,
    }
    if extra_params:
        payload.update(extra_params)

    headers = {
        "Authorization": f"Bearer {SONAR_API_KEY}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    # Logging sem segredos
    logger.info(
        "Sonar request: url=%s model=%s max_tokens=%s temp=%.2f context=%s",
        url,
        payload["model"],
        payload["max_tokens"],
        payload["temperature"],
        bool(context),
    )

    t0 = time.perf_counter()
    try:
        resp: Response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        raise SonarAPIError(f"Erro de rede ao chamar Sonar API: {e}") from e
    dt = time.perf_counter() - t0

    logger.info("Sonar response: status=%s dur=%.3fs", resp.status_code, dt)

    if not resp.ok:
        # tenta extrair corpo para diagnóstico
        body = None
        try:
            body = resp.json()
        except Exception:
            body = resp.text[:500]
        raise SonarAPIError(f"HTTP {resp.status_code} ao chamar Sonar API: {body}")

    try:
        data = resp.json()
    except ValueError as e:
        raise SonarAPIError("Resposta não é JSON válido da Sonar API") from e

    return data
