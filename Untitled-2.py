# tests/test_agente.py
import pytest
from unittest.mock import patch, MagicMock

from src.agente import AgenteFinanceiro


def test_classificar_intent():
    agente = AgenteFinanceiro()
    assert agente._classificar_intent("Qual produto devo comprar?") == "recomendacao"
    assert agente._classificar_intent("Como funciona um CDB?") == "educacao"
    assert agente._classificar_intent("Me mostre a performance da minha carteira") == "analise"
    assert agente._classificar_intent("Estou preocupado com o risco") == "risco"
    assert agente._classificar_intent("Qual é a taxa de juros?") == "geral"


@patch("src.agente.requests.post")
def test_chamar_ollama_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "Resposta simulada"}
    mock_post.return_value = mock_resp

    agente = AgenteFinanceiro()
    resposta = agente._chamar_ollama("prompt teste")
    assert resposta == "Resposta simulada"


@patch("src.agente.requests.post")
def test_chamar_ollama_failure(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_post.return_value = mock_resp

    agente = AgenteFinanceiro()
    resposta = agente._chamar_ollama("prompt teste")
    assert "Erro ao conectar com Ollama" in resposta
