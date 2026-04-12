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

  
