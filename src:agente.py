# src/agente.py
import requests
from typing import Dict, List, Optional

# ----------------------------------------------------------------------
# Classe pública – nome correto
# ----------------------------------------------------------------------
class AgenteFinanceiro:
    """
    Wrapper que envia a pergunta ao modelo Ollama, monta o contexto a partir da
    base de conhecimento e devolve a resposta.
    """

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.modelo = "mistral"

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def processar_pergunta(
        self,
        pergunta: str,
        cliente_id: str,
        base_conhecimento: "BaseConhecimento",   # forward reference para evitar import circular
    ) -> str:
        """
        Monta o prompt, classifica a intenção e chama o Ollama.
        """
        # 1️⃣ Dados do cliente
        perfil = base_conhecimento.obter_perfil(cliente_id)
        transacoes = base_conhecimento.obter_transacoes(cliente_id)
        historico = base_conhecimento.obter_historico_atendimento(cliente_id)
        produtos = base_conhecimento.obter_produtos()

        # 2️⃣ Contexto – limitamos a 5 transações mais recentes
        contexto = self._construir_contexto(
            perfil=perfil,
            transacoes=transacoes[-5:],          # apenas as 5 mais recentes
            historico=historico,
            produtos=produtos,
        )

        # 3️⃣ Classificação de intent (regra simples)
        intent = self._classificar_intent(pergunta)

        # 4️⃣ Prompt completo
        prompt = self._gerar_prompt(
            pergunta=pergunta,
            contexto=contexto,
            intent=intent,
            perfil=perfil,
        )

        # 5️⃣ Chamada ao Ollama (com pequeno retry)
        return self._chamar_ollama(prompt)


    # ------------------------------------------------------------------
    # Métodos auxiliares (privados)
    # ------------------------------------------------------------------
    def _construir_contexto(
        self,
        perfil: Dict,
        transacoes: List[Dict],
        historico: List[Dict],
        produtos: List[Dict],
    ) -> str:
        """Retorna uma string formatada com as informações mais relevantes."""
        nome = perfil.get('nome', 'N/A')
        idade = perfil.get('dados_pessoais', {}).get('idade', 'N/A')
        profissao = perfil.get('dados_pessoais', {}).get('profissao', 'N/A')
        renda = perfil.get('situacao_financeira', {}).get('renda_mensal', 0)
        patrimonio = perfil.get('situacao_financeira', {}).get('patrimonio_total', 0)
        risco = perfil.get('perfil_risco', {}).get('classificacao', 'N/A').upper()
        tolerancia = perfil.get('perfil_risco', {}).get('tolerancia_queda_percentual', 'N/A')

        contexto = f"""PERFIL DO CLIENTE:
- Nome: {nome}
- Idade: {idade} anos
- Profissão: {profissao}
- Renda Mensal: R$ {renda:,.2f}
- Patrimônio: R$ {patrimonio:,.2f}
- Perfil de Risco: {risco}
- Tolerância a Queda: {tolerancia}%

OBJETIVOS:
"""

        for obj in perfil.get('objetivos_investimento', []):
            objetivo = obj.get('objetivo', 'N/A')
            prazo = obj.get('prazo_anos', 'N/A')
            valor = obj.get('valor_alvo', 0)
            contexto += f"- {objetivo} ({prazo} anos): R$ {valor:,.2f}\n"

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
            for t in transacoes:
                data = t.get('data')
                tipo = t.get('tipo', '').upper()
                produto = t.get('produto')
                valor = t.get('valor', 0)
                contexto += f"- {data}: {tipo} {produto} - R$ {valor:,.2f}\n"
        else:
            contexto += "- Nenhuma transação recente.\n"

        # (Caso queira, pode acrescentar um pequeno resumo de `historico` ou `produtos`.)

        return contexto


    def _classificar_intent(self, pergunta: str) -> str:
        """Retorna a intenção de alto nível usando palavras‑chave."""
        q = pergunta.lower()

        # Mapa de intent → conjunto de palavras‑chave
        intents = {
            "recomendacao": {"recomend", "devo investir", "qual produto", "melhor", "sugest", "ideal"},
            "educacao": {"como funciona", "o que é", "explique", "diferen", "significado"},
            "analise": {"carteira", "performance", "como está", "análise", "rendimento"},
            "risco": {"risco", "volatilidade", "queda", "preocup", "segur", "conservadora"},
        }

        for intent, keywords in intents.items():
            if any(kw in q for kw in keywords):
                return intent

        return "geral"


    def _gerar_prompt(
        self,
        pergunta: str,
        contexto: str,
        intent: str,
        perfil: Dict,
    ) -> str:
        """
        Monta o prompt final que será enviado ao Ollama.
        ``intent`` ainda não altera o prompt, mas está lá para possíveis
        personalizações futuras.
        """
        return f"""{contexto}
PERGUNTA: {pergunta}
Você é um assessor de investimentos profissional. Responda baseado APENAS nos dados acima.

INSTRUÇÕES:
1. Baseie sua resposta nos dados fornecidos.
2. Não invente rentabilidades ou números inexistentes.
3. Considere o perfil de risco do cliente.
4. Seja claro e acessível.
5. Inclua disclaimer se for recomendação.

Responda de forma concisa e profissional."""


    def _chamar_ollama(self, prompt: str) -> str:
        """Chama o endpoint `/api/generate` do Ollama com pequeno retry."""
        max_tries = 2
        for attempt in range(1, max_tries + 1):
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.modelo,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.7,
                    },
                    timeout=30,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "Desculpe, não consegui gerar uma resposta.")
                else:
                    # Erro HTTP → levanta para retry ou falha final
                    raise RuntimeError(f"Ollama retornou {response.status_code}")
            except (requests.exceptions.ConnectionError, RuntimeError):
                if attempt == max_tries:
                    return (
                        "Erro ao conectar com Ollama. Verifique se o serviço está rodando "
                        "em http://localhost:11434 e tente novamente."
                    )
                # pequeno delay antes da tentativa seguinte
                import time
                time.sleep(0.5)
            except Exception as exc:
                return f"Erro inesperado: {str(exc)}"
