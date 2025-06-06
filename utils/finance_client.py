import json
import uuid
import csv
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
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

    def obter_transacoes_fatura_cartao(self, cartao_id: str, mes_fatura: int, ano_fatura: int) -> List[Transacao]:
        """
        Obtém transações de uma fatura específica do cartão
        
        Args:
            cartao_id: ID do cartão
            mes_fatura: Mês da fatura (vencimento)
            ano_fatura: Ano da fatura
            
        Returns:
            Lista de transações da fatura
        """
        try:
            # Obter informações do cartão
            cartao = self.obter_cartao(cartao_id)
            if not cartao:
                return []
            
            # Calcular período da fatura
            # A fatura inclui transações do dia de fechamento do mês anterior até o dia de fechamento do mês atual
            dia_fechamento = cartao.dia_fechamento
            
            # Data de início: dia após fechamento do mês anterior
            if mes_fatura == 1:
                mes_inicio = 12
                ano_inicio = ano_fatura - 1
            else:
                mes_inicio = mes_fatura - 1
                ano_inicio = ano_fatura
            
            # Ajustar data de início e fim considerando o dia de fechamento
            from datetime import datetime, timedelta
            
            # Data de início: dia após o fechamento do mês anterior
            data_inicio = datetime(ano_inicio, mes_inicio, dia_fechamento) + timedelta(days=1)
            
            # Data de fim: dia de fechamento do mês atual
            # Tratar caso onde o dia de fechamento não existe no mês (ex: 31 em fevereiro)
            try:
                data_fim = datetime(ano_fatura, mes_fatura, dia_fechamento)
            except ValueError:
                # Se o dia não existir no mês, usar o último dia do mês
                import calendar
                ultimo_dia = calendar.monthrange(ano_fatura, mes_fatura)[1]
                data_fim = datetime(ano_fatura, mes_fatura, min(dia_fechamento, ultimo_dia))
            
            # Filtros para buscar transações
            filtros = {
                "cartao_id": cartao_id,
                "data_transacao": {
                    "$gte": data_inicio.strftime("%Y-%m-%d"),
                    "$lte": data_fim.strftime("%Y-%m-%d")
                }
            }
            
            return self.listar_transacoes(filtros)
            
        except Exception as e:
            print(f"Erro ao obter transações da fatura: {e}")
            return []

    def listar_faturas_cartao(self, cartao_id: str, ano: int = None) -> List[Dict[str, Any]]:
        """
        Lista todas as faturas que possuem transações para um cartão específico
        
        Args:
            cartao_id: ID do cartão
            ano: Ano para filtrar (se None, usa ano atual)
            
        Returns:
            Lista de dicionários com informações das faturas
        """
        try:
            from collections import defaultdict
            
            if ano is None:
                ano = datetime.now().year
            
            # Obter todas as transações do cartão no ano
            filtros = {
                "cartao_id": cartao_id,
                "data_transacao": {
                    "$gte": f"{ano}-01-01",
                    "$lt": f"{ano + 1}-01-01"
                }
            }
            
            transacoes = self.listar_transacoes(filtros)
            
            if not transacoes:
                return []
            
            # Obter informações do cartão
            cartao = self.obter_cartao(cartao_id)
            if not cartao:
                return []
            
            # Agrupar transações por fatura
            faturas = defaultdict(lambda: {
                'transacoes': [],
                'total': 0.0,
                'total_compartilhado': 0.0,
                'mes': 0,
                'ano': 0
            })
            
            for transacao in transacoes:
                # Determinar a qual fatura a transação pertence
                data_transacao = datetime.strptime(transacao.data_transacao[:10], "%Y-%m-%d")
                
                # Calcular mês/ano da fatura baseado na data da transação e dia de fechamento
                dia_fechamento = cartao.dia_fechamento
                
                if data_transacao.day <= dia_fechamento:
                    # Transação está na fatura do mesmo mês
                    mes_fatura = data_transacao.month
                    ano_fatura = data_transacao.year
                else:
                    # Transação está na fatura do próximo mês
                    if data_transacao.month == 12:
                        mes_fatura = 1
                        ano_fatura = data_transacao.year + 1
                    else:
                        mes_fatura = data_transacao.month + 1
                        ano_fatura = data_transacao.year
                
                chave_fatura = f"{ano_fatura}-{mes_fatura:02d}"
                
                faturas[chave_fatura]['transacoes'].append(transacao)
                faturas[chave_fatura]['mes'] = mes_fatura
                faturas[chave_fatura]['ano'] = ano_fatura
                
                if transacao.tipo == TipoTransacao.DEBITO:
                    faturas[chave_fatura]['total'] += transacao.valor
                    if transacao.compartilhado_com_alzi:
                        faturas[chave_fatura]['total_compartilhado'] += transacao.valor
            
            # Converter para lista ordenada
            lista_faturas = []
            for chave, dados in sorted(faturas.items()):
                # Calcular período da fatura
                mes_fatura = dados['mes']
                ano_fatura = dados['ano']
                
                if mes_fatura == 1:
                    mes_inicio = 12
                    ano_inicio = ano_fatura - 1
                else:
                    mes_inicio = mes_fatura - 1
                    ano_inicio = ano_fatura
                
                try:
                    data_inicio = datetime(ano_inicio, mes_inicio, dia_fechamento) + timedelta(days=1)
                    data_fim = datetime(ano_fatura, mes_fatura, dia_fechamento)
                except ValueError:
                    # Se o dia não existir no mês, usar o último dia do mês
                    import calendar
                    ultimo_dia = calendar.monthrange(ano_fatura, mes_fatura)[1]
                    data_fim = datetime(ano_fatura, mes_fatura, min(dia_fechamento, ultimo_dia))
                    ultimo_dia_inicio = calendar.monthrange(ano_inicio, mes_inicio)[1]
                    data_inicio = datetime(ano_inicio, mes_inicio, min(dia_fechamento, ultimo_dia_inicio)) + timedelta(days=1)
                
                lista_faturas.append({
                    'mes': mes_fatura,
                    'ano': ano_fatura,
                    'periodo_inicio': data_inicio.strftime("%d/%m/%Y"),
                    'periodo_fim': data_fim.strftime("%d/%m/%Y"),
                    'vencimento': f"{cartao.dia_vencimento:02d}/{mes_fatura:02d}/{ano_fatura}",
                    'total_transacoes': len(dados['transacoes']),
                    'total_valor': dados['total'],
                    'total_compartilhado': dados['total_compartilhado'],
                    'transacoes': dados['transacoes']
                })
            
            return lista_faturas
            
        except Exception as e:
            print(f"Erro ao listar faturas do cartão: {e}")
            return []

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

    # Métodos de importação de arquivos
    def detectar_formato_csv(self, arquivo_path: str) -> Optional[str]:
        """
        Detecta o formato do arquivo CSV (Bradesco, Itaú, BTG)
        
        Args:
            arquivo_path: Caminho para o arquivo CSV
            
        Returns:
            String indicando o banco ou None se não reconhecido
        """
        try:
            with open(arquivo_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                
                # Verificar formato Bradesco (várias variações possíveis)
                bradesco_patterns = [
                    "Data;Histórico;Valor(US$);Valor(R$);",
                    "Data;Hist�rico;Valor(US$);Valor(R$);",
                    "Data;Histrico;Valor(US$);Valor(R$);",  # Encoding issues
                    "Data;Histórico;Valor(US$);Valor(R$)",   # Sem ponto e vírgula final
                    "Data;Hist�rico;Valor(US$);Valor(R$)",   # Sem ponto e vírgula final
                    "Data;Histrico;Valor(US$);Valor(R$)"     # Encoding issues sem ponto e vírgula
                ]
                
                for pattern in bradesco_patterns:
                    if pattern in content:
                        return "bradesco"
                
                # Verificar formato Itaú (exemplo)
                if "data,descricao,valor" in content.lower():
                    return "itau"
                
                # Verificar formato BTG (exemplo)
                if "date,description,amount" in content.lower():
                    return "btg"
                
                return None
                
        except Exception as e:
            print(f"Erro ao detectar formato do arquivo: {e}")
            return None

    def processar_csv_bradesco(self, arquivo_path: str, cartao_id: str) -> Tuple[List[Dict], int, int]:
        """
        Processa arquivo CSV do Bradesco e retorna transações processadas
        
        Args:
            arquivo_path: Caminho para o arquivo CSV
            cartao_id: ID do cartão associado
            
        Returns:
            Tupla com (transações_processadas, total_linhas, transações_importadas)
        """
        try:
            transacoes_processadas = []
            total_linhas = 0
            
            # Obter informações do cartão
            cartao = self.obter_cartao(cartao_id)
            if not cartao:
                raise Exception("Cartão não encontrado")
            
            with open(arquivo_path, 'r', encoding='utf-8', errors='ignore') as file:
                linhas = file.readlines()
            
            # Encontrar a linha do cabeçalho (pegar a ÚLTIMA ocorrência)
            linha_inicio = -1
            bradesco_patterns = [
                "Data;Histórico;Valor(US$);Valor(R$);",
                "Data;Hist�rico;Valor(US$);Valor(R$);",
                "Data;Histrico;Valor(US$);Valor(R$);",  # Encoding issues
                "Data;Histórico;Valor(US$);Valor(R$)",   # Sem ponto e vírgula final
                "Data;Hist�rico;Valor(US$);Valor(R$)",   # Sem ponto e vírgula final
                "Data;Histrico;Valor(US$);Valor(R$)"     # Encoding issues sem ponto e vírgula
            ]
            
            # Procurar pela ÚLTIMA ocorrência do cabeçalho
            for i, linha in enumerate(linhas):
                for pattern in bradesco_patterns:
                    if pattern in linha:
                        linha_inicio = i  # Continua procurando para pegar a última
                        break
            
            if linha_inicio == -1:
                raise Exception("Formato do arquivo Bradesco não reconhecido")
            
            # Processar transações
            for i in range(linha_inicio + 1, len(linhas)):
                linha = linhas[i].strip()
                
                # Parar se encontrar linha vazia ou fim das transações
                if not linha or linha.count(';') < 3:
                    break
                
                total_linhas += 1
                
                # Parse da linha CSV
                partes = linha.split(';')
                if len(partes) >= 4:
                    try:
                        data_str = partes[0].strip()
                        descricao = partes[1].strip()
                        valor_usd_str = partes[2].strip()
                        valor_brl_str = partes[3].strip()
                        
                        # Converter data (formato DD/MM/YYYY ou DD/MM)
                        if '/' in data_str:
                            partes_data = data_str.split('/')
                            if len(partes_data) == 3:  # DD/MM/YYYY
                                dia, mes, ano = partes_data
                                data_transacao = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
                            elif len(partes_data) == 2:  # DD/MM (assumir ano atual)
                                dia, mes = partes_data
                                ano_atual = datetime.now().year
                                data_transacao = f"{ano_atual}-{mes.zfill(2)}-{dia.zfill(2)}"
                            else:
                                continue  # Formato não reconhecido
                        else:
                            continue  # Pular se não conseguir converter data
                        
                        # Converter valor (formato brasileiro: 1.234,56)
                        valor_limpo = valor_brl_str.replace('.', '').replace(',', '.').replace('R$', '').strip()
                        # Remover caracteres não numéricos exceto ponto e hífen
                        valor_limpo = re.sub(r'[^0-9.,\-]', '', valor_limpo)
                        valor_limpo = valor_limpo.replace(',', '.')
                        
                        if valor_limpo:
                            valor = abs(float(valor_limpo))  # Usar valor absoluto
                            # Determinar tipo (assumir que valores são débitos por padrão em cartão)
                            tipo = TipoTransacao.DEBITO
                            
                            # Verificar se a transação já existe neste mês
                            data_dt = datetime.strptime(data_transacao, "%Y-%m-%d")
                            transacoes_mes = self.obter_transacoes_mes(data_dt.year, data_dt.month)
                            
                            # Verificar duplicatas por data, valor e cartão
                            ja_existe = False
                            for t in transacoes_mes:
                                if (t.cartao_id == cartao_id and 
                                    t.data_transacao[:10] == data_transacao and 
                                    abs(t.valor - valor) < 0.01):  # Tolerância de 1 centavo
                                    ja_existe = True
                                    break
                            
                            # Filtrar transações que não são compras
                            descricoes_ignorar = [
                                'SALDO ANTERIOR',
                                'PAGTO. POR DEB EM C/C',
                                'PAGAMENTO',
                                'ESTORNO',
                                'JUROS',
                                'MULTA',
                                'ANUIDADE'
                            ]
                            
                            deve_ignorar = any(termo in descricao.upper() for termo in descricoes_ignorar)
                            
                            if not ja_existe and not deve_ignorar:
                                transacao_data = {
                                    'data_transacao': data_transacao,
                                    'descricao': descricao,
                                    'valor': valor,
                                    'tipo': tipo,
                                    'cartao_id': cartao_id,
                                    'compartilhado_com_alzi': cartao.compartilhado_com_alzi,
                                    'categoria': 'Importado - Bradesco',
                                    'observacoes': f'Importado de CSV - Valor USD: {valor_usd_str}'
                                }
                                transacoes_processadas.append(transacao_data)
                        
                    except (ValueError, IndexError) as e:
                        print(f"Erro ao processar linha {i+1}: {linha} - {e}")
                        continue
            
            return transacoes_processadas, total_linhas, len(transacoes_processadas)
            
        except Exception as e:
            print(f"Erro ao processar CSV do Bradesco: {e}")
            return [], 0, 0

    def importar_transacoes_csv(self, arquivo_path: str, cartao_id: str) -> Dict[str, Any]:
        """
        Importa transações de um arquivo CSV
        
        Args:
            arquivo_path: Caminho para o arquivo CSV
            cartao_id: ID do cartão associado
            
        Returns:
            Dicionário com resultado da importação
        """
        try:
            # Detectar formato do arquivo
            formato = self.detectar_formato_csv(arquivo_path)
            
            if formato != "bradesco":
                return {
                    'sucesso': False,
                    'erro': f'Formato não suportado: {formato}. Apenas Bradesco suportado no momento.',
                    'transacoes_importadas': 0,
                    'total_linhas': 0
                }
            
            # Processar arquivo Bradesco
            transacoes_data, total_linhas, transacoes_encontradas = self.processar_csv_bradesco(arquivo_path, cartao_id)
            
            # Importar transações para o banco
            transacoes_importadas = 0
            erros = []
            
            for transacao_data in transacoes_data:
                try:
                    nova_transacao = self.criar_transacao(
                        descricao=transacao_data['descricao'],
                        valor=transacao_data['valor'],
                        tipo=transacao_data['tipo'],
                        data_transacao=transacao_data['data_transacao'],
                        categoria=transacao_data['categoria'],
                        cartao_id=transacao_data['cartao_id'],
                        observacoes=transacao_data['observacoes'],
                        compartilhado_com_alzi=transacao_data['compartilhado_com_alzi']
                    )
                    
                    if nova_transacao:
                        transacoes_importadas += 1
                    else:
                        erros.append(f"Falha ao criar transação: {transacao_data['descricao']}")
                        
                except Exception as e:
                    erros.append(f"Erro ao importar transação {transacao_data['descricao']}: {e}")
            
            # Gerar CSV limpo para download
            csv_limpo_path = self._gerar_csv_limpo(transacoes_data, arquivo_path)
            
            return {
                'sucesso': True,
                'formato_detectado': formato,
                'total_linhas': total_linhas,
                'transacoes_encontradas': transacoes_encontradas,
                'transacoes_importadas': transacoes_importadas,
                'erros': erros,
                'csv_limpo_path': csv_limpo_path
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'transacoes_importadas': 0,
                'total_linhas': 0
            }

    def _gerar_csv_limpo(self, transacoes_data: List[Dict], arquivo_original: str) -> str:
        """
        Gera um arquivo CSV limpo com as transações processadas
        
        Args:
            transacoes_data: Lista de transações processadas
            arquivo_original: Caminho do arquivo original
            
        Returns:
            Caminho do arquivo CSV limpo gerado
        """
        try:
            # Criar nome do arquivo limpo
            arquivo_path = Path(arquivo_original)
            csv_limpo_path = arquivo_path.parent / f"{arquivo_path.stem}_limpo.csv"
            
            # Gerar CSV limpo
            with open(csv_limpo_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Data', 'Descrição', 'Valor', 'Tipo', 'Categoria', 'Compartilhado_Alzi', 'Observações']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                
                writer.writeheader()
                for transacao in transacoes_data:
                    writer.writerow({
                        'Data': transacao['data_transacao'],
                        'Descrição': transacao['descricao'],
                        'Valor': f"R$ {transacao['valor']:.2f}",
                        'Tipo': transacao['tipo'].value if hasattr(transacao['tipo'], 'value') else transacao['tipo'],
                        'Categoria': transacao['categoria'],
                        'Compartilhado_Alzi': 'Sim' if transacao['compartilhado_com_alzi'] else 'Não',
                        'Observações': transacao['observacoes']
                    })
            
            return str(csv_limpo_path)
            
        except Exception as e:
            print(f"Erro ao gerar CSV limpo: {e}")
            return ""
