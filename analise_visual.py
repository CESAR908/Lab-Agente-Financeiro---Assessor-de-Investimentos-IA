import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def gerar_analise_visual(valor_investimento, perfil_risco, resultado):
    """Gera uma análise visual e formatada da carteira"""

    # Definir perfil de risco
    perfis = {
        "Conservador": {
            "renda_fixa": 70,
            "ações": 20,
            "outros": 10,
            "cor": "#2E7D32"
        },
        "Moderado": {
            "renda_fixa": 50,
            "ações": 40,
            "outros": 10,
            "cor": "#1976D2"
        },
        "Agressivo": {
            "renda_fixa": 30,
            "ações": 60,
            "outros": 10,
            "cor": "#D32F2F"
        }
    }

    perfil = perfis.get(perfil_risco, perfis["Moderado"])

    # Calcular valores
    valor_renda_fixa = valor_investimento * (perfil["renda_fixa"] / 100)
    valor_acoes = valor_investimento * (perfil["ações"] / 100)
    valor_outros = valor_investimento * (perfil["outros"] / 100)

    # Título da análise
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {perfil["cor"]} 0%, rgba(0,0,0,0.1) 100%);
                    padding: 2rem;
                    border-radius: 10px;
                    margin-bottom: 2rem;'>
            <h2 style='color: white; margin: 0;'>📊 Análise Personalizada de Carteira</h2>
            <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
                Recomendação para perfil <strong>{perfil_risco}</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💰 Valor Total",
            f"R$ {valor_investimento:,.2f}",
            delta=None
        )

    with col2:
        st.metric(
            "📈 Renda Fixa",
            f"R$ {valor_renda_fixa:,.2f}",
            f"{perfil['renda_fixa']}%"
        )

    with col3:
        st.metric(
            "📊 Ações",
            f"R$ {valor_acoes:,.2f}",
            f"{perfil['ações']}%"
        )

    with col4:
        st.metric(
            "🎯 Outros",
            f"R$ {valor_outros:,.2f}",
            f"{perfil['outros']}%"
        )

    # Gráfico de pizza (Alocação)
    st.markdown("### 📐 Alocação de Carteira")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Renda Fixa', 'Ações', 'Outros'],
            values=[perfil['renda_fixa'], perfil['ações'], perfil['outros']],
            marker=dict(colors=['#4CAF50', '#2196F3', '#FF9800']),
            textposition='inside',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>%{value}%<extra></extra>'
        )])

        fig_pie.update_layout(
            height=400,
            showlegend=True,
            margin=dict(l=0, r=0, t=0, b=0)
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("#### 📋 Resumo")
        st.markdown(f"""
        **Renda Fixa**  
        R$ {valor_renda_fixa:,.2f}  
        {perfil['renda_fixa']}%

        ---

        **Ações**  
        R$ {valor_acoes:,.2f}  
        {perfil['ações']}%

        ---

        **Outros**  
        R$ {valor_outros:,.2f}  
        {perfil['outros']}%
        """)

    # Produtos recomendados
    st.markdown("### 🎯 Produtos Recomendados")

    produtos = [
        {
            "nome": "CDB Banco XYZ",
            "tipo": "Renda Fixa",
            "rentabilidade": 12.5,
            "valor": valor_renda_fixa * 0.6,
            "risco": "Baixo",
            "icon": "📈"
        },
        {
            "nome": "LCI Banco ABC",
            "tipo": "Renda Fixa",
            "rentabilidade": 11.8,
            "valor": valor_renda_fixa * 0.4,
            "risco": "Baixo",
            "icon": "📊"
        },
        {
            "nome": "ETF IBOVESPA",
            "tipo": "Ações",
            "rentabilidade": 15.2,
            "valor": valor_acoes * 0.7,
            "risco": "Médio",
            "icon": "📉"
        },
        {
            "nome": "Fundo Multimercado",
            "tipo": "Diversificado",
            "rentabilidade": 13.5,
            "valor": valor_acoes * 0.3,
            "risco": "Médio",
            "icon": "🎯"
        }
    ]

    # Tabela de produtos
    df_produtos = pd.DataFrame([
        {
            "Produto": f"{p['icon']} {p['nome']}",
            "Tipo": p['tipo'],
            "Valor": f"R$ {p['valor']:,.2f}",
            "Rentabilidade": f"{p['rentabilidade']}% a.a.",
            "Risco": p['risco']
        }
        for p in produtos
    ])

    st.dataframe(df_produtos, use_container_width=True, hide_index=True)

    # Gráfico de rentabilidade esperada
    st.markdown("### 💹 Projeção de Rentabilidade (12 meses)")

    meses = list(range(1, 13))
    rentabilidade_conservadora = [valor_investimento * (1 + (0.10 * m / 12)) for m in meses]
    rentabilidade_moderada = [valor_investimento * (1 + (0.13 * m / 12)) for m in meses]
    rentabilidade_agressiva = [valor_investimento * (1 + (0.16 * m / 12)) for m in meses]

    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(
        x=meses,
        y=rentabilidade_conservadora,
        mode='lines',
        name='Conservador',
        line=dict(color='#4CAF50', width=2)
    ))

    fig_line.add_trace(go.Scatter(
        x=meses,
        y=rentabilidade_moderada,
        mode='lines',
        name='Moderado',
        line=dict(color='#2196F3', width=2)
    ))

    fig_line.add_trace(go.Scatter(
        x=meses,
        y=rentabilidade_agressiva,
        mode='lines',
        name='Agressivo',
        line=dict(color='#FF9800', width=2)
    ))

    fig_line.update_layout(
        title='Evolução da Carteira',
        xaxis_title='Meses',
        yaxis_title='Valor (R$)',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )

    st.plotly_chart(fig_line, use_container_width=True)

    # Recomendações e dicas
    st.markdown("### 💡 Recomendações Importantes")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"""
        **Seu Perfil: {perfil_risco}**

        - Tolerância a risco: Média
        - Horizonte de investimento: 3-5 anos
        - Diversificação recomendada: Sim
        - Rebalanceamento: A cada 6 meses
        """)

    with col2:
        st.warning(f"""
        **Próximos Passos**

        1. Revisar a carteira a cada 3 meses
        2. Rebalancear se desvios > 5%
        3. Considerar aportes mensais
        4. Monitorar rentabilidade vs. benchmark
        """)

    # Simulador de cenários
    st.markdown("### 🎲 Simulador de Cenários")

    cenarios = {
        "Otimista": 1.18,
        "Base": 1.13,
        "Pessimista": 1.08
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        valor_otimista = valor_investimento * cenarios["Otimista"]
        st.metric(
            "📈 Cenário Otimista",
            f"R$ {valor_otimista:,.2f}",
            f"+{((valor_otimista - valor_investimento) / valor_investimento * 100):.1f}%"
        )

    with col2:
        valor_base = valor_investimento * cenarios["Base"]
        st.metric(
            "➡️ Cenário Base",
            f"R$ {valor_base:,.2f}",
            f"+{((valor_base - valor_investimento) / valor_investimento * 100):.1f}%"
        )

    with col3:
        valor_pessimista = valor_investimento * cenarios["Pessimista"]
        st.metric(
            "📉 Cenário Pessimista",
            f"R$ {valor_pessimista:,.2f}",
            f"+{((valor_pessimista - valor_investimento) / valor_investimento * 100):.1f}%"
        )

    # Histórico de recomendações
    st.markdown("### 📜 Histórico da Análise")

    st.success(f"""
    ✅ **Análise Realizada em:** {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}

    **Cliente:** João Silva  
    **Valor Investido:** R$ {valor_investimento:,.2f}  
    **Perfil de Risco:** {perfil_risco}  
    **Status:** Recomendação Ativa
    """)
