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


import requests
import json
from typing import Dict, List, Optional

class AgenteFincanceiro:

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.modelo = "mistral"

    def processar_pergunta(
        self,
        pergunta: str,
        cliente_id: str,
        base_conhecimento
    ) -> str:

        perfil = base_conhecimento.obter_perfil(cliente_id)
        transacoes = base_conhecimento.obter_transacoes(cliente_id)
        historico = base_conhecimento.obter_historico_atendimento(cliente_id)
        produtos = base_conhecimento.obter_produtos()

        contexto = self._construir_contexto(
            perfil=perfil,
            transacoes=transacoes,
            historico=historico,
            produtos=produtos
        )

        intent = self._classificar_intent(pergunta)

        prompt = self._gerar_prompt(
            pergunta=pergunta,
            contexto=contexto,
            intent=intent,
            perfil=perfil
        )

        resposta = self._chamar_ollama(prompt)

        return resposta

    def _construir_contexto(
        self,
        perfil: Dict,
        transacoes: List[Dict],
        historico: List[Dict],
        produtos: List[Dict]
    ) -> str:

        contexto = f"""
PERFIL DO CLIENTE:
- Nome: {perfil.get('nome', 'N/A')}
- Idade: {perfil.get('dados_pessoais', {}).get('idade', 'N/A')} anos
- Profissão: {perfil.get('dados_pessoais', {}).get('profissao', 'N/A')}
- Renda Mensal: R$ {perfil.get('situacao_financeira', {}).get('renda_mensal', 0):,.2f}
- Patrimônio: R$ {perfil.get('situacao_financeira', {}).get('patrimonio_total', 0):,.2f}
- Perfil de Risco: {perfil.get('perfil_risco', {}).get('classificacao', 'N/A').upper()}
- Tolerância a Queda: {perfil.get('perfil_risco', {}).get('tolerancia_queda_percentual', 'N/A')}%

OBJETIVOS:
"""

        for obj in perfil.get('objetivos_investimento', []):
            contexto += f"- {obj.get('objetivo', 'N/A')} ({obj.get('prazo_anos', 'N/A')} anos): R$ {obj.get('valor_alvo', 0):,.2f}\n"

        contexto += f"""
ALOCAÇÃO ATUAL:
- Renda Fixa: {perfil.get('alocacao_atual', {}).get('renda_fixa', 0)}%
- Renda Variável: {perfil.get('alocacao_atual', {}).get('renda_variavel', 0)}%
- Alternativas: {perfil.get('alocacao_atual', {}).get('alternativas', 0)}%

PERFORMANCE:
- Rentabilidade Acumulada: {perfil.get('historico_performance', {}).get('rentabilidade_acumulada', 0)}%

ÚLTIMAS TRANSAÇÕES:
"""

        for transacao in transacoes[-3:]:
            contexto += f"- {transacao.get('data')}: {transacao.get('tipo').upper()} {transacao.get('produto')} - R$ {transacao.get('valor'):,.2f}\n"

        return contexto

    def _classificar_intent(self, pergunta: str) -> str:

        pergunta_lower = pergunta.lower()

        if any(word in pergunta_lower for word in ['recomend', 'devo investir', 'qual produto', 'melhor']):
            return 'recomendacao'
        elif any(word in pergunta_lower for word in ['como funciona', 'o que é', 'explique', 'diferença']):
            return 'educacao'
        elif any(word in pergunta_lower for word in ['carteira', 'performance', 'como está', 'análise']):
            return 'analise'
        elif any(word in pergunta_lower for word in ['risco', 'volatilidade', 'queda', 'preocupado']):
            return 'risco'
        else:
            return 'geral'

    def _gerar_prompt(
        self,
        pergunta: str,
        contexto: str,
        intent: str,
        perfil: Dict
    ) -> str:

        prompt = f"""{contexto}

PERGUNTA: {pergunta}

Você é um assessor de investimentos profissional. Responda baseado APENAS nos dados acima.

INSTRUÇÕES:
1. Sempre baseie sua resposta nos dados fornecidos
2. Nunca invente informações ou rentabilidades
3. Considere o perfil de risco do cliente
4. Seja claro e acessível
5. Inclua disclaimer se for recomendação

Responda de forma concisa e profissional."""

        return prompt

    def _chamar_ollama(self, prompt: str) -> str:

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.modelo,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7
                },
                timeout=30
            )

            if response.status_code == 200:
                resultado = response.json()
                return resultado.get('response', 'Desculpe, não consegui gerar uma resposta.')
            else:
                return f"Erro ao conectar com Ollama: {response.status_code}"

        except requests.exceptions.ConnectionError:
            return "Erro: Não consegui conectar com Ollama. Verifique se está rodando em http://localhost:11434"
        except Exception as e:
            return f"Erro: {str(e)}"
        
import json
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path

class BaseConhecimento:

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.clientes = {}
        self.produtos = []
        self.transacoes = {}
        self.historico_atendimento = {}

        self._carregar_dados()

    def _carregar_dados(self):

        perfil_path = self.data_dir / "perfil_investidor.json"
        if perfil_path.exists():
            with open(perfil_path, 'r', encoding='utf-8') as f:
                perfil = json.load(f)
                cliente_id = perfil.get('cliente_id', 'CLI001')
                self.clientes[cliente_id] = perfil

        transacoes_path = self.data_dir / "transacoes.csv"
        if transacoes_path.exists():
            df_transacoes = pd.read_csv(transacoes_path)
            self.transacoes['CLI001'] = df_transacoes.to_dict('records')

        historico_path = self.data_dir / "historico_atendimento.csv"
        if historico_path.exists():
            df_historico = pd.read_csv(historico_path)
            self.historico_atendimento['CLI001'] = df_historico.to_dict('records')

        produtos_path = self.data_dir / "produtos_financeiros.json"
        if produtos_path.exists():
            with open(produtos_path, 'r', encoding='utf-8') as f:
                dados_produtos = json.load(f)
                self.produtos = dados_produtos.get('produtos', [])

    def obter_perfil(self, cliente_id: str) -> Optional[Dict]:
        return self.clientes.get(cliente_id)

    def obter_transacoes(self, cliente_id: str) -> List[Dict]:
        return self.transacoes.get(cliente_id, [])

    def obter_historico_atendimento(self, cliente_id: str) -> List[Dict]:
        return self.historico_atendimento.get(cliente_id, [])

    def obter_produtos(self) -> List[Dict]:
        return self.produtos

    def obter_produto(self, produto_id: str) -> Optional[Dict]:
        for produto in self.produtos:
            if produto.get('id') == produto_id:
                return produto
        return None

    def listar_clientes(self) -> List[str]:
        return list(self.clientes.keys())

    def salvar_cliente(self, cliente_data: Dict) -> str:
        cliente_id = f"CLI{len(self.clientes) + 1:03d}"
        cliente_data['cliente_id'] = cliente_id
        self.clientes[cliente_id] = cliente_data
        self.transacoes[cliente_id] = []
        self.historico_atendimento[cliente_id] = []
        return cliente_id

def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def formatar_percentual(valor: float) -> str:
    return f"{valor:.2f}%"

def classificar_risco(score: int) -> str:
    if score < 30:
        return "Muito Baixo"
    elif score < 50:
        return "Baixo"
    elif score < 70:
        return "Moderado"
    elif score < 85:
        return "Alto"
    else:
        return "Muito Alto"

