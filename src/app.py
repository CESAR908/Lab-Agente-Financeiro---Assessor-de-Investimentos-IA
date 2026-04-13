import streamlit as st
import pandas as pd
from datetime import datetime
import json
from agente import AgenteFincanceiro
from base_conhecimento import BaseConhecimento
from utils import formatar_moeda
from login import show_login, check_login

# Verificar login
if not check_login():
    show_login()
    st.stop()

# Se chegou aqui, usuário está logado
st.set_page_config(
    page_title="Assessor IA",
    page_icon="💰",
    layout="wide"
)

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

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.divider()

    try:
        clientes = st.session_state.base_conhecimento.listar_clientes()
        if clientes:
            cliente_selecionado = st.selectbox(
                "Selecione um cliente",
                [c['id'] for c in clientes],
                format_func=lambda x: next((c['nome'] for c in clientes if c['id'] == x), x)
            )
            st.session_state.cliente_id = cliente_selecionado
    except Exception as e:
        st.warning(f"Erro ao carregar clientes: {str(e)}")

# Abas principais
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Análise de Carteira",
    "💬 Chat com Assessor",
    "📈 Histórico",
    "ℹ️ Sobre"
])

# TAB 1: Análise de Carteira
with tab1:
    st.subheader("📊 Análise de Carteira de Investimentos")

    col1, col2 = st.columns(2)

    with col1:
        valor_investimento = st.number_input(
            "Valor a Investir (R$)",
            min_value=100.0,
            value=1000.0,
            step=100.0
        )

    with col2:
        perfil_risco = st.selectbox(
            "Perfil de Risco",
            ["Conservador", "Moderado", "Agressivo"]
        )

    if st.button("🔍 Analisar Carteira", use_container_width=True, type="primary"):
        with st.spinner("Analisando sua carteira..."):
            try:
                resultado = st.session_state.agente.analisar_carteira(
                    cliente_id=st.session_state.cliente_id,
                    valor_investimento=valor_investimento,
                    base_conhecimento=st.session_state.base_conhecimento
                )

                if resultado['status'] == 'sucesso':
                    st.success("✅ Análise concluída com sucesso!")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Valor Investimento", formatar_moeda(valor_investimento))
                    with col2:
                        st.metric("Perfil", str(resultado.get('perfil', 'N/A')))
                    with col3:
                        st.metric("Status", "✅ Ativo")

                    st.markdown("### 📋 Recomendações")

                    recomendacoes = resultado.get('recomendacoes', {})

                    if isinstance(recomendacoes, dict):
                        # Converter dict para string formatada
                        st.json(recomendacoes)
                    elif isinstance(recomendacoes, str):
                        st.write(recomendacoes)
                    else:
                        st.write(str(recomendacoes))

                    st.session_state.historico_chat.append({
                        'tipo': 'analise',
                        'data': datetime.now(),
                        'valor': valor_investimento,
                        'perfil': perfil_risco,
                        'resultado': str(recomendacoes)
                    })
                else:
                    st.error(f"❌ Erro: {resultado.get('mensagem', 'Erro desconhecido')}")

            except Exception as e:
                st.error(f"❌ Erro ao analisar: {str(e)}")

# TAB 2: Chat com Assessor
with tab2:
    st.subheader("💬 Chat com Seu Assessor IA")

    pergunta = st.text_area(
        "Faça sua pergunta",
        placeholder="Digite sua pergunta sobre investimentos...",
        height=100
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        enviar = st.button("📤 Enviar Pergunta", use_container_width=True, type="primary")

    with col2:
        limpar = st.button("🗑️ Limpar", use_container_width=True)

    if limpar:
        st.session_state.historico_chat = []
        st.rerun()

    if enviar and pergunta:
        with st.spinner("Processando sua pergunta..."):
            try:
                resposta = st.session_state.agente.processar_pergunta(
                    pergunta=pergunta,
                    cliente_id=st.session_state.cliente_id,
                    base_conhecimento=st.session_state.base_conhecimento
                )

                st.info(f"**Sua Pergunta:** {pergunta}")
                st.success(f"**Resposta:** {resposta}")

                st.session_state.historico_chat.append({
                    'tipo': 'chat',
                    'data': datetime.now(),
                    'pergunta': pergunta,
                    'resposta': resposta
                })

            except Exception as e:
                st.error(f"❌ Erro ao processar: {str(e)}")

    if st.session_state.historico_chat:
        st.markdown("### 📜 Histórico da Conversa")
        for msg in reversed(st.session_state.historico_chat[-5:]):
            if msg['tipo'] == 'chat':
                st.markdown(f"**[{msg['data'].strftime('%H:%M:%S')}]**")
                st.write(f"📝 **Pergunta:** {msg['pergunta']}")
                st.write(f"💬 **Resposta:** {msg['resposta']}")
                st.divider()

# TAB 3: Histórico
with tab3:
    st.subheader("📈 Histórico de Operações")

    if st.session_state.historico_chat:
        df_historico = pd.DataFrame([
            {
                'Data': msg['data'].strftime('%d/%m/%Y %H:%M:%S'),
                'Tipo': msg['tipo'].upper(),
                'Detalhes': msg.get('pergunta', msg.get('valor', 'N/A'))
            }
            for msg in st.session_state.historico_chat
        ])

        st.dataframe(df_historico, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Operações", str(len(st.session_state.historico_chat)))
        with col2:
            chats = len([m for m in st.session_state.historico_chat if m['tipo'] == 'chat'])
            st.metric("Perguntas Realizadas", str(chats))
    else:
        st.info("📭 Nenhuma operação registrada ainda.")

# TAB 4: Sobre
with tab4:
    st.subheader("ℹ️ Sobre o Assessor IA")

    st.markdown("""
    ### 💡 O que é o Assessor IA?

    O **Assessor IA** é uma plataforma inteligente de consultoria de investimentos que utiliza
    inteligência artificial para fornecer recomendações personalizadas baseadas no seu perfil
    e histórico financeiro.

    ### 🎯 Funcionalidades

    - **📊 Análise de Carteira**: Análise detalhada de seus investimentos
    - **💬 Chat Inteligente**: Converse com um assessor IA 24/7
    - **📈 Histórico**: Acompanhe todas as suas operações
    - **🔐 Segurança**: Seus dados são protegidos

    ### 🚀 Tecnologias

    - **Streamlit**: Interface web moderna
    - **Ollama + Phi**: IA local e privada
    - **Python**: Backend robusto

    ### 📞 Suporte

    Para dúvidas ou sugestões, entre em contato com nosso time.

    ---

    **Versão:** 1.0.0  
    **Última atualização:** 2026-04-12
    """)

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "✅ Online")
    with col2:
        st.metric("Usuário", "2026")
    with col3:
        st.metric("Modelo IA", "Phi")
