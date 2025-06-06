import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from calendar import monthrange

from .database_manager import DatabaseManager
from .finance_models import (
    ContaCorrente, CartaoCredito, Transacao, Parcelamento, ResumoFinanceiro,
    TipoTransacao, StatusTransacao, TipoConta, BandeiraCartao
)

class FinanceClient:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.fallback_file = Path("data/finance_data.json")
        self.fallback_file.parent.mkdir(exist_ok=True)
        
        # Collections
        self.contas_collection = "contas_correntes"
        self.cartoes_collection = "cartoes_credito"
        self.transacoes_collection = "transacoes"
        
        # Ensure indexes exist
        self._create_indexes()

    def _create_indexes(self):
        """Cria índices para otimizar as consultas"""
        if self.db_manager.is_connected():
            try:
                # Índices para contas
                self.db_manager.collection(self.contas_collection).create_index("id", unique=True)
                self.db_manager.collection(self.contas_collection).create_index("compartilhado_com_alzi")
                
                # Índices para cartões
                self.db_manager.collection(self.cartoes_collection).create_index("id", unique=True)
                self.db_manager.collection(self.cartoes_collection).create_index("conta_vinculada_id")
                self.db_manager.collection(self.cartoes_collection).create_index("compartilhado_com_alzi")
                
                # Índices para transações
                self.db_manager.collection(self.transacoes_collection).create_index("id", unique=True)
                self.db_manager.collection(self.transacoes_collection).create_index("data_transacao")
                self.db_manager.collection(self.transacoes_collection).create_index("conta_id")
                self.db_manager.collection(self.transacoes_collection).create_index("cartao_id")
                self.db_manager.collection(self.transacoes_collection).create_index("compartilhado_com_alzi")
                self.db_manager.collection(self.transacoes_collection).create_index("categoria")
                
            except Exception as e:
                print(f"Aviso: Não foi possível criar índices: {e}")

    def _load_fallback_data(self) -> Dict[str, List[Dict]]:
        """Carrega dados do arquivo JSON de fallback"""
        if self.fallback_file.exists():
            try:
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"contas": [], "cartoes": [], "transacoes": []}

    def _save_fallback_data(self, data: Dict[str, List[Dict]]):
        """Salva dados no arquivo JSON de fallback"""
        try:
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar dados de fallback: {e}")

    def _generate_id(self) -> str:
        """Gera um ID único"""
        return str(uuid.uuid4())

    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        return datetime.now().isoformat()

    # CRUD - Contas Correntes
    def criar_conta(self, nome: str, banco: str, agencia: str, conta: str, 
                   tipo: TipoConta, saldo_inicial: float, 
                   compartilhado_com_alzi: bool = False) -> Optional[ContaCorrente]:
        """Cria uma nova conta corrente"""
        try:
            nova_conta = ContaCorrente(
                id=self._generate_id(),
                nome=nome,
                banco=banco,
                agencia=agencia,
                conta=conta,
                tipo=tipo,
                saldo_inicial=saldo_inicial,
                saldo_atual=saldo_inicial,
                compartilhado_com_alzi=compartilhado_com_alzi,
                created_at=self._get_timestamp(),
                updated_at=self._get_timestamp()
            )

            # Tentar salvar no MongoDB
            if self.db_manager.is_connected():
                self.db_manager.collection(self.contas_collection).insert_one(nova_conta.to_dict())
            else:
                # Fallback para JSON
                data = self._load_fallback_data()
                data["contas"].append(nova_conta.to_dict())
                self._save_fallback_data(data)

            return nova_conta
        except Exception as e:
            print(f"Erro ao criar conta: {e}")
            return None

    def listar_contas(self, ativas_apenas: bool = True) -> List[ContaCorrente]:
        """Lista todas as contas correntes"""
        try:
            if self.db_manager.is_connected():
                filtro = {"ativa": True} if ativas_apenas else {}
                contas_data = list(self.db_manager.collection(self.contas_collection).find(filtro))
            else:
                data = self._load_fallback_data()
                contas_data = data["contas"]
                if ativas_apenas:
                    contas_data = [c for c in contas_data if c.get("ativa", True)]

            return [ContaCorrente.from_dict(conta) for conta in contas_data]
        except Exception as e:
            print(f"Erro ao listar contas: {e}")
            return []

    def obter_conta(self, conta_id: str) -> Optional[ContaCorrente]:
        """Obtém uma conta específica"""
        try:
            if self.db_manager.is_connected():
                conta_data = self.db_manager.collection(self.contas_collection).find_one({"id": conta_id})
            else:
                data = self._load_fallback_data()
                conta_data = next((c for c in data["contas"] if c["id"] == conta_id), None)

            return ContaCorrente.from_dict(conta_data) if conta_data else None
        except Exception as e:
            print(f"Erro ao obter conta: {e}")
            return None

    def atualizar_conta(self, conta_id: str, **kwargs) -> bool:
        """Atualiza uma conta corrente"""
        try:
            kwargs["updated_at"] = self._get_timestamp()
            
            if self.db_manager.is_connected():
                result = self.db_manager.collection(self.contas_collection).update_one(
                    {"id": conta_id}, {"$set": kwargs}
                )
                return result.modified_count > 0
            else:
                data = self._load_fallback_data()
                for conta in data["contas"]:
                    if conta["id"] == conta_id:
                        conta.update(kwargs)
                        self._save_fallback_data(data)
                        return True
                return False
        except Exception as e:
            print(f"Erro ao atualizar conta: {e}")
            return False

    def excluir_conta(self, conta_id: str) -> bool:
        """Exclui (desativa) uma conta corrente"""
        return self.atualizar_conta(conta_id, ativa=False)

    # CRUD - Cartões de Crédito
    def criar_cartao(self, nome: str, banco: str, bandeira: BandeiraCartao, 
                    limite: float, dia_vencimento: int, dia_fechamento: int,
                    conta_vinculada_id: Optional[str] = None,
                    compartilhado_com_alzi: bool = False) -> Optional[CartaoCredito]:
        """Cria um novo cartão de crédito"""
        try:
            novo_cartao = CartaoCredito(
                id=self._generate_id(),
                nome=nome,
                banco=banco,
                bandeira=bandeira,
                limite=limite,
                limite_disponivel=limite,
                conta_vinculada_id=conta_vinculada_id,
                dia_vencimento=dia_vencimento,
                dia_fechamento=dia_fechamento,
                compartilhado_com_alzi=compartilhado_com_alzi,
                created_at=self._get_timestamp(),
                updated_at=self._get_timestamp()
            )

            if self.db_manager.is_connected():
                self.db_manager.collection(self.cartoes_collection).insert_one(novo_cartao.to_dict())
            else:
                data = self._load_fallback_data()
                data["cartoes"].append(novo_cartao.to_dict())
                self._save_fallback_data(data)

            return novo_cartao
        except Exception as e:
            print(f"Erro ao criar cartão: {e}")
            return None

    def listar_cartoes(self, ativos_apenas: bool = True) -> List[CartaoCredito]:
        """Lista todos os cartões de crédito"""
        try:
            if self.db_manager.is_connected():
                filtro = {"ativo": True} if ativos_apenas else {}
                cartoes_data = list(self.db_manager.collection(self.cartoes_collection).find(filtro))
            else:
                data = self._load_fallback_data()
                cartoes_data = data["cartoes"]
                if ativos_apenas:
                    cartoes_data = [c for c in cartoes_data if c.get("ativo", True)]

            return [CartaoCredito.from_dict(cartao) for cartao in cartoes_data]
        except Exception as e:
            print(f"Erro ao listar cartões: {e}")
            return []

    def obter_cartao(self, cartao_id: str) -> Optional[CartaoCredito]:
        """Obtém um cartão específico"""
        try:
            if self.db_manager.is_connected():
                cartao_data = self.db_manager.collection(self.cartoes_collection).find_one({"id": cartao_id})
            else:
                data = self._load_fallback_data()
                cartao_data = next((c for c in data["cartoes"] if c["id"] == cartao_id), None)

            return CartaoCredito.from_dict(cartao_data) if cartao_data else None
        except Exception as e:
            print(f"Erro ao obter cartão: {e}")
            return None

    def atualizar_cartao(self, cartao_id: str, **kwargs) -> bool:
        """Atualiza um cartão de crédito"""
        try:
            kwargs["updated_at"] = self._get_timestamp()
            
            if self.db_manager.is_connected():
                result = self.db_manager.collection(self.cartoes_collection).update_one(
                    {"id": cartao_id}, {"$set": kwargs}
                )
                return result.modified_count > 0
            else:
                data = self._load_fallback_data()
                for cartao in data["cartoes"]:
                    if cartao["id"] == cartao_id:
                        cartao.update(kwargs)
                        self._save_fallback_data(data)
                        return True
                return False
        except Exception as e:
            print(f"Erro ao atualizar cartão: {e}")
            return False

    def excluir_cartao(self, cartao_id: str) -> bool:
        """Exclui (desativa) um cartão de crédito"""
        return self.atualizar_cartao(cartao_id, ativo=False)

    # CRUD - Transações
    def criar_transacao(self, descricao: str, valor: float, tipo: TipoTransacao,
                       data_transacao: str, categoria: Optional[str] = None,
                       conta_id: Optional[str] = None, cartao_id: Optional[str] = None,
                       parcelas: int = 1, observacoes: Optional[str] = None,
                       compartilhado_com_alzi: bool = False) -> Optional[Transacao]:
        """Cria uma nova transação"""
        try:
            # Gerar parcelamento se necessário
            parcelamento = []
            if parcelas > 1:
                valor_parcela = valor / parcelas
                data_base = datetime.fromisoformat(data_transacao.replace('Z', '+00:00'))
                
                for i in range(parcelas):
                    # Calcular data de vencimento (mês + i)
                    mes = data_base.month + i
                    ano = data_base.year
                    while mes > 12:
                        mes -= 12
                        ano += 1
                    
                    # Último dia do mês se o dia não existir
                    ultimo_dia = monthrange(ano, mes)[1]
                    dia = min(data_base.day, ultimo_dia)
                    
                    data_vencimento = datetime(ano, mes, dia).isoformat()
                    
                    parcela = Parcelamento(
                        numero_parcela=i + 1,
                        total_parcelas=parcelas,
                        valor_parcela=valor_parcela,
                        data_vencimento=data_vencimento
                    )
                    parcelamento.append(parcela)

            nova_transacao = Transacao(
                id=self._generate_id(),
                descricao=descricao,
                valor=valor,
                tipo=tipo,
                data_transacao=data_transacao,
                categoria=categoria,
                conta_id=conta_id,
                cartao_id=cartao_id,
                parcelamento=parcelamento,
                observacoes=observacoes,
                compartilhado_com_alzi=compartilhado_com_alzi,
                created_at=self._get_timestamp(),
                updated_at=self._get_timestamp()
            )

            if self.db_manager.is_connected():
                self.db_manager.collection(self.transacoes_collection).insert_one(nova_transacao.to_dict())
            else:
                data = self._load_fallback_data()
                data["transacoes"].append(nova_transacao.to_dict())
                self._save_fallback_data(data)

            # Atualizar saldo da conta ou limite do cartão
            if conta_id:
                self._atualizar_saldo_conta(conta_id, valor, tipo)
            elif cartao_id:
                self._atualizar_limite_cartao(cartao_id, valor)

            return nova_transacao
        except Exception as e:
            print(f"Erro ao criar transação: {e}")
            return None

    def listar_transacoes(self, filtros: Optional[Dict[str, Any]] = None) -> List[Transacao]:
        """Lista transações com filtros opcionais"""
        try:
            if filtros is None:
                filtros = {}
            
            if self.db_manager.is_connected():
                transacoes_data = list(self.db_manager.collection(self.transacoes_collection).find(filtros).sort("data_transacao", -1))
            else:
                data = self._load_fallback_data()
                transacoes_data = data["transacoes"]
                
                # Aplicar filtros manualmente
                for key, value in filtros.items():
                    transacoes_data = [t for t in transacoes_data if t.get(key) == value]
                
                # Ordenar por data (mais recente primeiro)
                transacoes_data.sort(key=lambda x: x.get("data_transacao", ""), reverse=True)

            return [Transacao.from_dict(transacao) for transacao in transacoes_data]
        except Exception as e:
            print(f"Erro ao listar transações: {e}")
            return []

    def obter_transacao(self, transacao_id: str) -> Optional[Transacao]:
        """Obtém uma transação específica"""
        try:
            if self.db_manager.is_connected():
                transacao_data = self.db_manager.collection(self.transacoes_collection).find_one({"id": transacao_id})
            else:
                data = self._load_fallback_data()
                transacao_data = next((t for t in data["transacoes"] if t["id"] == transacao_id), None)

            return Transacao.from_dict(transacao_data) if transacao_data else None
        except Exception as e:
            print(f"Erro ao obter transação: {e}")
            return None

    def atualizar_transacao(self, transacao_id: str, **kwargs) -> bool:
        """Atualiza uma transação"""
        try:
            kwargs["updated_at"] = self._get_timestamp()
            
            if self.db_manager.is_connected():
                result = self.db_manager.collection(self.transacoes_collection).update_one(
                    {"id": transacao_id}, {"$set": kwargs}
                )
                return result.modified_count > 0
            else:
                data = self._load_fallback_data()
                for transacao in data["transacoes"]:
                    if transacao["id"] == transacao_id:
                        transacao.update(kwargs)
                        self._save_fallback_data(data)
                        return True
                return False
        except Exception as e:
            print(f"Erro ao atualizar transação: {e}")
            return False

    def excluir_transacao(self, transacao_id: str) -> bool:
        """Exclui uma transação"""
        try:
            if self.db_manager.is_connected():
                result = self.db_manager.collection(self.transacoes_collection).delete_one({"id": transacao_id})
                return result.deleted_count > 0
            else:
                data = self._load_fallback_data()
                data["transacoes"] = [t for t in data["transacoes"] if t["id"] != transacao_id]
                self._save_fallback_data(data)
                return True
        except Exception as e:
            print(f"Erro ao excluir transação: {e}")
            return False

    def _atualizar_saldo_conta(self, conta_id: str, valor: float, tipo: TipoTransacao):
        """Atualiza o saldo de uma conta"""
        conta = self.obter_conta(conta_id)
        if conta:
            if tipo == TipoTransacao.DEBITO:
                novo_saldo = conta.saldo_atual - valor
            else:
                novo_saldo = conta.saldo_atual + valor
            
            self.atualizar_conta(conta_id, saldo_atual=novo_saldo)

    def _atualizar_limite_cartao(self, cartao_id: str, valor: float):
        """Atualiza o limite disponível de um cartão"""
        cartao = self.obter_cartao(cartao_id)
        if cartao:
            novo_limite_disponivel = cartao.limite_disponivel - valor
            self.atualizar_cartao(cartao_id, limite_disponivel=novo_limite_disponivel)

    # Métodos de consulta e relatórios
    def obter_transacoes_mes(self, ano: int, mes: int, 
                           compartilhadas_apenas: bool = False) -> List[Transacao]:
        """Obtém transações de um mês específico"""
        data_inicio = f"{ano}-{mes:02d}-01"
        if mes == 12:
            data_fim = f"{ano + 1}-01-01"
        else:
            data_fim = f"{ano}-{mes + 1:02d}-01"
        
        filtros = {
            "data_transacao": {"$gte": data_inicio, "$lt": data_fim}
        }
        
        if compartilhadas_apenas:
            filtros["compartilhado_com_alzi"] = True
        
        return self.listar_transacoes(filtros)

    def obter_resumo_financeiro(self) -> ResumoFinanceiro:
        """Gera um resumo financeiro completo"""
        try:
            contas = self.listar_contas()
            cartoes = self.listar_cartoes()
            
            # Transações do mês atual
            hoje = datetime.now()
            transacoes_mes = self.obter_transacoes_mes(hoje.year, hoje.month)
            transacoes_compartilhadas_mes = self.obter_transacoes_mes(
                hoje.year, hoje.month, compartilhadas_apenas=True
            )
            
            # Calcular totais
            saldo_total_contas = sum(conta.saldo_atual for conta in contas)
            limite_total_cartoes = sum(cartao.limite for cartao in cartoes)
            limite_disponivel_cartoes = sum(cartao.limite_disponivel for cartao in cartoes)
            
            valor_total_gastos_mes = sum(
                t.valor for t in transacoes_mes if t.tipo == TipoTransacao.DEBITO
            )
            
            valor_compartilhado_alzi_mes = sum(
                t.valor for t in transacoes_compartilhadas_mes if t.tipo == TipoTransacao.DEBITO
            )
            
            contas_compartilhadas = sum(1 for conta in contas if conta.compartilhado_com_alzi)
            cartoes_compartilhados = sum(1 for cartao in cartoes if cartao.compartilhado_com_alzi)
            
            return ResumoFinanceiro(
                total_contas=len(contas),
                total_cartoes=len(cartoes),
                total_transacoes=len(transacoes_mes),
                saldo_total_contas=saldo_total_contas,
                limite_total_cartoes=limite_total_cartoes,
                limite_disponivel_cartoes=limite_disponivel_cartoes,
                valor_total_gastos_mes=valor_total_gastos_mes,
                valor_compartilhado_alzi_mes=valor_compartilhado_alzi_mes,
                contas_compartilhadas=contas_compartilhadas,
                cartoes_compartilhados=cartoes_compartilhados,
                transacoes_compartilhadas_mes=len(transacoes_compartilhadas_mes)
            )
        except Exception as e:
            print(f"Erro ao gerar resumo financeiro: {e}")
            return ResumoFinanceiro(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0)