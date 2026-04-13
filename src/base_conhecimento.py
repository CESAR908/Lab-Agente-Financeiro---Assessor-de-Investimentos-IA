import json
import os
from datetime import datetime

class BaseConhecimento:
    """Classe para gerenciar a base de conhecimento do sistema"""

    def __init__(self):
        """Inicializa a base de conhecimento"""
        self.clientes = self._inicializar_clientes()
        self.produtos = self._inicializar_produtos()
        self.recomendacoes = self._inicializar_recomendacoes()

    def _inicializar_clientes(self):
        """Inicializa os clientes cadastrados"""
        return [
            {
                'id': 'CLI001',
                'nome': 'João Silva',
                'email': 'joao@email.com',
                'telefone': '(11) 98765-4321',
                'cpf': '123.456.789-00',
                'data_cadastro': '2025-01-15',
                'patrimonio': 50000.00,
                'perfil_risco': 'moderado'
            },
            {
                'id': 'CLI002',
                'nome': 'Pedro Santos',
                'email': 'pedro@email.com',
                'telefone': '(11) 99876-5432',
                'cpf': '987.654.321-00',
                'data_cadastro': '2025-02-10',
                'patrimonio': 100000.00,
                'perfil_risco': 'conservador'
            },
            {
                'id': 'CLI003',
                'nome': 'Maria Garcia',
                'email': 'maria@email.com',
                'telefone': '(11) 97654-3210',
                'cpf': '456.789.123-00',
                'data_cadastro': '2025-03-05',
                'patrimonio': 75000.00,
                'perfil_risco': 'agressivo'
            },
            {
                'id': 'CLI004',
                'nome': 'Carlos Oliveira',
                'email': 'carlos@email.com',
                'telefone': '(11) 96543-2109',
                'cpf': '789.123.456-00',
                'data_cadastro': '2025-03-20',
                'patrimonio': 150000.00,
                'perfil_risco': 'moderado'
            },
            {
                'id': 'CLI005',
                'nome': 'Ana Costa',
                'email': 'ana@email.com',
                'telefone': '(11) 95432-1098',
                'cpf': '321.654.987-00',
                'data_cadastro': '2025-04-01',
                'patrimonio': 200000.00,
                'perfil_risco': 'conservador'
            }
        ]

    def _inicializar_produtos(self):
        """Inicializa os produtos de investimento disponíveis"""
        return [
            {
                'id': 'PROD001',
                'nome': 'CDB Banco XYZ',
                'tipo': 'Renda Fixa',
                'rentabilidade': 12.5,
                'risco': 'Baixo',
                'liquidez': 'Média',
                'valor_minimo': 1000.00,
                'descricao': 'Certificado de Depósito Bancário com rentabilidade pós-fixada'
            },
            {
                'id': 'PROD002',
                'nome': 'LCI Banco ABC',
                'tipo': 'Renda Fixa',
                'rentabilidade': 11.8,
                'risco': 'Baixo',
                'liquidez': 'Baixa',
                'valor_minimo': 5000.00,
                'descricao': 'Letra de Crédito Imobiliário com isenção de IR'
            },
            {
                'id': 'PROD003',
                'nome': 'ETF IBOVESPA',
                'tipo': 'Ações',
                'rentabilidade': 15.2,
                'risco': 'Médio',
                'liquidez': 'Alta',
                'valor_minimo': 100.00,
                'descricao': 'Fundo de índice que acompanha o IBOVESPA'
            },
            {
                'id': 'PROD004',
                'nome': 'Fundo Multimercado',
                'tipo': 'Diversificado',
                'rentabilidade': 13.5,
                'risco': 'Médio',
                'liquidez': 'Média',
                'valor_minimo': 500.00,
                'descricao': 'Fundo que investe em múltiplos mercados'
            },
            {
                'id': 'PROD005',
                'nome': 'Tesouro IPCA+',
                'tipo': 'Renda Fixa',
                'rentabilidade': 10.5,
                'risco': 'Muito Baixo',
                'liquidez': 'Alta',
                'valor_minimo': 100.00,
                'descricao': 'Título público com proteção contra inflação'
            },
            {
                'id': 'PROD006',
                'nome': 'Fundo de Ações',
                'tipo': 'Ações',
                'rentabilidade': 18.0,
                'risco': 'Alto',
                'liquidez': 'Média',
                'valor_minimo': 1000.00,
                'descricao': 'Fundo gerenciado focado em ações de crescimento'
            },
            {
                'id': 'PROD007',
                'nome': 'Fundo Imobiliário',
                'tipo': 'Imóvel',
                'rentabilidade': 9.5,
                'risco': 'Médio',
                'liquidez': 'Média',
                'valor_minimo': 100.00,
                'descricao': 'Fundo que investe em imóveis e gera renda'
            },
            {
                'id': 'PROD008',
                'nome': 'Debêntures',
                'tipo': 'Renda Fixa',
                'rentabilidade': 14.0,
                'risco': 'Médio',
                'liquidez': 'Baixa',
                'valor_minimo': 1000.00,
                'descricao': 'Títulos de dívida emitidos por empresas'
            }
        ]

    def _inicializar_recomendacoes(self):
        """Inicializa as regras de recomendação por perfil"""
        return {
            'conservador': {
                'renda_fixa': 70,
                'acoes': 20,
                'outros': 10,
                'produtos': ['PROD002', 'PROD005', 'PROD001'],
                'descricao': 'Perfil conservador com foco em segurança'
            },
            'moderado': {
                'renda_fixa': 50,
                'acoes': 40,
                'outros': 10,
                'produtos': ['PROD001', 'PROD003', 'PROD004'],
                'descricao': 'Perfil moderado com equilíbrio entre risco e retorno'
            },
            'agressivo': {
                'renda_fixa': 30,
                'acoes': 60,
                'outros': 10,
                'produtos': ['PROD003', 'PROD006', 'PROD004'],
                'descricao': 'Perfil agressivo com foco em crescimento'
            }
        }

    def listar_clientes(self):
        """Lista todos os clientes cadastrados"""
        try:
            return self.clientes
        except Exception as e:
            print(f"Erro ao listar clientes: {str(e)}")
            return []

    def obter_cliente(self, cliente_id):
        """Obtém informações de um cliente específico"""
        try:
            cliente = next((c for c in self.clientes if c['id'] == cliente_id), None)
            return cliente if cliente else {'erro': 'Cliente não encontrado'}
        except Exception as e:
            return {'erro': str(e)}

    def listar_produtos(self):
        """Lista todos os produtos disponíveis"""
        try:
            return self.produtos
        except Exception as e:
            print(f"Erro ao listar produtos: {str(e)}")
            return []

    def obter_produto(self, produto_id):
        """Obtém informações de um produto específico"""
        try:
            produto = next((p for p in self.produtos if p['id'] == produto_id), None)
            return produto if produto else {'erro': 'Produto não encontrado'}
        except Exception as e:
            return {'erro': str(e)}

    def obter_recomendacoes_por_perfil(self, perfil):
        """Obtém as recomendações para um perfil de risco"""
        try:
            perfil_lower = perfil.lower()
            recomendacao = self.recomendacoes.get(perfil_lower)
            return recomendacao if recomendacao else {'erro': 'Perfil não encontrado'}
        except Exception as e:
            return {'erro': str(e)}

    def obter_produtos_recomendados(self, perfil):
        """Obtém os produtos recomendados para um perfil"""
        try:
            recomendacao = self.obter_recomendacoes_por_perfil(perfil)
            if 'erro' in recomendacao:
                return []

            produto_ids = recomendacao.get('produtos', [])
            produtos_recomendados = [p for p in self.produtos if p['id'] in produto_ids]
            return produtos_recomendados
        except Exception as e:
            print(f"Erro ao obter produtos recomendados: {str(e)}")
            return []

    def calcular_alocacao(self, valor_total, perfil):
        """Calcula a alocação de carteira para um valor e perfil"""
        try:
            recomendacao = self.obter_recomendacoes_por_perfil(perfil)
            if 'erro' in recomendacao:
                return {'erro': 'Perfil inválido'}

            alocacao = {
                'renda_fixa': valor_total * (recomendacao['renda_fixa'] / 100),
                'acoes': valor_total * (recomendacao['acoes'] / 100),
                'outros': valor_total * (recomendacao['outros'] / 100),
                'percentuais': {
                    'renda_fixa': recomendacao['renda_fixa'],
                    'acoes': recomendacao['acoes'],
                    'outros': recomendacao['outros']
                }
            }
            return alocacao
        except Exception as e:
            return {'erro': str(e)}

    def gerar_recomendacao(self, cliente_id, valor_investimento, perfil):
        """Gera uma recomendação completa para um cliente"""
        try:
            cliente = self.obter_cliente(cliente_id)
            if 'erro' in cliente:
                return {'erro': 'Cliente não encontrado'}

            alocacao = self.calcular_alocacao(valor_investimento, perfil)
            if 'erro' in alocacao:
                return alocacao

            produtos = self.obter_produtos_recomendados(perfil)

            recomendacao = {
                'cliente': cliente['nome'],
                'valor_investimento': valor_investimento,
                'perfil': perfil,
                'alocacao': alocacao,
                'produtos_recomendados': produtos,
                'data_geracao': datetime.now().isoformat(),
                'status': 'sucesso'
            }
            return recomendacao
        except Exception as e:
            return {'erro': str(e), 'status': 'erro'}

    def buscar_cliente_por_nome(self, nome):
        """Busca um cliente pelo nome"""
        try:
            clientes_encontrados = [c for c in self.clientes if nome.lower() in c['nome'].lower()]
            return clientes_encontrados
        except Exception as e:
            return []

    def buscar_produto_por_tipo(self, tipo):
        """Busca produtos por tipo"""
        try:
            produtos_encontrados = [p for p in self.produtos if tipo.lower() in p['tipo'].lower()]
            return produtos_encontrados
        except Exception as e:
            return []

    def obter_estatisticas(self):
        """Obtém estatísticas da base de conhecimento"""
        try:
            total_patrimonio = sum(c.get('patrimonio', 0) for c in self.clientes)
            patrimonio_medio = total_patrimonio / len(self.clientes) if self.clientes else 0

            stats = {
                'total_clientes': len(self.clientes),
                'total_produtos': len(self.produtos),
                'total_patrimonio': total_patrimonio,
                'patrimonio_medio': patrimonio_medio,
                'rentabilidade_media_produtos': sum(p['rentabilidade'] for p in self.produtos) / len(self.produtos),
                'data_atualizacao': datetime.now().isoformat()
            }
            return stats
        except Exception as e:
            return {'erro': str(e)}

    def adicionar_cliente(self, cliente_data):
        """Adiciona um novo cliente"""
        try:
            novo_cliente = {
                'id': f"CLI{len(self.clientes) + 1:03d}",
                'nome': cliente_data.get('nome'),
                'email': cliente_data.get('email'),
                'telefone': cliente_data.get('telefone'),
                'cpf': cliente_data.get('cpf'),
                'data_cadastro': datetime.now().strftime('%Y-%m-%d'),
                'patrimonio': cliente_data.get('patrimonio', 0),
                'perfil_risco': cliente_data.get('perfil_risco', 'moderado')
            }
            self.clientes.append(novo_cliente)
            return {'status': 'sucesso', 'cliente': novo_cliente}
        except Exception as e:
            return {'status': 'erro', 'erro': str(e)}

    def atualizar_cliente(self, cliente_id, dados_atualizacao):
        """Atualiza dados de um cliente"""
        try:
            cliente = next((c for c in self.clientes if c['id'] == cliente_id), None)
            if not cliente:
                return {'status': 'erro', 'erro': 'Cliente não encontrado'}

            cliente.update(dados_atualizacao)
            return {'status': 'sucesso', 'cliente': cliente}
        except Exception as e:
            return {'status': 'erro', 'erro': str(e)}

    def deletar_cliente(self, cliente_id):
        """Deleta um cliente"""
        try:
            self.clientes = [c for c in self.clientes if c['id'] != cliente_id]
            return {'status': 'sucesso', 'mensagem': 'Cliente deletado'}
        except Exception as e:
            return {'status': 'erro', 'erro': str(e)}
