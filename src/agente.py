from datetime import datetime

class AgenteFincanceiro:
    """Agente financeiro para análise de carteiras"""

    def __init__(self):
        """Inicializa o agente"""
        self.historico = []

    def analisar_carteira(self, cliente_id, valor_investimento, base_conhecimento):
        """Analisa uma carteira de investimentos"""
        try:
            cliente = base_conhecimento.obter_cliente(cliente_id)

            if 'erro' in cliente:
                return {
                    'status': 'erro',
                    'mensagem': 'Cliente não encontrado'
                }

            perfil = cliente.get('perfil_risco', 'moderado').lower()

            recomendacao = base_conhecimento.gerar_recomendacao(
                cliente_id=cliente_id,
                valor_investimento=valor_investimento,
                perfil=perfil
            )

            if 'erro' in recomendacao:
                return {
                    'status': 'erro',
                    'mensagem': str(recomendacao['erro'])
                }

            self.historico.append({
                'data': datetime.now(),
                'cliente_id': cliente_id,
                'valor': valor_investimento,
                'perfil': perfil,
                'recomendacao': recomendacao
            })

            return {
                'status': 'sucesso',
                'cliente': cliente['nome'],
                'valor': valor_investimento,
                'perfil': perfil,
                'recomendacao': recomendacao
            }

        except Exception as e:
            return {
                'status': 'erro',
                'mensagem': f'Erro ao analisar carteira: {str(e)}'
            }

    def processar_pergunta(self, pergunta, cliente_id, base_conhecimento):
        """Processa uma pergunta do cliente"""
        try:
            pergunta_lower = pergunta.lower()

            if 'cliente' in pergunta_lower:
                clientes = base_conhecimento.listar_clientes()
                return f"Total de clientes: {len(clientes)}"

            elif 'produto' in pergunta_lower:
                produtos = base_conhecimento.listar_produtos()
                return f"Total de produtos: {len(produtos)}"

            else:
                return "Pergunta não compreendida. Tente novamente."

        except Exception as e:
            return f"Erro ao processar pergunta: {str(e)}"

    def obter_historico(self):
        """Obtém o histórico de análises"""
        return self.historico
