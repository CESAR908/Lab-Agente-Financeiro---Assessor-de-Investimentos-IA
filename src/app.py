import streamlit as st
import pandas as pd
from datetime import datetime
from agente import AgenteFincanceiro
from base_conhecimento import BaseConhecimento
from utils import formatar_moeda

st.set_page_config(
    page_title="Assessor IA",
    page_icon="💰",
    layout="wide"
)

st.markdown("""
    <style>
    .recommendation-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-left: 4px solid #0066cc;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

if 'agente' not in st.session_state:
    st.session_state.agente = AgenteFincanceiro()
    st.session_state.base_conhecimento = BaseConhecimento()
    st.session_state.historico_chat = []
    st.session_state.cliente_id = "CLI001"

st.title("💰 Assessor IA - Consultoria de Investimentos")
st.markdown("*Seu assessor de investimentos disponível 24/7*")

with st.sidebar:
    st.header("⚙️ Configurações")

    clientes = st.session_state.base_conhecimento.listar_clientes()

    if clientes:
        cliente_selecionado = st.selectbox(
            "Selecione um cliente:",
            clientes,
            key="cliente_select"
        )
        st.session_state.cliente_id = cliente_selecionado

        perfil = st.session_state.base_conhecimento.obter_perfil(
            st.session_state.cliente_id
        )

        if perfil:
            st.subheader("Perfil do Cliente")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Idade",
                    perfil.get('dados_pessoais', {}).get('idade', 'N/A')
                )
            with col2:
                st.metric(
                    "Perfil de Risco",
                    perfil.get('perfil_risco', {}).get('classificacao', 'N/A').upper()
                )

    st.warning(
        "⚠️ Esta é uma recomendação educacional, não uma orientação de investimento."
    )

if st.session_state.cliente_id:
    st.subheader("💬 Chat com Assessor IA")

    if st.session_state.historico_chat:
        for mensagem in st.session_state.historico_chat:
            if mensagem['tipo'] == 'usuario':
                with st.chat_message("user"):
                    st.write(mensagem['conteudo'])
            else:
                with st.chat_message("assistant"):
                    st.write(mensagem['conteudo'])

    usuario_input = st.chat_input(
        "Faça uma pergunta sobre investimentos...",
        key="chat_input"
    )

    if usuario_input:
        st.session_state.historico_chat.append({
            'tipo': 'usuario',
            'conteudo': usuario_input,
            'timestamp': datetime.now()
        })

        with st.spinner("🤔 Analisando sua pergunta..."):
            resposta = st.session_state.agente.processar_pergunta(
                pergunta=usuario_input,
                cliente_id=st.session_state.cliente_id,
                base_conhecimento=st.session_state.base_conhecimento
            )

        st.session_state.historico_chat.append({
            'tipo': 'assistente',
            'conteudo': resposta,
            'timestamp': datetime.now()
        })

        with st.chat_message("assistant"):
            st.write(resposta)

        st.rerun()

    st.divider()
    st.subheader("⚡ Ações Rápidas")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Análise de Carteira"):
            usuario_input = "Faça uma análise completa da minha carteira atual"
            st.session_state.historico_chat.append({
                'tipo': 'usuario',
                'conteudo': usuario_input,
                'timestamp': datetime.now()
            })
            resposta = st.session_state.agente.processar_pergunta(
                pergunta=usuario_input,
                cliente_id=st.session_state.cliente_id,
                base_conhecimento=st.session_state.base_conhecimento
            )
            st.session_state.historico_chat.append({
                'tipo': 'assistente',
                'conteudo': resposta,
                'timestamp': datetime.now()
            })
            st.rerun()

    with col2:
        if st.button("💡 Recomendação"):
            usuario_input = "Qual é a melhor alocação para meu perfil?"
            st.session_state.historico_chat.append({
                'tipo': 'usuario',
                'conteudo': usuario_input,
                'timestamp': datetime.now()
            })
            resposta = st.session_state.agente.processar_pergunta(
                pergunta=usuario_input,
                cliente_id=st.session_state.cliente_id,
                base_conhecimento=st.session_state.base_conhecimento
            )
            st.session_state.historico_chat.append({
                'tipo': 'assistente',
                'conteudo': resposta,
                'timestamp': datetime.now()
            })
            st.rerun()

    with col3:
        if st.button("🗑️ Limpar"):
            st.session_state.historico_chat = []
            st.rerun()


