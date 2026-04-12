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
        
        # ✅ VERIFICAÇÃO CRÍTICA
        if perfil is None:
            clientes = base_conhecimento.listar_clientes()
            return f"❌ **ERRO**: Perfil do cliente '{cliente_id}' não encontrado!\n\n**Clientes disponíveis**: {clientes if clientes else 'Nenhum'}\n\n**Solução**: Verifique se `data/perfil_investidor.json` existe."
        
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

        if transacoes:
            for transacao in transacoes[-3:]:
                contexto += f"- {transacao.get('data')}: {transacao.get('tipo').upper()} {transacao.get('produto')} - R$ {transacao.get('valor'):,.2f}\n"
        else:
            contexto += "- Nenhuma transação registrada\n"

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
            return "⚠️ Ollama não está rodando em http://localhost:11434"
        except Exception as e:
            return f"Erro: {str(e)}"

