"""
Period Service - Serviços relacionados a períodos e faturas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

from ..domains.period_domain_data import PeriodDomainData
from utils.database_manager import DatabaseManager
from utils.finance_models import CartaoCredito, Transacao, TipoTransacao


class PeriodService:
    """
    Service para gerenciamento de períodos e faturas
    Implementa a lógica de negócios para cálculos de períodos
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.period_data = PeriodDomainData(db_manager)
    
    def get_billing_period_transactions(self, cartao_id: str, mes_fatura: int, 
                                      ano_fatura: int) -> List[Transacao]:
        """
        Obtém transações de uma fatura específica do cartão
        
        Args:
            cartao_id: ID do cartão
            mes_fatura: Mês da fatura (vencimento)
            ano_fatura: Ano da fatura
            
        Returns:
            Lista de transações da fatura
        """
        # Validações
        if not cartao_id:
            raise ValueError("ID do cartão é obrigatório")
        
        if not (1 <= mes_fatura <= 12):
            raise ValueError("Mês da fatura deve estar entre 1 e 12")
        
        if ano_fatura < 1900 or ano_fatura > 2100:
            raise ValueError("Ano da fatura deve estar entre 1900 e 2100")
        
        # Obter informações do cartão
        from .card_service import CardService
        card_service = CardService(self.db_manager)
        cartao = card_service.get_card_by_id(cartao_id)
        
        if not cartao:
            raise ValueError("Cartão não encontrado")
        
        return self.period_domain.get_billing_period_transactions(cartao, mes_fatura, ano_fatura)
    
    def list_card_invoices(self, cartao_id: str, ano: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista todas as faturas que possuem transações para um cartão específico
        
        Args:
            cartao_id: ID do cartão
            ano: Ano para filtrar (se None, usa ano atual)
            
        Returns:
            Lista de dicionários com informações das faturas
        """
        if not cartao_id:
            raise ValueError("ID do cartão é obrigatório")
        
        if ano is None:
            ano = datetime.now().year
        
        # Obter informações do cartão
        from .card_service import CardService
        card_service = CardService(self.db_manager)
        cartao = card_service.get_card_by_id(cartao_id)
        
        if not cartao:
            raise ValueError("Cartão não encontrado")
        
        # Obter todas as transações do cartão no ano
        from .transaction_service import TransactionService
        transaction_service = TransactionService(self.db_manager)
        
        filtros = {
            "cartao_id": cartao_id,
            "data_transacao": {
                "$gte": f"{ano}-01-01",
                "$lt": f"{ano + 1}-01-01"
            }
        }
        
        transacoes = transaction_service.list_transactions(filtros)
        
        if not transacoes:
            return []
        
        return self._group_transactions_by_invoice(transacoes, cartao)
    
    def get_monthly_summary(self, ano: int, mes: int, 
                           shared_only: bool = False) -> Dict[str, Any]:
        """
        Obtém resumo financeiro de um mês específico
        
        Args:
            ano: Ano
            mes: Mês (1-12)
            shared_only: Se deve considerar apenas transações compartilhadas
            
        Returns:
            Dicionário com resumo do mês
        """
        # Validações
        if not (1 <= mes <= 12):
            raise ValueError("Mês deve estar entre 1 e 12")
        
        if ano < 1900 or ano > 2100:
            raise ValueError("Ano deve estar entre 1900 e 2100")
        
        from .transaction_service import TransactionService
        transaction_service = TransactionService(self.db_manager)
        
        # Obter transações do mês
        transacoes = transaction_service.get_transactions_by_month(ano, mes, shared_only)
        
        # Separar por conta e cartão
        transacoes_conta = [t for t in transacoes if t.conta_id]
        transacoes_cartao = [t for t in transacoes if t.cartao_id]
        
        # Calcular totais
        total_debitos = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.DEBITO)
        total_creditos = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.CREDITO)
        total_compartilhado = sum(t.valor for t in transacoes 
                                if t.compartilhado_com_alzi and t.tipo == TipoTransacao.DEBITO)
        
        return {
            'periodo': f"{mes:02d}/{ano}",
            'total_transacoes': len(transacoes),
            'total_debitos': total_debitos,
            'total_creditos': total_creditos,
            'saldo_liquido': total_creditos - total_debitos,
            'total_compartilhado': total_compartilhado,
            'valor_individual': total_compartilhado / 2 if total_compartilhado > 0 else 0,
            'transacoes_conta': len(transacoes_conta),
            'transacoes_cartao': len(transacoes_cartao),
            'gastos_por_categoria': self._group_expenses_by_category(transacoes),
            'transacoes_por_dia': self._group_transactions_by_day(transacoes)
        }
    
    def get_year_summary(self, ano: int, shared_only: bool = False) -> Dict[str, Any]:
        """
        Obtém resumo financeiro de um ano específico
        
        Args:
            ano: Ano
            shared_only: Se deve considerar apenas transações compartilhadas
            
        Returns:
            Dicionário com resumo do ano
        """
        if ano < 1900 or ano > 2100:
            raise ValueError("Ano deve estar entre 1900 e 2100")
        
        resumos_mensais = []
        total_ano_debitos = 0
        total_ano_creditos = 0
        total_ano_compartilhado = 0
        
        for mes in range(1, 13):
            try:
                resumo_mes = self.get_monthly_summary(ano, mes, shared_only)
                resumos_mensais.append(resumo_mes)
                
                total_ano_debitos += resumo_mes['total_debitos']
                total_ano_creditos += resumo_mes['total_creditos']
                total_ano_compartilhado += resumo_mes['total_compartilhado']
                
            except Exception:
                # Se não houver dados para o mês, criar resumo vazio
                resumos_mensais.append({
                    'periodo': f"{mes:02d}/{ano}",
                    'total_transacoes': 0,
                    'total_debitos': 0,
                    'total_creditos': 0,
                    'saldo_liquido': 0,
                    'total_compartilhado': 0,
                    'valor_individual': 0
                })
        
        return {
            'ano': ano,
            'total_debitos': total_ano_debitos,
            'total_creditos': total_ano_creditos,
            'saldo_liquido': total_ano_creditos - total_ano_debitos,
            'total_compartilhado': total_ano_compartilhado,
            'valor_individual_ano': total_ano_compartilhado / 2 if total_ano_compartilhado > 0 else 0,
            'resumos_mensais': resumos_mensais,
            'melhor_mes': self._find_best_month(resumos_mensais),
            'pior_mes': self._find_worst_month(resumos_mensais)
        }
    
    def get_current_invoices_summary(self) -> List[Dict[str, Any]]:
        """
        Obtém resumo das faturas atuais de todos os cartões
        
        Returns:
            Lista com resumo das faturas atuais
        """
        from .card_service import CardService
        card_service = CardService(self.db_manager)
        
        cartoes = card_service.list_cards(active_only=True)
        faturas_atuais = []
        
        hoje = datetime.now()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        for cartao in cartoes:
            try:
                # Para cada cartão, obter a fatura atual e próxima
                fatura_atual = self._get_current_invoice_info(cartao, hoje)
                if fatura_atual:
                    faturas_atuais.append(fatura_atual)
                    
            except Exception as e:
                print(f"Erro ao processar cartão {cartao.nome}: {e}")
        
        return faturas_atuais
    
    def calculate_billing_dates(self, cartao: CartaoCredito, mes_referencia: int, 
                              ano_referencia: int) -> Dict[str, str]:
        """
        Calcula as datas de fechamento e vencimento para um período específico
        
        Args:
            cartao: Cartão de crédito
            mes_referencia: Mês de referência
            ano_referencia: Ano de referência
            
        Returns:
            Dicionário com datas calculadas
        """
        return self.period_domain.calculate_billing_dates(cartao, mes_referencia, ano_referencia)
    
    def _group_transactions_by_invoice(self, transacoes: List[Transacao], 
                                     cartao: CartaoCredito) -> List[Dict[str, Any]]:
        """
        Agrupa transações por fatura
        
        Args:
            transacoes: Lista de transações
            cartao: Cartão de crédito
            
        Returns:
            Lista de faturas com suas transações
        """
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
            mes_fatura, ano_fatura = self._calculate_invoice_month(data_transacao, cartao.dia_fechamento)
            
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
            periodo_info = self.calculate_billing_dates(cartao, dados['mes'], dados['ano'])
            
            lista_faturas.append({
                'mes': dados['mes'],
                'ano': dados['ano'],
                'periodo_inicio': periodo_info['periodo_inicio'],
                'periodo_fim': periodo_info['periodo_fim'],
                'vencimento': periodo_info['data_vencimento'],
                'total_transacoes': len(dados['transacoes']),
                'total_valor': dados['total'],
                'total_compartilhado': dados['total_compartilhado'],
                'transacoes': dados['transacoes']
            })
        
        return lista_faturas
    
    def _calculate_invoice_month(self, data_transacao: datetime, dia_fechamento: int) -> tuple:
        """
        Calcula o mês/ano da fatura baseado na data da transação
        
        Args:
            data_transacao: Data da transação
            dia_fechamento: Dia de fechamento do cartão
            
        Returns:
            Tupla (mes_fatura, ano_fatura)
        """
        if data_transacao.day > dia_fechamento:
            # Transação após fechamento vai para fatura que vence em 2 meses
            if data_transacao.month >= 11:  # Novembro ou Dezembro
                mes_fatura = data_transacao.month - 10  # 11->1, 12->2
                ano_fatura = data_transacao.year + 1
            else:
                mes_fatura = data_transacao.month + 2
                ano_fatura = data_transacao.year
        else:
            # Transação até o dia de fechamento vai para fatura do próximo mês
            if data_transacao.month == 12:
                mes_fatura = 1
                ano_fatura = data_transacao.year + 1
            else:
                mes_fatura = data_transacao.month + 1
                ano_fatura = data_transacao.year
        
        return mes_fatura, ano_fatura
    
    def _get_current_invoice_info(self, cartao: CartaoCredito, data_referencia: datetime) -> Optional[Dict[str, Any]]:
        """
        Obtém informações da fatura atual de um cartão
        
        Args:
            cartao: Cartão de crédito
            data_referencia: Data de referência
            
        Returns:
            Dicionário com informações da fatura atual
        """
        # Determinar qual é a fatura "atual" baseado na data
        mes_fatura, ano_fatura = self._calculate_invoice_month(data_referencia, cartao.dia_fechamento)
        
        try:
            transacoes = self.get_billing_period_transactions(cartao.id, mes_fatura, ano_fatura)
            
            total_fatura = sum(t.valor for t in transacoes if t.tipo == TipoTransacao.DEBITO)
            total_compartilhado = sum(t.valor for t in transacoes 
                                   if t.compartilhado_com_alzi and t.tipo == TipoTransacao.DEBITO)
            
            periodo_info = self.calculate_billing_dates(cartao, mes_fatura, ano_fatura)
            
            return {
                'cartao_id': cartao.id,
                'cartao_nome': cartao.nome,
                'mes': mes_fatura,
                'ano': ano_fatura,
                'periodo_inicio': periodo_info['periodo_inicio'],
                'periodo_fim': periodo_info['periodo_fim'],
                'vencimento': periodo_info['data_vencimento'],
                'total_transacoes': len(transacoes),
                'total_valor': total_fatura,
                'total_compartilhado': total_compartilhado,
                'limite_disponivel': cartao.limite_disponivel,
                'percentual_uso': ((cartao.limite - cartao.limite_disponivel) / cartao.limite * 100) if cartao.limite > 0 else 0
            }
            
        except Exception:
            return None
    
    def _group_expenses_by_category(self, transacoes: List[Transacao]) -> Dict[str, float]:
        """
        Agrupa gastos por categoria
        
        Args:
            transacoes: Lista de transações
            
        Returns:
            Dicionário com total por categoria
        """
        gastos_categoria = {}
        
        for transacao in transacoes:
            if transacao.tipo == TipoTransacao.DEBITO:
                categoria = transacao.categoria or 'Sem categoria'
                gastos_categoria[categoria] = gastos_categoria.get(categoria, 0) + transacao.valor
        
        return gastos_categoria
    
    def _group_transactions_by_day(self, transacoes: List[Transacao]) -> Dict[str, int]:
        """
        Agrupa transações por dia
        
        Args:
            transacoes: Lista de transações
            
        Returns:
            Dicionário com contagem por dia
        """
        transacoes_dia = {}
        
        for transacao in transacoes:
            dia = transacao.data_transacao[:10]  # YYYY-MM-DD
            transacoes_dia[dia] = transacoes_dia.get(dia, 0) + 1
        
        return transacoes_dia
    
    def _find_best_month(self, resumos_mensais: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Encontra o melhor mês (menor gasto)
        
        Args:
            resumos_mensais: Lista de resumos mensais
            
        Returns:
            Resumo do melhor mês ou None
        """
        if not resumos_mensais:
            return None
        
        return min(resumos_mensais, key=lambda x: x['total_debitos'])
    
    def _find_worst_month(self, resumos_mensais: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Encontra o pior mês (maior gasto)
        
        Args:
            resumos_mensais: Lista de resumos mensais
            
        Returns:
            Resumo do pior mês ou None
        """
        if not resumos_mensais:
            return None
        
        return max(resumos_mensais, key=lambda x: x['total_debitos'])