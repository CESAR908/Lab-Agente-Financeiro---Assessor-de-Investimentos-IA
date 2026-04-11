# src/app.py

import streamlit as st
from datetime import datetime

# imports corretos com o caminho do pacote
from src.agente import AgenteFinanceiro
from src.base_conhecimento import BaseConhecimento
from src.utils import formatar_moeda, formatar_percentual

# ... o resto do código permanece exatamente como enviado anteriormente ...


# ----------------------------------------------------------------------
# Configurações da página + CSS global
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
# Inicialização do session_state (executa só na primeira carga)
# ----------------------------------------------------------------------
if "agente" not in st.session_state:
    st.session_state.agente = AgenteFinanceiro()
    st.session_state.base_conhecimento = BaseConhecimento()
    st.session_state.historico_chat = []          # lista de dicts {tipo, conteudo, timestamp}
    st.session_state.cliente_id = "CLI001"
    st.session_state.bot_is_thinking = False      # controla loading UI

# ----------------------------------------------------------------------
# Sidebar – seleção do cliente
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")

    clientes = st.session_state.base_conhecimento.listar_clientes()
    if not clientes:
        st.warning("Nenhum cliente encontrado. Verifique a pasta **data/**.")
        st.stop()

    cliente_selecionado = st.selectbox(
        "Selecione um cliente:",
        clientes,
        index=clientes.index(st.session_state.cliente_id)
        if st.session_state.cliente_id in clientes
        else 0,
        key="cliente_select",
    )
    st.session_state.cliente_id = cliente_selecionado

    # Exibe informações resumidas do cliente selecionado
    perfil = st.session_state.base_conhecimento.obter_perfil(st.session_state.cliente_id)
    if perfil:
        st.subheader("Perfil do Cliente")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Idade", perfil.get("dados_pessoais", {}).get("idade", "N/A"))
        with col2:
            st.metric(
                "Perfil de Risco",
                perfil.get("perfil_risco", {}).get("classificacao", "N/A").upper(),
            )
    st.warning(
        "⚠️ Esta é uma recomendação educacional, não uma orientação de investimento."
    )

# ----------------------------------------------------------------------
# Área principal – chat + ações rápidas
# ----------------------------------------------------------------------
if st.session_state.cliente_id:
    st.subheader("💬 Chat com Assessor IA")

    # ---------- Renderiza mensagens anteriores ----------
    for mensagem in st.session_state.historico_chat:
        if mensagem["tipo"] == "usuario":
            with st.chat_message("user"):
                st.write(mensagem["conteudo"])
        else:
            with st.chat_message("assistant"):
                st.write(mensagem["conteudo"])

    # ---------- Caixa de entrada ----------
    if not st.session_state.bot_is_thinking:
        usuario_input = st.chat_input(
            "Faça uma pergunta sobre investimentos...", key="chat_input"
        )
    else:
        usuario_input = None  # desabilita nova entrada enquanto processa

    # ---------- Processa a pergunta do usuário ----------
    if usuario_input:
        # 1️⃣ grava mensagem do usuário
        st.session_state.historico_chat.append(
            {"tipo": "usuario", "conteudo": usuario_input, "timestamp": datetime.now()}
        )
        st.session_state.bot_is_thinking = True

        # 2️⃣ mostra spinner dentro da bolha do assistente
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analisando sua pergunta..."):
                resposta = st.session_state.agente.processar_pergunta(
                    pergunta=usuario_input,
                    cliente_id=st.session_state.cliente_id,
                    base_conhecimento=st.session_state.base_conhecimento,
                )

        # 3️⃣ grava resposta do assistente
        st.session_state.historico_chat.append(
            {"tipo": "assistente", "conteudo": resposta, "timestamp": datetime.now()}
        )
        st.session_state.bot_is_thinking = False
        # Não precisamos chamar st.rerun(); o Streamlit já atualiza a UI.

    # ---------- Ações rápidas (botões) ----------
    st.divider()
    st.subheader("⚡ Ações Rápidas")
    col1, col2, col3 = st.columns(3)

    def _canned_question(texto: str):
        """Executa a mesma lógica de chat, porém usando uma pergunta pré‑definida."""
        st.session_state.historico_chat.append(
            {"tipo": "usuario", "conteudo": texto, "timestamp": datetime.now()}
        )
        st.session_state.bot_is_thinking = True

        resp = st.session_state.agente.processar_pergunta(
            pergunta=texto,
            cliente_id=st.session_state.cliente_id,
            base_conhecimento=st.session_state.base_conhecimento,
        )

        st.session_state.historico_chat.append(
            {"tipo": "assistente", "conteudo": resp, "timestamp": datetime.now()}
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
            st.session_state.historico_chat = []   # limpa o chat
