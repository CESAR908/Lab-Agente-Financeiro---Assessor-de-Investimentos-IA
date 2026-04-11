# src/base_conhecimento.py
import json
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class BaseConhecimento:
    """
    Mini‑banco de dados em memória que lê arquivos JSON/CSV da pasta ``data/``.
    Agora suporta **vários clientes** – cada CSV deve conter a coluna ``cliente_id``.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.clientes: Dict[str, Dict] = {}
        self.produtos: List[Dict] = []
        self.transacoes: Dict[str, List[Dict]] = {}
        self.historico_atendimento: Dict[str, List[Dict]] = {}

        self._carregar_dados()

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------
    def _carregar_dados(self):
        """Carrega todos os arquivos presentes em ``self.data_dir``."""

        # ---- 1️⃣ Perfil (JSON) -------------------------------------------------
        perfil_path = self.data_dir / "perfil_investidor.json"
        if perfil_path.exists():
            with open(perfil_path, "r", encoding="utf-8") as f:
                perfil = json.load(f)
                cliente_id = perfil.get("cliente_id", "CLI001")
                self.clientes[cliente_id] = perfil

        # ---- 2️⃣ Transações (CSV) ---------------------------------------------
        transacoes_path = self.data_dir / "transacoes.csv"
        if transacoes_path.exists():
            df = pd.read_csv(transacoes_path, dtype=str)  # tudo como string primeiro
            # Caso não exista a coluna cliente_id, assumimos que todos são CLI001
            if "cliente_id" not in df.columns:
                df["cliente_id"] = "CLI001"
            # Converte colunas numéricas
            numeric_cols = ["valor"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

            for cliente_id, group in df.groupby("cliente_id"):
                self.transacoes[cliente_id] = (
                    group.drop(columns=["cliente_id"]).to_dict("records")
                )

        # ---- 3️⃣ Histórico de atendimento (CSV) ---------------------------------
        historico_path = self.data_dir / "historico_atendimento.csv"
        if historico_path.exists():
            df = pd.read_csv(historico_path, dtype=str)
            if "cliente_id" not in df.columns:
                df["cliente_id"] = "CLI001"
            for cliente_id, group in df.groupby("cliente_id"):
                self.historico_atendimento[cliente_id] = (
                    group.drop(columns=["cliente_id"]).to_dict("records")
                )

        # ---- 4️⃣ Produtos (JSON) ------------------------------------------------
        produtos_path = self.data_dir / "produtos_financeiros.json"
        if produtos_path.exists():
            with open(produtos_path, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.produtos = dados.get("produtos", [])

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def obter_perfil(self, cliente_id: str) -> Optional[Dict]:
        return self.clientes.get(cliente_id)

    def obter_transacoes(self, cliente_id: str) -> List[Dict]:
        return self.transacoes.get(cliente_id, [])

    def obter_historico_atendimento(self, cliente_id: str) -> List[Dict]:
        return self.historico_atendimento.get(cliente_id, [])

    def obter_produtos(self) -> List[Dict]:
        return self.produtos

    def obter_produto(self, produto_id: str) -> Optional[Dict]:
        for p in self.produtos:
            if p.get("id") == produto_id:
                return p
        return None

    def listar_clientes(self) -> List[str]:
        """Retorna a lista de IDs de clientes conhecidos (ex.: ['CLI001', 'CLI002'])."""
        return list(self.clientes.keys())

    # ------------------------------------------------------------------
    # Helpers para inserir novo cliente (útil para futuras telas)
    # ------------------------------------------------------------------
    def salvar_cliente(self, cliente_data: Dict) -> str:
        """Adiciona um cliente na memória e devolve o ID gerado."""
        cliente_id = f"CLI{len(self.clientes) + 1:03d}"
        cliente_data["cliente_id"] = cliente_id
        self.clientes[cliente_id] = cliente_data
        self.transacoes[cliente_id] = []
        self.historico_atendimento[cliente_id] = []
        return cliente_id
