import streamlit as st
import pandas as pd
from datetime import datetime
import json
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
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

try:
    if 'agente' not in st.session_state:
        st.session_state.agente = AgenteFincanceiro()
        st.session_state.base_conhecimento = BaseConhecimento()
        st.session_state.historico_chat = []
        st.session_state.cliente_id = "CLI001"
except Exception as e:
    st.error(f"Erro ao inicializar: {str(e)}")
    st.stop()

st.title("💰 Assessor IA - Consultoria de Investimentos")
st.markdown("*Seu assessor de investimentos disponível 24/7*")

with st.sidebar:
    st.header("⚙️ Configurações")

    try:
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
                st.subheader("📊 Perfil do Cliente")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Idade",
                        f"{perfil.get('dados_pessoais', {}).get('idade', 'N/A')} anos"
                    )
                    st.metric(
                        "Profissão",
                        perfil.get('dados_pessoais', {}).get('profissao', 'N/A')
                    )

                with col2:
                    st.metric(
                        "Perfil de Risco",
                        perfil.get('perfil_risco', {}).get('classificacao', 'N/A').upper()
                    )
                    st.metric(
                        "Patrimônio",
                        f"R$ {perfil.get('situacao_financeira', {}).get('patrimonio_total', 0):,.0f}"
                    )

                st.divider()
                st.subheader("💼 Alocação Atual")

                alocacao = perfil.get('alocacao_atual', {})
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Renda Fixa",
                        f"{alocacao.get('renda_fixa', 0)}%"
                    )

                with col2:
                    st.metric(
                        "Renda Variável",
                        f"{alocacao.get('renda_variavel', 0)}%"
                    )

                with col3:
                    st.metric(
                        "Alternativas",
                        f"{alocacao.get('alternativas', 0)}%"
                    )
        else:
            st.warning("Nenhum cliente disponível")

    except Exception as e:
        st.error(f"Erro ao carregar clientes: {str(e)}")

    st.divider()
    st.warning(
        "⚠️ **Disclaimer**: Esta é uma recomendação educacional, não uma orientação de investimento."
    )

if st.session_state.cliente_id:
    st.subheader("💬 Chat com Assessor IA")

    # Exibir histórico
    if st.session_state.historico_chat:
        for mensagem in st.session_state.historico_chat:
            if mensagem['tipo'] == 'usuario':
                with st.chat_message("user", avatar="👤"):
                    st.write(mensagem['conteudo'])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    # Tentar parsear JSON se for resposta estruturada
                    conteudo = mensagem['conteudo']
                    try:
                        if conteudo.strip().startswith('{'):
                            dados = json.loads(conteudo)
                            st.json(dados)
                        else:
                            st.write(conteudo)
                    except:
                        st.write(conteudo)

    # Input do usuário
    usuario_input = st.chat_input(
        "Faça uma pergunta sobre investimentos...",
        key="chat_input"
    )

    if usuario_input:
        # Adicionar mensagem do usuário
        st.session_state.historico_chat.append({
            'tipo': 'usuario',
            'conteudo': usuario_input,
            'timestamp': datetime.now()
        })

        # Gerar resposta
        with st.spinner("🤔 Analisando sua pergunta..."):
            try:
                resposta = st.session_state.agente.processar_pergunta(
                    pergunta=usuario_input,
                    cliente_id=st.session_state.cliente_id,
                    base_conhecimento=st.session_state.base_conhecimento
                )
            except Exception as e:
                resposta = f"Erro ao processar: {str(e)}"

        # Adicionar resposta
        st.session_state.historico_chat.append({
            'tipo': 'assistente',
            'conteudo': resposta,
            'timestamp': datetime.now()
        })

        # Exibir resposta
        with st.chat_message("assistant", avatar="🤖"):
            try:
                if resposta.strip().startswith('{'):
                    dados = json.loads(resposta)
                    st.json(dados)
                else:
                    st.write(resposta)
            except:
                st.write(resposta)

        st.rerun()

    # Ações rápidas
    st.divider()
    st.subheader("⚡ Ações Rápidas")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Análise de Carteira", key="btn_analise"):
            usuario_input = "Faça uma análise completa da minha carteira atual"
            st.session_state.historico_chat.append({
                'tipo': 'usuario',
                'conteudo': usuario_input,
                'timestamp': datetime.now()
            })

            with st.spinner("🤔 Analisando..."):
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
        if st.button("💡 Recomendação Personalizada", key="btn_recomendacao"):
            usuario_input = "Qual é a melhor alocação para meu perfil?"
            st.session_state.historico_chat.append({
                'tipo': 'usuario',
                'conteudo': usuario_input,
                'timestamp': datetime.now()
            })

            with st.spinner("🤔 Analisando..."):
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
        if st.button("🗑️ Limpar Histórico", key="btn_limpar"):
            st.session_state.historico_chat = []
            st.rerun()

    # Seção de produtos disponíveis
    st.divider()
    st.subheader("📚 Produtos Disponíveis")

    produtos = st.session_state.base_conhecimento.obter_produtos()

    if produtos:
        # Criar abas para cada produto
        tabs = st.tabs([p.get('nome', 'Produto') for p in produtos[:5]])

        for tab, produto in zip(tabs, produtos[:5]):
            with tab:
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Categoria:** {produto.get('categoria', 'N/A')}")
                    st.write(f"**Descrição:** {produto.get('descricao', 'N/A')}")
                    st.write(f"**Risco:** {produto.get('risco', 'N/A').replace('_', ' ').upper()}")

                with col2:
                    st.write(f"**Rentabilidade Esperada:** {produto.get('rentabilidade_esperada', 'N/A')}")
                    st.write(f"**Rentabilidade 12m:** {produto.get('rentabilidade_historica_12m', 0)}%")
                    st.write(f"**Taxa Admin:** {produto.get('taxa_administracao', 0)}%")
    else:
        st.info("Nenhum produto disponível")

st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>Assessor IA © 2026 | Consultoria de Investimentos Inteligente</p>
        <p>Desenvolvido com ❤️ usando Streamlit e Ollama</p>
    </div>
""", unsafe_allow_html=True)
