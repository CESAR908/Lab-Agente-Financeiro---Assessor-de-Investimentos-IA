import requests
import json
from typing import Dict, List, Optional

class AgenteFincanceiro:

    def __init__(self, ollama_url: str = "http://127.0.0.1:11434"):
        self.ollama_url = ollama_url
        self.modelo = "phi"

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

            prompt = self._construir_prompt(
                pergunta=pergunta,
                contexto=contexto,
                perfil=perfil
            )

            resposta = self._chamar_ollama(prompt)

            return resposta

        except Exception as e:
            return f"Erro ao processar pergunta: {str(e)}"

    def _construir_contexto(
        self,
        perfil: Dict,
        transacoes: List,
        historico: List,
        produtos: List
    ) -> str:

        contexto = f"""
PERFIL DO CLIENTE:
- Nome: {perfil.get('nome', 'N/A')}
- Idade: {perfil.get('idade', 'N/A')}
- Renda Mensal: R$ {perfil.get('renda_mensal', 0):,.2f}
- Patrimônio: R$ {perfil.get('patrimonio', 0):,.2f}
- Perfil de Risco: {perfil.get('perfil_risco', 'N/A')}
- Objetivo: {perfil.get('objetivo', 'N/A')}

TRANSAÇÕES RECENTES:
"""
        for t in transacoes[-5:]:
            contexto += f"- {t.get('data')}: {t.get('tipo')} - R$ {t.get('valor'):,.2f}\n"

        contexto += "\nPRODUTOS DISPONÍVEIS:\n"
        for p in produtos[:5]:
            contexto += f"- {p.get('nome')}: {p.get('descricao')}\n"

        return contexto

    def _construir_prompt(
        self,
        pergunta: str,
        contexto: str,
        perfil: Dict
    ) -> str:

        prompt = f"""Você é um assessor financeiro profissional e experiente.

{contexto}

Cliente pergunta: {pergunta}

Responda de forma:
1. Clara e objetiva
2. Baseada no perfil e histórico do cliente
3. Com recomendações práticas
4. Em português brasileiro

Resposta:"""

        return prompt

    def _chamar_ollama(self, prompt: str) -> str:
        try:
            payload = {
                "model": self.modelo,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                resultado = response.json()
                return resultado.get("response", "Sem resposta do modelo")
            else:
                return f"Erro na API: {response.status_code}"

        except requests.exceptions.Timeout:
            return "Timeout: O modelo demorou muito para responder. Tente novamente."
        except requests.exceptions.ConnectionError:
            return "Erro de conexão com Ollama. Verifique se está rodando em http://127.0.0.1:11434"
        except Exception as e:
            return f"Erro ao chamar Ollama: {str(e)}"

    def analisar_carteira(
        self,
        cliente_id: str,
        valor_investimento: float,
        base_conhecimento
    ) -> Dict:

        try:
            perfil = base_conhecimento.obter_perfil(cliente_id)
            produtos = base_conhecimento.obter_produtos()

            contexto = f"""
ANÁLISE DE CARTEIRA:
- Cliente: {perfil.get('nome')}
- Valor a Investir: R$ {valor_investimento:,.2f}
- Perfil de Risco: {perfil.get('perfil_risco')}
- Patrimônio Atual: R$ {perfil.get('patrimonio', 0):,.2f}
- Objetivo: {perfil.get('objetivo')}

PRODUTOS DISPONÍVEIS:
"""
            for p in produtos:
                contexto += f"- {p.get('nome')}: Rentabilidade {p.get('rentabilidade')}% ao ano\n"

            prompt = f"""{contexto}

Baseado neste perfil e valor de investimento, recomende uma alocação de carteira.
Forneça em formato JSON com as recomendações."""

            resposta = self._chamar_ollama(prompt)

            try:
                recomendacoes = json.loads(resposta)
            except:
                recomendacoes = {"recomendacao": resposta}

            return {
                "status": "sucesso",
                "valor_investimento": valor_investimento,
                "recomendacoes": recomendacoes,
                "perfil": perfil.get('perfil_risco')
            }

        except Exception as e:
            return {
                "status": "erro",
                "mensagem": str(e)
            }
