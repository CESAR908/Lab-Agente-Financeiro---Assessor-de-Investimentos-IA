import json
import re
from datetime import datetime

class AgenteOtimizado:
    """Agente de investimentos otimizado com respostas em português claro"""

    def __init__(self):
        """Inicializa o agente"""
        self.historico = []

    def classificar_cliente(self, base_conhecimento, cliente_id):
        """Classifica o cliente como novice, intermediário ou expert"""
        try:
            cliente = base_conhecimento.obter_cliente(cliente_id)
            perfil = cliente.get('perfil_risco', 'moderado').lower()

            if perfil == 'conservador':
                return 'Iniciante'
            elif perfil == 'moderado':
                return 'Intermediário'
            else:
                return 'Avançado'
        except:
            return 'Intermediário'

    def gerar_recomendacao_simples(self, valor, perfil, base_conhecimento):
        """Gera recomendação simples e clara"""
        recomendacoes = {
            'Conservador': {
                'alocacao': 'Renda Fixa 70% | Ações 20% | Outros 10%',
                'produtos': [
                    'CDB Banco XYZ (Rentabilidade: 12,5% a.a.)',
                    'Tesouro IPCA+ (Rentabilidade: 10,5% a.a.)',
                    'LCI Banco ABC (Rentabilidade: 11,8% a.a.)'
                ],
                'risco': 'Baixo',
                'horizonte': '3-5 anos'
            },
            'Moderado': {
                'alocacao': 'Renda Fixa 50% | Ações 40% | Outros 10%',
                'produtos': [
                    'CDB Banco XYZ (Rentabilidade: 12,5% a.a.)',
                    'ETF IBOVESPA (Rentabilidade: 15,2% a.a.)',
                    'Fundo Multimercado (Rentabilidade: 13,5% a.a.)'
                ],
                'risco': 'Médio',
                'horizonte': '3-5 anos'
            },
            'Agressivo': {
                'alocacao': 'Renda Fixa 30% | Ações 60% | Outros 10%',
                'produtos': [
                    'ETF IBOVESPA (Rentabilidade: 15,2% a.a.)',
                    'Fundo de Ações (Rentabilidade: 18,0% a.a.)',
                    'Fundo Multimercado (Rentabilidade: 13,5% a.a.)'
                ],
                'risco': 'Alto',
                'horizonte': '5+ anos'
            }
        }
        return recomendacoes.get(perfil, recomendacoes['Moderado'])

    def extrair_valor_pergunta(self, pergunta):
        """Extrai valor numérico da pergunta"""
        try:
            numeros = re.findall(r'\d+', pergunta)
            if numeros:
                return float(numeros[0])
        except:
            pass
        return 0.0

    def processar_pergunta_investimento(self, pergunta, valor, perfil, base_conhecimento):
        """Processa perguntas sobre investimento de forma clara"""
        pergunta_lower = pergunta.lower().strip()

        if valor == 0:
            valor_extraido = self.extrair_valor_pergunta(pergunta)
            if valor_extraido > 0:
                valor = valor_extraido
            else:
                valor = 1000.0

        if any(palavra in pergunta_lower for palavra in ['investir', 'aplicar', 'quero', 'gostaria', 'preciso']):
            recomendacao = self.gerar_recomendacao_simples(valor, perfil, base_conhecimento)

            resposta = f"""
🎯 **RECOMENDAÇÃO DE INVESTIMENTO**

💰 **Valor a Investir:** R$ {valor:,.2f}
📊 **Seu Perfil:** {perfil}
⭐ **Classificação:** {self.classificar_cliente(base_conhecimento, 'CLI001')}

---

📐 **ALOCAÇÃO RECOMENDADA:**
{recomendacao['alocacao']}

---

🏆 **PRODUTOS RECOMENDADOS:**
"""
            for i, produto in enumerate(recomendacao['produtos'], 1):
                valor_produto = valor * (0.5 if i == 1 else 0.25)
                resposta += f"\n{i}. {produto}\n   💵 Valor sugerido: R$ {valor_produto:,.2f}"

            resposta += f"""

---

📈 **PROJEÇÃO (12 MESES):**
• Cenário Conservador: R$ {valor * 1.10:,.2f}
• Cenário Base: R$ {valor * 1.13:,.2f}
• Cenário Otimista: R$ {valor * 1.18:,.2f}

---

⚠️ **INFORMAÇÕES IMPORTANTES:**
• Risco: {recomendacao['risco']}
• Horizonte de Investimento: {recomendacao['horizonte']}
• Rebalanceamento recomendado: A cada 6 meses
• Revisão da carteira: A cada 3 meses

---

💡 **PRÓXIMOS PASSOS:**
1. Revisar a carteira a cada 3 meses
2. Rebalancear se desvios > 5%
3. Considerar aportes mensais
4. Monitorar rentabilidade vs. benchmark
"""
            return resposta.strip()

        elif any(palavra in pergunta_lower for palavra in ['produto', 'fundo', 'qual', 'quais']):
            produtos = base_conhecimento.listar_produtos()
            resposta = "🏦 **PRODUTOS DISPONÍVEIS:**\n\n"

            for produto in produtos[:5]:
                resposta += f"""
📦 **{produto['nome']}**
• Tipo: {produto['tipo']}
• Rentabilidade: {produto['rentabilidade']}% a.a.
• Risco: {produto['risco']}
• Valor Mínimo: R$ {produto['valor_minimo']:,.2f}
• Descrição: {produto['descricao']}

"""
            return resposta.strip()

        elif 'risco' in pergunta_lower:
            resposta = f"""
🎯 **ANÁLISE DE RISCO - PERFIL {perfil.upper()}**

📊 **Seu Perfil de Risco:** {perfil}

"""
            if perfil == 'Conservador':
                resposta += """
✅ **Características:**
• Prioriza segurança do capital
• Aceita rentabilidades menores
• Baixa tolerância a perdas
• Horizonte: 3-5 anos

📈 **Alocação Sugerida:**
• Renda Fixa: 70%
• Ações: 20%
• Outros: 10%

💡 **Recomendação:** Foque em CDB, Tesouro e LCI
"""
            elif perfil == 'Moderado':
                resposta += """
✅ **Características:**
• Equilíbrio entre risco e retorno
• Aceita flutuações moderadas
• Tolerância média a perdas
• Horizonte: 3-5 anos

📈 **Alocação Sugerida:**
• Renda Fixa: 50%
• Ações: 40%
• Outros: 10%

💡 **Recomendação:** Diversifique entre CDB, ETF e Fundos
"""
            else:
                resposta += """
✅ **Características:**
• Busca máximo crescimento
• Aceita flutuações grandes
• Alta tolerância a perdas
• Horizonte: 5+ anos

📈 **Alocação Sugerida:**
• Renda Fixa: 30%
• Ações: 60%
• Outros: 10%

💡 **Recomendação:** Foque em Ações e Fundos de Crescimento
"""
            return resposta.strip()

        elif any(palavra in pergunta_lower for palavra in ['rentabilidade', 'retorno', 'ganho', 'lucro']):
            resposta = f"""
💹 **PROJEÇÃO DE RENTABILIDADE**

💰 **Valor Investido:** R$ {valor:,.2f}

---

📊 **CENÁRIOS (12 MESES):**

🟢 **Cenário Otimista (+18%):**
Valor Final: R$ {valor * 1.18:,.2f}
Ganho: R$ {valor * 0.18:,.2f}

🟡 **Cenário Base (+13%):**
Valor Final: R$ {valor * 1.13:,.2f}
Ganho: R$ {valor * 0.13:,.2f}

🔴 **Cenário Pessimista (+8%):**
Valor Final: R$ {valor * 1.08:,.2f}
Ganho: R$ {valor * 0.08:,.2f}

---

⚠️ **Observações:**
• Estes são cenários estimados
• Rentabilidade passada não garante futura
• Mercado pode ter volatilidade
• Rebalanceamento é importante
"""
            return resposta.strip()

        else:
            resposta = f"""
📋 **INFORMAÇÕES SOBRE INVESTIMENTO**

Você perguntou: "{pergunta}"

💰 **Valor a Investir:** R$ {valor:,.2f}
🎯 **Seu Perfil:** {perfil}

---

Para melhor ajudá-lo, você pode perguntar sobre:
• Produtos de investimento disponíveis
• Recomendação de carteira
• Análise de risco
• Projeção de rentabilidade
• Alocação de recursos

Qual dessas opções você gostaria de explorar?
"""
            return resposta.strip()

    def processar_pergunta_geral(self, pergunta, base_conhecimento):
        """Processa perguntas gerais sobre investimentos"""
        pergunta_lower = pergunta.lower()

        if 'cliente' in pergunta_lower:
            clientes = base_conhecimento.listar_clientes()
            resposta = f"👥 **CLIENTES CADASTRADOS:** {len(clientes)}\n\n"
            for cliente in clientes[:5]:
                resposta += f"• {cliente['nome']} (ID: {cliente['id']})\n"
            return resposta.strip()

        elif 'produto' in pergunta_lower:
            produtos = base_conhecimento.listar_produtos()
            resposta = f"📦 **PRODUTOS DISPONÍVEIS:** {len(produtos)}\n\n"
            for produto in produtos[:5]:
                resposta += f"• {produto['nome']} - {produto['rentabilidade']}% a.a.\n"
            return resposta.strip()

        else:
            return """
👋 **Olá! Sou seu Assessor IA**

Estou aqui para ajudá-lo com:
✅ Análise de carteira de investimentos
✅ Recomendações personalizadas
✅ Informações sobre produtos
✅ Projeção de rentabilidade
✅ Dicas de investimento

Como posso ajudá-lo hoje?
"""
