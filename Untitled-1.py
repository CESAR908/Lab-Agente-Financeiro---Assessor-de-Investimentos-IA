# tests/test_base_conhecimento.py
import json
import pandas as pd
import pytest
from pathlib import Path

from src.base_conhecimento import BaseConhecimento


@pytest.fixture
def tmp_data_dir(tmp_path):
    # 1️⃣ perfil JSON
    perfil = {
        "cliente_id": "CLI999",
        "nome": "Teste Cliente",
        "dados_pessoais": {"idade": 30, "profissao": "Engenheiro"},
        "situacao_financeira": {"renda_mensal": 12000, "patrimonio_total": 250000},
        "perfil_risco": {"classificacao": "moderado", "tolerancia_queda_percentual": 15},
        "objetivos_investimento": [
            {"objetivo": "Aposentadoria", "prazo_anos": 20, "valor_alvo": 800000}
        ],
        "alocacao_atual": {"renda_fixa": 50, "renda_variavel": 30, "alternativas": 20},
        "historico_performance": {"rentabilidade_acumulada": 12.5},
    }
    (tmp_path / "perfil_investidor.json").write_text(json.dumps(perfil))

    # 2️⃣ transações CSV com coluna cliente_id
    df_trans = pd.DataFrame(
        [
            {"cliente_id": "CLI999", "data": "2024-01-15", "tipo": "compra", "produto": "ETF XYZ", "valor": 1500},
            {"cliente_id": "CLI999", "data": "2024-02-10", "tipo": "venda", "produto": "CDB 110%", "valor": 2000},
        ]
    )
    df_trans.to_csv(tmp_path / "transacoes.csv", index=False)

    # 3️⃣ histórico CSV
    df_hist = pd.DataFrame(
        [{"cliente_id": "CLI999", "data": "2024-03-01", "assunto": "Rebalanceamento", "observacoes": "OK"}]
    )
    df_hist.to_csv(tmp_path / "historico_atendimento.csv", index=False)

    # 4️⃣ produtos JSON
    produtos = {"produtos": [{"id": "P001", "nome": "Tesouro Selic", "tipo": "renda_fixa"}]}
    (tmp_path / "produtos_financeiros.json").write_text(json.dumps(produtos))

    return tmp_path


def test_carrega_todos_os_dados(tmp_data_dir):
    bc = BaseConhecimento(data_dir=str(tmp_data_dir))

    # Perfil
    perfil = bc.obter_perfil("CLI999")
    assert perfil["nome"] == "Teste Cliente"
    assert perfil["dados_pessoais"]["idade"] == 30

    # Transações
    trans = bc.obter_transacoes("CLI999")
    assert len(trans) == 2
    assert trans[0]["produto"] == "ETF XYZ"

    # Histórico
    hist = bc.obter_historico_atendimento("CLI999")
    assert len(hist) == 1
    assert hist[0]["assunto"] == "Rebalanceamento"

    # Produtos
    prods = bc.obter_produtos()
    assert prods[0]["id"] == "P001"
