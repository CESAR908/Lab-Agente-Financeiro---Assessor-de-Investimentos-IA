import streamlit as st
import pandas as pd
from datetime import datetime
import json
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import sqlite3

# ⚠️ IMPORTANTE: set_page_config DEVE ser a PRIMEIRA chamada do Streamlit
st.set_page_config(
    page_title="Assessor IA",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Agora importar os outros módulos
from agente import AgenteFincanceiro
from base_conhecimento import BaseConhecimento
from utils import formatar_moeda
from login import show_login, check_login
from analise_visual import gerar_analise_visual

# CSS customizado
st.markdown("""
    <style>
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Verificar login
if not check_login():
    show_login()
    st.stop()

# Se chegou aqui, usuário está logado
try:
    if 'agente' not in st.session_state:
        st.session_state.agente = AgenteFincanceiro()
        st.session_state.base_conhecimento = BaseConhecimento()
        st.session_state.historico_chat = []
        st.session_state.cliente_id = "CLI001"
        st.session_state.carteiras = {}
except Exception as e:
    st.error(f"Erro ao inicializar: {str(e)}")
    st.stop()

# Título e descrição
st.title("💰 Assessor IA - Consultoria de Investimentos")
st.markdown("*Seu assessor de investimentos disponível 24/7 | Powered by Phi AI*")

# ============================================================================
# SIDEBAR - CONFIGURAÇÕES E CLIENTE
# ============================================================================
with st.sidebar:
    st.header("⚙️ Configurações")

    # Logout
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.divider()

    # Seleção de cliente
    try:
        clientes = st.session_state.base_conhecimento.listar_clientes()
        if clientes and isinstance(clientes, list) and len(clientes) > 0:
            if isinstance(clientes[0], dict) and 'id' in clientes[0]:
                cliente_ids = [c['id'] for c in clientes]
                cliente_nomes = {c['id']: c['nome'] for c in clientes}

                cliente_selecionado = st.selectbox(
                    "👤 Selecione um cliente",
                    cliente_ids,
                    format_func=lambda x: cliente_nomes.get(x, x)
                )
                st.session_state.cliente_id = cliente_selecionado

                # Mostrar info do cliente
                cliente_info = next((c for c in clientes if c['id'] == cliente_selecionado), None)
                if cliente_info:
                    st.markdown(f"""
                    **Cliente Selecionado:**
                    - 👤 Nome: {cliente_info['nome']}
                    - 📧 Email: {cliente_info['email']}
                    - 📱 Telefone: {cliente_info['telefone']}
                    - 💼 Patrimônio: R$ {cliente_info.get('patrimonio', 0):,.2f}
                    - 🎯 Perfil: {cliente_info.get('perfil_risco', 'N/A').capitalize()}
                    """)
            else:
                st.warning("⚠️ Formato de clientes inválido")
        else:
            st.info("ℹ️ Nenhum cliente disponível")
    except Exception as e:
        st.error(f"❌ Erro ao carregar clientes: {str(e)}")

    st.divider()

    # Estatísticas
    st.markdown("### 📊 Estatísticas")
    stats = st.session_state.base_conhecimento.obter_estatisticas()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Clientes", stats.get('total_clientes', 0))
    with col2:
        st.metric("📦 Produtos", stats.get('total_produtos', 0))

    st.metric(
        "💵 Patrimônio Total",
        f"R$ {stats.get('total_patrimonio', 0):,.2f}"
    )

# ============================================================================
# ABAS PRINCIPAIS
# ============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard",
    "📈 Análise de Carteira",
    "💬 Chat com Assessor",
    "📜 Histórico",
    "📄 Relatórios",
    "ℹ️ Sobre"
])

# ============================================================================
# TAB 1: DASHBOARD
# ============================================================================
with tab1:
    st.subheader("📊 Dashboard Executivo")

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Total de Operações", len(st.session_state.historico_chat))

    with col2:
        chats = len([m for m in st.session_state.historico_chat if m['tipo'] == 'chat'])
        st.metric("💬 Perguntas", chats)

    with col3:
        analises = len([m for m in st.session_state.historico_chat if m['tipo'] == 'analise'])
        st.metric("📈 Análises", analises)

    with col4:
        st.metric("👤 Cliente Ativo", st.session_state.cliente_id)

    st.divider()

    # Gráfico de atividades
    if st.session_state.historico_chat:
        st.markdown("### 📈 Atividades Recentes")

        df_atividades = pd.DataFrame([
            {
                'Data': msg['data'].strftime('%d/%m'),
                'Hora': msg['data'].strftime('%H:%M'),
                'Tipo': msg['tipo'].upper(),
                'Detalhes': msg.get('pergunta', msg.get('valor', 'N/A'))[:30]
            }
            for msg in st.session_state.historico_chat[-10:]
        ])

        st.dataframe(df_atividades, use_container_width=True, hide_index=True)

        # Gráfico de tipos de operação
        col1, col2 = st.columns(2)

        with col1:
            tipos = pd.DataFrame([
                {'Tipo': msg['tipo'], 'Quantidade': 1}
                for msg in st.session_state.historico_chat
            ]).groupby('Tipo').size()

            fig_tipos = go.Figure(data=[go.Pie(
                labels=tipos.index,
                values=tipos.values,
                marker=dict(colors=['#2196F3', '#4CAF50', '#FF9800'])
            )])
            fig_tipos.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig_tipos, use_container_width=True)

        with col2:
            st.markdown("### 📋 Resumo")
            st.markdown(f"""
            **Total de Operações:** {len(st.session_state.historico_chat)}

            **Análises Realizadas:** {analises}

            **Perguntas Respondidas:** {chats}

            **Taxa de Utilização:** {(len(st.session_state.historico_chat) / 100 * 100):.1f}%
            """)
    else:
        st.info("📭 Nenhuma operação registrada ainda. Comece analisando uma carteira!")

# ============================================================================
# TAB 2: ANÁLISE DE CARTEIRA
# ============================================================================
with tab2:
    st.subheader("📈 Análise de Carteira de Investimentos")

    col1, col2, col3 = st.columns(3)

    with col1:
        valor_investimento = st.number_input(
            "💰 Valor a Investir (R$)",
            min_value=100.0,
            value=1000.0,
            step=100.0
        )

    with col2:
        perfil_risco = st.selectbox(
            "🎯 Perfil de Risco",
            ["Conservador", "Moderado", "Agressivo"]
        )

    with col3:
        horizonte = st.selectbox(
            "📅 Horizonte de Investimento",
            ["Curto Prazo (< 1 ano)", "Médio Prazo (1-5 anos)", "Longo Prazo (> 5 anos)"]
        )

    if st.button("🔍 Analisar Carteira", use_container_width=True, type="primary"):
        with st.spinner("⏳ Analisando sua carteira..."):
            try:
                resultado = st.session_state.agente.analisar_carteira(
                    cliente_id=st.session_state.cliente_id,
                    valor_investimento=valor_investimento,
                    base_conhecimento=st.session_state.base_conhecimento
                )

                if resultado['status'] == 'sucesso':
                    # Gerar análise visual
                    gerar_analise_visual(valor_investimento, perfil_risco, resultado)

                    # Guardar no histórico
                    st.session_state.historico_chat.append({
                        'tipo': 'analise',
                        'data': datetime.now(),
                        'valor': valor_investimento,
                        'perfil': perfil_risco,
                        'horizonte': horizonte,
                        'resultado': str(resultado)
                    })

                    # Guardar carteira
                    st.session_state.carteiras[st.session_state.cliente_id] = {
                        'valor': valor_investimento,
                        'perfil': perfil_risco,
                        'horizonte': horizonte,
                        'data': datetime.now(),
                        'resultado': resultado
                    }
                else:
                    st.error(f"❌ Erro: {resultado.get('mensagem', 'Erro desconhecido')}")

            except Exception as e:
                st.error(f"❌ Erro ao analisar: {str(e)}")

# ============================================================================
# TAB 3: CHAT COM ASSESSOR
# ============================================================================
with tab3:
    st.subheader("💬 Chat com Seu Assessor IA")

    pergunta = st.text_area(
        "Faça sua pergunta",
        placeholder="Digite sua pergunta sobre investimentos, produtos, carteira, etc...",
        height=100
    )

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        enviar = st.button("📤 Enviar Pergunta", use_container_width=True, type="primary")

    with col2:
        limpar = st.button("🗑️ Limpar Chat", use_container_width=True)

    with col3:
        exportar = st.button("📥 Exportar", use_container_width=True)

    if limpar:
        st.session_state.historico_chat = []
        st.rerun()

    if enviar and pergunta:
        with st.spinner("⏳ Processando sua pergunta..."):
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

        for msg in reversed(st.session_state.historico_chat[-10:]):
            if msg['tipo'] == 'chat':
                st.markdown(f"**[{msg['data'].strftime('%d/%m %H:%M:%S')}]**")
                st.write(f"📝 **Pergunta:** {msg['pergunta']}")
                st.write(f"💬 **Resposta:** {msg['resposta']}")
                st.divider()

# ============================================================================
# TAB 4: HISTÓRICO
# ============================================================================
with tab4:
    st.subheader("📜 Histórico de Operações")

    if st.session_state.historico_chat:
        df_historico = pd.DataFrame([
            {
                'Data': msg['data'].strftime('%d/%m/%Y'),
                'Hora': msg['data'].strftime('%H:%M:%S'),
                'Tipo': msg['tipo'].upper(),
                'Detalhes': msg.get('pergunta', msg.get('valor', 'N/A'))[:50]
            }
            for msg in st.session_state.historico_chat
        ])

        st.dataframe(df_historico, use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total de Operações", len(st.session_state.historico_chat))
        with col2:
            chats = len([m for m in st.session_state.historico_chat if m['tipo'] == 'chat'])
            st.metric("💬 Perguntas", chats)
        with col3:
            analises = len([m for m in st.session_state.historico_chat if m['tipo'] == 'analise'])
            st.metric("📈 Análises", analises)
    else:
        st.info("📭 Nenhuma operação registrada ainda.")

# ============================================================================
# TAB 5: RELATÓRIOS
# ============================================================================
with tab5:
    st.subheader("📄 Geração de Relatórios")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Gerar Relatório em PDF", use_container_width=True):
            st.info("📄 Funcionalidade em desenvolvimento...")

    with col2:
        if st.button("📊 Exportar para Excel", use_container_width=True):
            if st.session_state.historico_chat:
                df_export = pd.DataFrame([
                    {
                        'Data': msg['data'].strftime('%d/%m/%Y %H:%M:%S'),
                        'Tipo': msg['tipo'],
                        'Detalhes': msg.get('pergunta', msg.get('valor', 'N/A'))
                    }
                    for msg in st.session_state.historico_chat
                ])

                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_export.to_excel(writer, sheet_name='Histórico', index=False)

                buffer.seek(0)
                st.download_button(
                    label="📥 Baixar Excel",
                    data=buffer.getvalue(),
                    file_name=f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ Nenhum dado para exportar")

    st.divider()

    st.markdown("### 📋 Resumo de Carteiras")

    if st.session_state.carteiras:
        for cliente_id, carteira in st.session_state.carteiras.items():
            st.markdown(f"""
            **Cliente:** {cliente_id}
            - **Valor:** R$ {carteira['valor']:,.2f}
            - **Perfil:** {carteira['perfil']}
            - **Horizonte:** {carteira['horizonte']}
            - **Data:** {carteira['data'].strftime('%d/%m/%Y %H:%M')}
            """)
    else:
        st.info("ℹ️ Nenhuma carteira analisada ainda")

# ============================================================================
# TAB 6: SOBRE
# ============================================================================
with tab6:
    st.subheader("ℹ️ Sobre o Assessor IA")

    st.markdown("""
    ### 💡 O que é o Assessor IA?

    O **Assessor IA** é uma plataforma inteligente de consultoria de investimentos que utiliza
    inteligência artificial para fornecer recomendações personalizadas baseadas no seu perfil
    e histórico financeiro.

    ### 🎯 Funcionalidades

    - **📊 Dashboard Executivo**: Visualize suas operações em tempo real
    - **📈 Análise de Carteira**: Análise detalhada com gráficos interativos
    - **💬 Chat Inteligente**: Converse com um assessor IA 24/7
    - **📜 Histórico Completo**: Acompanhe todas as suas operações
    - **📄 Relatórios**: Exporte dados em Excel
    - **🔐 Segurança**: Seus dados são protegidos

    ### 🚀 Tecnologias

    - **Streamlit**: Interface web moderna e responsiva
    - **Ollama + Phi**: IA local e privada
    - **Plotly**: Gráficos interativos
    - **Pandas**: Manipulação de dados
    - **Python**: Backend robusto

    ### 📊 Recursos Principais

    1. **Análise Visual**: Gráficos de alocação, projeção e cenários
    2. **Recomendações Inteligentes**: Baseadas em perfil de risco
    3. **Simulador de Cenários**: Otimista, Base e Pessimista
    4. **Histórico Detalhado**: Todas as operações registradas
    5. **Exportação de Dados**: Excel e relatórios

    ### 📞 Suporte

    Para dúvidas ou sugestões, entre em contato com nosso time.

    ---

    **Versão:** 2.0.0  
    **Data:** 2026-04-12  
    **Status:** ✅ Produção
    """)

    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Status", "Online")
    with col2:
        st.metric("👤 Usuário", "2026")
    with col3:
        st.metric("🤖 Modelo IA", "Phi")
    with col4:
        st.metric("📈 Versão", "2.0.0")

# ============================================================================
# RODAPÉ
# ============================================================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #999; padding: 2rem 0;'>
    <p>💰 <strong>Assessor IA</strong> - Consultoria de Investimentos Inteligente</p>
    <p>© 2026 | Desenvolvido com ❤️ usando Streamlit + Phi AI</p>
</div>
""", unsafe_allow_html=True)
