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

        # Carregar perfil do cliente
        perfil_path = self.data_dir / "perfil_investidor.json"
        if perfil_path.exists():
            try:
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    conteudo = f.read().strip()
                    if conteudo:
                        perfil = json.loads(conteudo)
                        cliente_id = perfil.get('cliente_id', 'CLI001')
                        self.clientes[cliente_id] = perfil
            except json.JSONDecodeError as e:
                print(f"Erro ao carregar perfil: {e}")
                self._criar_perfil_padrao()
        else:
            self._criar_perfil_padrao()

        # Carregar transações
        transacoes_path = self.data_dir / "transacoes.csv"
        if transacoes_path.exists():
            try:
                df_transacoes = pd.read_csv(transacoes_path)
                self.transacoes['CLI001'] = df_transacoes.to_dict('records')
            except Exception as e:
                print(f"Erro ao carregar transações: {e}")
                self.transacoes['CLI001'] = []

        # Carregar histórico de atendimento
        historico_path = self.data_dir / "historico_atendimento.csv"
        if historico_path.exists():
            try:
                df_historico = pd.read_csv(historico_path)
                self.historico_atendimento['CLI001'] = df_historico.to_dict('records')
            except Exception as e:
                print(f"Erro ao carregar histórico: {e}")
                self.historico_atendimento['CLI001'] = []

        # Carregar produtos
        produtos_path = self.data_dir / "produtos_financeiros.json"
        if produtos_path.exists():
            try:
                with open(produtos_path, 'r', encoding='utf-8') as f:
                    conteudo = f.read().strip()
                    if conteudo:
                        dados_produtos = json.loads(conteudo)
                        self.produtos = dados_produtos.get('produtos', [])
            except json.JSONDecodeError as e:
                print(f"Erro ao carregar produtos: {e}")
                self._criar_produtos_padrao()
        else:
            self._criar_produtos_padrao()

    def _criar_perfil_padrao(self):
        """Criar perfil padrão se arquivo não existir"""
        perfil = {
            "cliente_id": "CLI001",
            "nome": "João Silva",
            "email": "joao@email.com",
            "dados_pessoais": {
                "idade": 35,
                "profissao": "Engenheiro de Software"
            },
            "situacao_financeira": {
                "renda_mensal": 8000,
                "patrimonio_total": 150000,
                "disponivel_investir": 50000
            },
            "objetivos_investimento": [
                {
                    "objetivo": "Aposentadoria",
                    "prazo_anos": 30,
                    "valor_alvo": 500000,
                    "prioridade": "alta"
                }
            ],
            "perfil_risco": {
                "classificacao": "moderado",
                "tolerancia_queda_percentual": 15,
                "experiencia_investimento": "intermediário"
            },
            "alocacao_atual": {
                "renda_fixa": 60,
                "renda_variavel": 30,
                "alternativas": 10,
                "valor_total_investido": 23500
            },
            "historico_performance": {
                "rentabilidade_acumulada": 3.7,
                "rentabilidade_ano_anterior": 5.2
            }
        }
        self.clientes["CLI001"] = perfil

    def _criar_produtos_padrao(self):
        """Criar produtos padrão se arquivo não existir"""
        self.produtos = [
            {
                "id": "PROD001",
                "nome": "Tesouro Direto IPCA+ 2035",
                "categoria": "Renda Fixa",
                "descricao": "Título público indexado à inflação",
                "rentabilidade_esperada": "IPCA + 5.5%",
                "rentabilidade_historica_12m": 6.2,
                "risco": "muito_baixo",
                "liquidez": "alta",
                "aplicacao_minima": 100,
                "taxa_administracao": 0,
                "publico_alvo": ["conservador", "moderado"]
            },
            {
                "id": "PROD002",
                "nome": "Fundo Multimercado XYZ",
                "categoria": "Fundos",
                "descricao": "Fundo que investe em múltiplos ativos",
                "rentabilidade_esperada": "CDI + 3%",
                "rentabilidade_historica_12m": 8.5,
                "risco": "medio",
                "liquidez": "alta",
                "aplicacao_minima": 1000,
                "taxa_administracao": 1.2,
                "publico_alvo": ["moderado", "agressivo"]
            },
            {
                "id": "PROD003",
                "nome": "ETF IBOVESPA",
                "categoria": "Renda Variável",
                "descricao": "Fundo que replica o índice IBOVESPA",
                "rentabilidade_esperada": "Acompanha IBOVESPA",
                "rentabilidade_historica_12m": 12.3,
                "risco": "alto",
                "liquidez": "muito_alta",
                "aplicacao_minima": 100,
                "taxa_administracao": 0.15,
                "publico_alvo": ["moderado", "agressivo"]
            },
            {
                "id": "PROD004",
                "nome": "CDB Banco XYZ",
                "categoria": "Renda Fixa",
                "descricao": "Certificado de Depósito Bancário",
                "rentabilidade_esperada": "12% ao ano",
                "rentabilidade_historica_12m": 11.8,
                "risco": "baixo",
                "liquidez": "media",
                "aplicacao_minima": 1000,
                "taxa_administracao": 0,
                "publico_alvo": ["conservador", "moderado"]
            },
            {
                "id": "PROD005",
                "nome": "LCI Banco ABC",
                "categoria": "Renda Fixa",
                "descricao": "Letra de Crédito Imobiliário",
                "rentabilidade_esperada": "100% do CDI",
                "rentabilidade_historica_12m": 10.5,
                "risco": "baixo",
                "liquidez": "baixa",
                "aplicacao_minima": 1000,
                "taxa_administracao": 0,
                "publico_alvo": ["conservador", "moderado"]
            }
        ]

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

