import requests
import json
from typing import Dict, List, Optional

class AgenteFincanceiro:

    def __init__(self, ollama_url: str = "http://127.0.0.1:11434"):
        self.ollama_url = ollama_url
        self.modelo = "mistral"

    def processar_pergunta(
        self,
        pergunta: str,
        cliente_id: str,
        base_conhecimento
    ) -> str:

        try:
            perfil = base_conhecimento.obter_perfil(cliente_id)
            if not perfil:
                return "Erro: Perfil do cliente não encontrado."

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

        except Exception as e:
            return f"Erro ao processar pergunta: {str(e)}"

    def _construir_contexto(
        self,
        perfil: Dict,
        transacoes: List[Dict],
        historico: List[Dict],
        produtos: List[Dict]
    ) -> str:

        try:
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
- Valor Total: R$ {perfil.get('alocacao_atual', {}).get('valor_total_investido', 0):,.2f}

PERFORMANCE:
- Rentabilidade Acumulada: {perfil.get('historico_performance', {}).get('rentabilidade_acumulada', 0)}%
- Rentabilidade Ano Anterior: {perfil.get('historico_performance', {}).get('rentabilidade_ano_anterior', 0)}%

ÚLTIMAS TRANSAÇÕES:
"""

            if transacoes:
                for transacao in transacoes[-3:]:
                    contexto += f"- {transacao.get('data')}: {transacao.get('tipo', 'N/A').upper()} {transacao.get('produto', 'N/A')} - R$ {transacao.get('valor', 0):,.2f}\n"
            else:
                contexto += "- Nenhuma transação registrada\n"

            return contexto

        except Exception as e:
            return f"Erro ao construir contexto: {str(e)}"

    def _classificar_intent(self, pergunta: str) -> str:

        pergunta_lower = pergunta.lower()

        if any(word in pergunta_lower for word in ['recomend', 'devo investir', 'qual produto', 'melhor', 'alocação']):
            return 'recomendacao'
        elif any(word in pergunta_lower for word in ['como funciona', 'o que é', 'explique', 'diferença']):
            return 'educacao'
        elif any(word in pergunta_lower for word in ['carteira', 'performance', 'como está', 'análise', 'desempenho']):
            return 'analise'
        elif any(word in pergunta_lower for word in ['risco', 'volatilidade', 'queda', 'preocupado', 'assustado']):
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

        if intent == 'analise':
            prompt = f"""{contexto}

PERGUNTA: {pergunta}

Você é um assessor de investimentos profissional. Faça uma análise COMPLETA e ESTRUTURADA da carteira.

RESPONDA EM JSON COM ESTA ESTRUTURA:
{{
  "analise_carteira": {{
    "resumo_geral": "Análise breve da situação atual",
    "pontos_fortes": ["ponto 1", "ponto 2", "ponto 3"],
    "areas_melhoria": ["área 1", "área 2"],
    "recomendacoes": [
      {{
        "acao": "descrição da ação",
        "beneficio": "benefício esperado",
        "prioridade": "alta/média/baixa"
      }}
    ],
    "rentabilidade_esperada": "X% ao ano",
    "proximos_passos": ["passo 1", "passo 2"]
  }}
}}

Seja específico e baseie-se APENAS nos dados fornecidos."""

        elif intent == 'recomendacao':
            prompt = f"""{contexto}

PERGUNTA: {pergunta}

Você é um assessor de investimentos profissional. Recomende produtos ESPECÍFICOS baseado no perfil.

RESPONDA EM JSON COM ESTA ESTRUTURA:
{{
  "recomendacoes": {{
    "alocacao_sugerida": {{
      "renda_fixa": "X%",
      "renda_variavel": "X%",
      "alternativas": "X%"
    }},
    "produtos": [
      {{
        "nome": "Nome do Produto",
        "percentual": "X%",
        "motivo": "Por que recomendo",
        "risco": "baixo/médio/alto",
        "rentabilidade_esperada": "X% ao ano"
      }}
    ],
    "beneficios": ["benefício 1", "benefício 2"],
    "riscos": ["risco 1", "risco 2"],
    "disclaimer": "Esta é uma recomendação educacional"
  }}
}}

Seja específico e baseie-se APENAS nos dados fornecidos."""

        else:
            prompt = f"""{contexto}

PERGUNTA: {pergunta}

Você é um assessor de investimentos profissional. Responda de forma clara, acessível e baseada nos dados fornecidos.

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
                timeout=60
            )

            if response.status_code == 200:
                try:
                    resultado = response.json()
                    return resultado.get('response', 'Desculpe, não consegui gerar uma resposta.')
                except json.JSONDecodeError:
                    return f"Erro ao decodificar resposta: {response.text[:200]}"
            else:
                return f"Erro ao conectar com Ollama: Status {response.status_code}"

        except requests.exceptions.ConnectionError:
            return "⚠️ Ollama não está rodando. Execute em outro terminal: ollama serve"
        except requests.exceptions.Timeout:
            return "⚠️ Timeout ao conectar com Ollama. Verifique se está rodando."
        except Exception as e:
            return f"Erro: {str(e)}"
