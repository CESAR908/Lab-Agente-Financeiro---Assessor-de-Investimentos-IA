# src/agente.py
import requests
from typing import Dict, List, Optional

# ----------------------------------------------------------------------
# Public class – the correct name
# ----------------------------------------------------------------------
class AgenteFinanceiro:
    """
    Wrapper around an Ollama model that receives a natural‑language question,
    builds a context from the knowledge base and returns the model response.
    """

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.modelo = "mistral"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def processar_pergunta(
        self,
        pergunta: str,
        cliente_id: str,
        base_conhecimento: "BaseConhecimento",   # forward reference to avoid circular import
    ) -> str:
        """
        Build the prompt and call Ollama.
        """
        # 1️⃣ Gather data
        perfil = base_conhecimento.obter_perfil(cliente_id)
        transacoes = base_conhecimento.obter_transacoes(cliente_id)
        historico = base_conhecimento.obter_historico_atendimento(cliente_id)
        produtos = base_conhecimento.obter_produtos()

        # 2️⃣ Build context (limited to the latest 5 transactions)
        contexto = self._construir_contexto(
            perfil=perfil,
            transacoes=transacoes[-5:],          # keep only the newest 5
            historico=historico,
            produtos=produtos,
        )

        # 3️⃣ Intent classification (rule‑based)
        intent = self._classificar_intent(pergunta)

        # 4️⃣ Full prompt
        prompt = self._gerar_prompt(
            pergunta=pergunta,
            contexto=contexto,
            intent=intent,
            perfil=perfil,
        )

        # 5️⃣ Call Ollama (with a tiny retry)
        return self._chamar_ollama(prompt)


    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _construir_contexto(
        self,
        perfil: Dict,
        transacoes: List[Dict],
        historico: List[Dict],
        produtos: List[Dict],
    ) -> str:
        """Return a formatted string with the most relevant data."""
        # Keep the same layout you already have – just a tiny bit of safety.
        nome = perfil.get('nome', 'N/A')
        idade = perfil.get('dados_pessoais', {}).get('idade', 'N/A')
        profissao = perfil.get('dados_pessoais', {}).get('profissao', 'N/A')
        renda = perfil.get('situacao_financeira', {}).get('renda_mensal', 0)
        patrimonio = perfil.get('situacao_financeira', {}).get('patrimonio_total', 0)
        risco = perfil.get('perfil_risco', {}).get('classificacao', 'N/A').upper()
        tolerancia = perfil.get('perfil_risco', {}).get('tolerancia_queda_percentual', 'N/A')

        contexto = f"""PERFIL DO CLIENTE:
- Nome: {nome}
- Idade: {idade} anos
- Profissão: {profissao}
- Renda Mensal: R$ {renda:,.2f}
- Patrimônio: R$ {patrimonio:,.2f}
- Perfil de Risco: {risco}
- Tolerância a Queda: {tolerancia}%

OBJETIVOS:
"""

        for obj in perfil.get('objetivos_investimento', []):
            objetivo = obj.get('objetivo', 'N/A')
            prazo = obj.get('prazo_anos', 'N/A')
            valor = obj.get('valor_alvo', 0)
            contexto += f"- {objetivo} ({prazo} anos): R$ {valor:,.2f}\n"

        contexto += f"""
ALOCAÇÃO ATUAL:
- Renda Fixa: {perfil.get('alocacao_atual', {}).get('renda_fixa', 0)}%
- Renda Variável: {perfil.get('alocacao_atual', {}).get('renda_variavel', 0)}%
- Alternativas: {perfil.get('alocacao_atual', {}).get('alternativas', 0)}%

PERFORMANCE:
- Rentabilidade Acumulada: {perfil.get('historico_performance', {}).get('rentabilidade_acumulada', 0)}%

ÚLTIMAS TRANSAÇÕES:
"""

        if transacoes:
            for t in transacoes:
                data = t.get('data')
                tipo = t.get('tipo', '').upper()
                produto = t.get('produto')
                valor = t.get('valor', 0)
                contexto += f"- {data}: {tipo} {produto} - R$ {valor:,.2f}\n"
        else:
            contexto += "- Nenhuma transação recente.\n"

        # (You could also add a short summary of `historico` or `produtos` if needed.)

        return contexto


    def _classificar_intent(self, pergunta: str) -> str:
        """Return a high‑level intent based on keyword matching."""
        # Lower‑casing and normalising accented characters helps a lot.
        q = pergunta.lower()

        # map of intent → set of trigger words
        intents = {
            "recomendacao": {"recomend", "devo investir", "qual produto", "melhor", "sugest", "ideal"},
            "educacao": {"como funciona", "o que é", "explique", "diferen", "significado"},
            "analise": {"carteira", "performance", "como está", "análise", "rendimento"},
            "risco": {"risco", "volatilidade", "queda", "preocup", "segur", "conservadora"},
        }

        for intent, keywords in intents.items():
            if any(kw in q for kw in keywords):
                return intent

        return "geral"


    def _gerar_prompt(
        self,
        pergunta: str,
        contexto: str,
        intent: str,
        perfil: Dict,
    ) -> str:
        """
        Build the final prompt that will be sent to Ollama.
        ``intent`` is currently unused but kept for possible future styling.
        """
        # You can experiment with different system messages per intent later.
        return f"""{contexto}
PERGUNTA: {pergunta}
Você é um assessor de investimentos profissional. Responda baseado APENAS nos dados acima.

INSTRUÇÕES:
1. Baseie sua resposta nos dados fornecidos.
2. Não invente rentabilidades ou números que não existam.
3. Considere o perfil de risco do cliente.
4. Seja claro e acessível.
5. Inclua disclaimer se for recomendação.

Responda de forma concisa e profissional."""


    def _chamar_ollama(self, prompt: str) -> str:
        """Call the Ollama `/api/generate` endpoint with a tiny retry."""
        max_tries = 2
        for attempt in range(1, max_tries + 1):
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.modelo,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.7,
                    },
                    timeout=30,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "Desculpe, não consegui gerar uma resposta.")
                else:
                    # Non‑200, raise to retry (or finally report)
                    raise RuntimeError(f"Ollama returned {response.status_code}")
            except (requests.exceptions.ConnectionError, RuntimeError) as exc:
                if attempt == max_tries:
                    return (
                        "Erro ao conectar com Ollama. Verifique se o serviço está rodando "
                        "em http://localhost:11434 e tente novamente."
                    )
                # Wait a tiny bit before next try
                import time
                time.sleep(0.5)
            except Exception as exc:
                return f"Erro inesperado: {str(exc)}"



# src/base_conhecimento.py
import json
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class BaseConhecimento:
    """
    Simple in‑memory data‑store that loads JSON/CSV files from ``data/``.
    It now supports **multiple** clients – each CSV must contain a ``cliente_id`` column.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.clientes: Dict[str, Dict] = {}
        self.produtos: List[Dict] = []
        self.transacoes: Dict[str, List[Dict]] = {}
        self.historico_atendimento: Dict[str, List[Dict]] = {}

        self._carregar_dados()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _carregar_dados(self):
        """Load all files from ``self.data_dir``."""

        # ---- 1️⃣ Perfis (JSON) -------------------------------------------------
        perfil_path = self.data_dir / "perfil_investidor.json"
        if perfil_path.exists():
            with open(perfil_path, "r", encoding="utf-8") as f:
                perfil = json.load(f)
                cliente_id = perfil.get("cliente_id", "CLI001")
                self.clientes[cliente_id] = perfil

        # ---- 2️⃣ Transações (CSV) ---------------------------------------------
        transacoes_path = self.data_dir / "transacoes.csv"
        if transacoes_path.exists():
            df = pd.read_csv(transacoes_path, dtype=str)  # keep everything as string first
            # If there is no explicit client column, assume all rows belong to CLI001
            if "cliente_id" not in df.columns:
                df["cliente_id"] = "CLI001"
            # Convert numeric columns to proper types
            numeric_cols = ["valor"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

            for cliente_id, group in df.groupby("cliente_id"):
                self.transacoes[cliente_id] = group.drop(columns=["cliente_id"]).to_dict(
                    "records"
                )

        # ---- 3️⃣ Histórico de atendimento (CSV) ---------------------------------
        historico_path = self.data_dir / "historico_atendimento.csv"
        if historico_path.exists():
            df = pd.read_csv(historico_path, dtype=str)
            if "cliente_id" not in df.columns:
                df["cliente_id"] = "CLI001"
            for cliente_id, group in df.groupby("cliente_id"):
                self.historico_atendimento[cliente_id] = group.drop(columns=["cliente_id"]).to_dict(
                    "records"
                )

        # ---- 4️⃣ Produtos (JSON) ------------------------------------------------
        produtos_path = self.data_dir / "produtos_financeiros.json"
        if produtos_path.exists():
            with open(produtos_path, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.produtos = dados.get("produtos", [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def obter_perfil(self, cliente_id: str) -> Optional[Dict]:
        return self.clientes.get(cliente_id)

    def obter_transacoes(self, cliente_id: str) -> List[Dict]:
        return self.transacoes.get(cliente_id, [])

    def obter_historico_atendimento(self, cliente_id: str) -> List[Dict]:
        return self.historico_atendimento.get(cliente_id, [])

    def obter_produtos(self) -> List[Dict]:
        return self.produtos

    def obter_produto(self, produto_id: str) -> Optional[Dict]:
        for p in self.produtos:
            if p.get("id") == produto_id:
                return p
        return None

    def listar_clientes(self) -> List[str]:
        """Return a list of known client identifiers (e.g. [\"CLI001\", \"CLI002\"])."""
        return list(self.clientes.keys())

    # ------------------------------------------------------------------
    # Helpers to add a new client (useful for future UI)
    # ------------------------------------------------------------------
    def salvar_cliente(self, cliente_data: Dict) -> str:
        """Add a new client to the in‑memory store and return its generated ID."""
        cliente_id = f"CLI{len(self.clientes) + 1:03d}"
        cliente_data["cliente_id"] = cliente_id
        self.clientes[cliente_id] = cliente_data
        self.transacoes[cliente_id] = []
        self.historico_atendimento[cliente_id] = []
        return cliente_id

# src/app.py
import streamlit as st
from datetime import datetime

from agente import AgenteFinanceiro   # <-- new correct import
from base_conhecimento import BaseConhecimento
from utils import formatar_moeda, formatar_percentual

# ----------------------------------------------------------------------
# Page config + global CSS
# ----------------------------------------------------------------------
st.set_page_config(page_title="Assessor IA", page_icon="💰", layout="wide")
st.markdown(
    """
    <style>
    .recommendation-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-left: 4px solid #0066cc;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Initialise session state (once per user)
# ----------------------------------------------------------------------
if "agente" not in st.session_state:
    st.session_state.agente = AgenteFinanceiro()
    st.session_state.base_conhecimento = BaseConhecimento()
    st.session_state.historico_chat = []          # list of dicts {tipo, conteudo, timestamp}
    st.session_state.cliente_id = "CLI001"
    st.session_state.bot_is_thinking = False      # UI flag

# ----------------------------------------------------------------------
# Sidebar – client selector
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")

    clientes = st.session_state.base_conhecimento.listar_clientes()
    if not clientes:
        st.warning("Nenhum cliente carregado. Verifique os arquivos em *data/*.")
        st.stop()

    cliente_selecionado = st.selectbox(
        "Selecione um cliente:",
        clientes,
        index=clientes.index(st.session_state.cliente_id) if st.session_state.cliente_id in clientes else 0,
        key="cliente_select",
    )
    st.session_state.cliente_id = cliente_selecionado

    # Show a quick profile snapshot
    perfil = st.session_state.base_conhecimento.obter_perfil(st.session_state.cliente_id)
    if perfil:
        st.subheader("Perfil do Cliente")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Idade",
                perfil.get("dados_pessoais", {}).get("idade", "N/A")
            )
        with col2:
            st.metric(
                "Perfil de Risco",
                perfil.get("perfil_risco", {}).get("classificacao", "N/A").upper()
            )
    st.warning(
        "⚠️ Esta é uma recomendação educacional, não uma orientação de investimento."
    )

# ----------------------------------------------------------------------
# Main UI – chat + quick actions
# ----------------------------------------------------------------------
if st.session_state.cliente_id:
    st.subheader("💬 Chat com Assessor IA")

    # ---- Render previous messages ----------------------------------------
    for mensagem in st.session_state.historico_chat:
        if mensagem["tipo"] == "usuario":
            with st.chat_message("user"):
                st.write(mensagem["conteudo"])
        else:
            with st.chat_message("assistant"):
                st.write(mensagem["conteudo"])

    # ---- Input box -------------------------------------------------------
    if not st.session_state.bot_is_thinking:
        usuario_input = st.chat_input(
            "Faça uma pergunta sobre investimentos...",
            key="chat_input"
        )
    else:
        usuario_input = None   # block new input while we wait for the model

    # ---- Process user question -------------------------------------------
    if usuario_input:
        # Append user message
        st.session_state.historico_chat.append(
            {"tipo": "usuario", "conteudo": usuario_input, "timestamp": datetime.now()}
        )
        st.session_state.bot_is_thinking = True
        # Show a spinner *inside* the assistant chat bubble
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analisando sua pergunta..."):
                resposta = st.session_state.agente.processar_pergunta(
                    pergunta=usuario_input,
                    cliente_id=st.session_state.cliente_id,
                    base_conhecimento=st.session_state.base_conhecimento,
                )
        # Append assistant reply
        st.session_state.historico_chat.append(
            {"tipo": "assistente", "conteudo": resposta, "timestamp": datetime.now()}
        )
        st.session_state.bot_is_thinking = False
        # No need to call `st.rerun()` – Streamlit already updates the UI after the block.

    # ----------------------------------------------------------------------
    # Quick actions (buttons)
    # ----------------------------------------------------------------------
    st.divider()
    st.subheader("⚡ Ações Rápidas")
    col1, col2, col3 = st.columns(3)

    # Helper to fire a canned question
    def _canned_question(text: str):
        # Simulate same flow as manual input
        st.session_state.historico_chat.append(
            {"tipo": "usuario", "conteudo": text, "timestamp": datetime.now()}
        )
        st.session_state.bot_is_thinking = True
        resposta = st.session_state.agente.processar_pergunta(
            pergunta=text,
            cliente_id=st.session_state.cliente_id,
            base_conhecimento=st.session_state.base_conhecimento,
        )
        st.session_state.historico_chat.append(
            {"tipo": "assistente", "conteudo": resposta, "timestamp": datetime.now()}
        )
        st.session_state.bot_is_thinking = False

    with col1:
        if st.button("📊 Análise de Carteira", disabled=st.session_state.bot_is_thinking):
            _canned_question("Faça uma análise completa da minha carteira atual")
    with col2:
        if st.button("💡 Recomendação", disabled=st.session_state.bot_is_thinking):
            _canned_question("Qual é a melhor alocação para meu perfil?")
    with col3:
        if st.button("🗑️ Limpar", disabled=st.session_state.bot_is_thinking):
            st.session_state.historico_chat = []
            # No need for st.rerun() – the UI will re‑render automatically

import os
import shutil
import json
import pandas as pd
import pytest

from src.base_conhecimento import BaseConhecimento


@pytest.fixture
def tmp_data_dir(tmp_path):
    # ---- 1️⃣ Write a minimal perfil JSON ----
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

    # ---- 2️⃣ Write a transactions CSV with a client_id column ----
    df = pd.DataFrame(
        [
            {"cliente_id": "CLI999", "data": "2024-01-15", "tipo": "compra", "produto": "ETF XYZ", "valor": 1500},
            {"cliente_id": "CLI999", "data": "2024-02-10", "tipo": "venda", "produto": "CDB 110%", "valor": 2000},
        ]
    )
    df.to_csv(tmp_path / "transacoes.csv", index=False)

    # ---- 3️⃣ Write a simple histórico CSV ----
    df_hist = pd.DataFrame(
        [
            {"cliente_id": "CLI999", "data": "2024-03-01", "assunto": "Rebalanceamento", "observacoes": "OK"},
        ]
    )
    df_hist.to_csv(tmp_path / "historico_atendimento.csv", index=False)

    # ---- 4️⃣ Write a tiny produtos JSON ----
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
    resp = agente._chamar_ollama("prompt teste")
    assert resp == "Resposta simulada"


@patch("src.agente.requests.post")
def test_chamar_ollama_failure(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_post.return_value = mock_resp

    agente = AgenteFinanceiro()
    resp = agente._chamar_ollama("prompt teste")
    assert "Erro ao conectar com Ollama" in resp


        
