"""
Alzi Service - Serviços relacionados aos gastos compartilhados com Alzi
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..domains.alzi_domain_data import AlziDomainData
from utils.database_manager import DatabaseManager
from utils.finance_models import (
    Transacao, ContaCorrente, CartaoCredito, TipoTransacao, ResumoFinanceiro
)


class AlziService:
    """
    Service para gerenciamento de gastos compartilhados com Alzi
    Implementa a lógica de negócios para operações compartilhadas
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.alzi_data = AlziDomainData(db_manager)
    
    def get_shared_transactions_summary(self, ano: int, mes: int) -> Dict[str, Any]:
        """
        Obtém resumo das transações compartilhadas de um mês específico
        
        Args:
            ano: Ano
            mes: Mês (1-12)
            
        Returns:
            Dicionário com resumo das transações compartilhadas
        """
        # Validações
        if not (1 <= mes <= 12):
            raise ValueError("Mês deve estar entre 1 e 12")
        
        if ano < 1900 or ano > 2100:
            raise ValueError("Ano deve estar entre 1900 e 2100")
        
        transacoes_compartilhadas = self.alzi_domain.get_shared_transactions_by_month(ano, mes)
        
        # Separar débitos e créditos
        debitos = [t for t in transacoes_compartilhadas if t.tipo == TipoTransacao.DEBITO]
        creditos = [t for t in transacoes_compartilhadas if t.tipo == TipoTransacao.CREDITO]
        
        total_debitos = sum(t.valor for t in debitos)
        total_creditos = sum(t.valor for t in creditos)
        valor_individual = total_debitos / 2
        
        return {
            'periodo': f"{mes:02d}/{ano}",
            'total_transacoes': len(transacoes_compartilhadas),
            'total_debitos': total_debitos,
            'total_creditos': total_creditos,
            'saldo_liquido_compartilhado': total_creditos - total_debitos,
            'valor_individual': valor_individual,
            'valor_bruno': valor_individual,
            'valor_alzi': valor_individual,
            'transacoes_por_categoria': self._group_by_category(debitos),
            'transacoes_por_conta_cartao': self._group_by_account_card(transacoes_compartilhadas),
            'transacoes': transacoes_compartilhadas
        }
    
    def get_current_month_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo das transações compartilhadas do mês atual
        
        Returns:
            Dicionário com resumo do mês atual
        """
        hoje = datetime.now()
        return self.get_shared_transactions_summary(hoje.year, hoje.month)
    
    def get_year_shared_summary(self, ano: int) -> Dict[str, Any]:
        """
        Obtém resumo anual das transações compartilhadas
        
        Args:
            ano: Ano para análise
            
        Returns:
            Dicionário com resumo anual
        """
        if ano < 1900 or ano > 2100:
            raise ValueError("Ano deve estar entre 1900 e 2100")
        
        resumos_mensais = []
        total_ano_debitos = 0
        total_ano_creditos = 0
        
        for mes in range(1, 13):
            try:
                resumo_mes = self.get_shared_transactions_summary(ano, mes)
                resumos_mensais.append(resumo_mes)
                
                total_ano_debitos += resumo_mes['total_debitos']
                total_ano_creditos += resumo_mes['total_creditos']
                
            except Exception:
                # Se não houver dados para o mês, criar resumo vazio
                resumos_mensais.append({
                    'periodo': f"{mes:02d}/{ano}",
                    'total_transacoes': 0,
                    'total_debitos': 0,
                    'total_creditos': 0,
                    'saldo_liquido_compartilhado': 0,
                    'valor_individual': 0
                })
        
        valor_individual_ano = total_ano_debitos / 2
        
        return {
            'ano': ano,
            'total_debitos': total_ano_debitos,
            'total_creditos': total_ano_creditos,
            'saldo_liquido_compartilhado': total_ano_creditos - total_ano_debitos,
            'valor_individual_ano': valor_individual_ano,
            'valor_bruno_ano': valor_individual_ano,
            'valor_alzi_ano': valor_individual_ano,
            'resumos_mensais': resumos_mensais,
            'mes_maior_gasto': self._find_highest_expense_month(resumos_mensais),
            'mes_menor_gasto': self._find_lowest_expense_month(resumos_mensais),
            'media_mensal': total_ano_debitos / 12 if total_ano_debitos > 0 else 0
        }
    
    def get_shared_accounts_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo das contas compartilhadas com Alzi
        
        Returns:
            Dicionário com informações das contas compartilhadas
        """
        from .account_service import AccountService
        account_service = AccountService(self.db_manager)
        
        return account_service.get_shared_accounts_summary()
    
    def get_shared_cards_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo dos cartões compartilhados com Alzi
        
        Returns:
            Dicionário com informações dos cartões compartilhados
        """
        from .card_service import CardService
        card_service = CardService(self.db_manager)
        
        return card_service.get_shared_cards_summary()
    
    def get_comprehensive_shared_report(self, ano: int, mes: int) -> Dict[str, Any]:
        """
        Gera relatório completo dos gastos compartilhados
        
        Args:
            ano: Ano
            mes: Mês (1-12)
            
        Returns:
            Relatório completo com todas as informações relevantes
        """
        # Resumo das transações do mês
        resumo_transacoes = self.get_shared_transactions_summary(ano, mes)
        
        # Informações das contas e cartões compartilhados
        resumo_contas = self.get_shared_accounts_summary()
        resumo_cartoes = self.get_shared_cards_summary()
        
        # Estatísticas adicionais
        transacoes = resumo_transacoes['transacoes']
        
        return {
            'periodo': resumo_transacoes['periodo'],
            'resumo_geral': {
                'total_gasto_compartilhado': resumo_transacoes['total_debitos'],
                'valor_individual': resumo_transacoes['valor_individual'],
                'percentual_do_orcamento': self._calculate_budget_percentage(resumo_transacoes['total_debitos']),
                'comparacao_mes_anterior': self._compare_with_previous_month(ano, mes)
            },
            'contas_compartilhadas': resumo_contas,
            'cartoes_compartilhados': resumo_cartoes,
            'transacoes_detalhadas': {
                'por_categoria': resumo_transacoes['transacoes_por_categoria'],
                'por_origem': resumo_transacoes['transacoes_por_conta_cartao'],
                'maiores_gastos': self._get_highest_transactions(transacoes, 10),
                'distribuicao_semanal': self._group_by_week(transacoes)
            },
            'insights': self._generate_insights(resumo_transacoes, ano, mes),
            'transacoes': transacoes
        }
    
    def mark_transaction_as_shared(self, transaction_id: str) -> bool:
        """
        Marca uma transação como compartilhada com Alzi
        
        Args:
            transaction_id: ID da transação
            
        Returns:
            True se a operação foi bem-sucedida
        """
        if not transaction_id:
            raise ValueError("ID da transação é obrigatório")
        
        from .transaction_service import TransactionService
        transaction_service = TransactionService(self.db_manager)
        
        return transaction_service.update_transaction(transaction_id, compartilhado_com_alzi=True)
    
    def unmark_transaction_as_shared(self, transaction_id: str) -> bool:
        """
        Remove a marcação de compartilhamento de uma transação
        
        Args:
            transaction_id: ID da transação
            
        Returns:
            True se a operação foi bem-sucedida
        """
        if not transaction_id:
            raise ValueError("ID da transação é obrigatório")
        
        from .transaction_service import TransactionService
        transaction_service = TransactionService(self.db_manager)
        
        return transaction_service.update_transaction(transaction_id, compartilhado_com_alzi=False)
    
    def bulk_mark_transactions_as_shared(self, transaction_ids: List[str]) -> Dict[str, Any]:
        """
        Marca múltiplas transações como compartilhadas
        
        Args:
            transaction_ids: Lista de IDs das transações
            
        Returns:
            Resultado da operação
        """
        result = {
            'success': True,
            'total_requested': len(transaction_ids),
            'marked': 0,
            'errors': []
        }
        
        for transaction_id in transaction_ids:
            try:
                if self.mark_transaction_as_shared(transaction_id):
                    result['marked'] += 1
                else:
                    result['errors'].append(f"Falha ao marcar transação {transaction_id[:8]}...")
            except Exception as e:
                result['errors'].append(f"Erro ao marcar {transaction_id[:8]}...: {e}")
        
        if result['errors']:
            result['success'] = False
        
        return result
    
    def calculate_settlement(self, ano: int, mes: int) -> Dict[str, Any]:
        """
        Calcula o acerto de contas entre Bruno e Alzi para um período
        
        Args:
            ano: Ano
            mes: Mês
            
        Returns:
            Dicionário com cálculo do acerto
        """
        resumo = self.get_shared_transactions_summary(ano, mes)
        
        # Por enquanto, divisão simples 50/50
        valor_total = resumo['total_debitos']
        valor_individual = valor_total / 2
        
        return {
            'periodo': resumo['periodo'],
            'valor_total_gasto': valor_total,
            'valor_bruno': valor_individual,
            'valor_alzi': valor_individual,
            'metodo_divisao': '50/50',
            'observacoes': f'Divisão igualitária de {valor_total:.2f} entre Bruno e Alzi',
            'detalhamento': resumo['transacoes_por_categoria']
        }
    
    def _group_by_category(self, transacoes: List[Transacao]) -> Dict[str, Dict[str, Any]]:
        """
        Agrupa transações por categoria
        
        Args:
            transacoes: Lista de transações
            
        Returns:
            Dicionário agrupado por categoria
        """
        grouped = {}
        
        for transacao in transacoes:
            categoria = transacao.categoria or 'Sem categoria'
            
            if categoria not in grouped:
                grouped[categoria] = {
                    'count': 0,
                    'total': 0.0,
                    'valor_individual': 0.0,
                    'transacoes': []
                }
            
            grouped[categoria]['count'] += 1
            grouped[categoria]['total'] += transacao.valor
            grouped[categoria]['valor_individual'] = grouped[categoria]['total'] / 2
            grouped[categoria]['transacoes'].append(transacao)
        
        return grouped
    
    def _group_by_account_card(self, transacoes: List[Transacao]) -> Dict[str, Dict[str, Any]]:
        """
        Agrupa transações por conta/cartão
        
        Args:
            transacoes: Lista de transações
            
        Returns:
            Dicionário agrupado por origem
        """
        grouped = {'contas': {}, 'cartoes': {}}
        
        from .account_service import AccountService
        from .card_service import CardService
        account_service = AccountService(self.db_manager)
        card_service = CardService(self.db_manager)
        
        for transacao in transacoes:
            if transacao.conta_id:
                conta = account_service.get_account_by_id(transacao.conta_id)
                nome = conta.nome if conta else f"Conta {transacao.conta_id[:8]}..."
                
                if nome not in grouped['contas']:
                    grouped['contas'][nome] = {
                        'count': 0,
                        'total': 0.0,
                        'valor_individual': 0.0
                    }
                
                grouped['contas'][nome]['count'] += 1
                grouped['contas'][nome]['total'] += transacao.valor
                grouped['contas'][nome]['valor_individual'] = grouped['contas'][nome]['total'] / 2
            
            elif transacao.cartao_id:
                cartao = card_service.get_card_by_id(transacao.cartao_id)
                nome = cartao.nome if cartao else f"Cartão {transacao.cartao_id[:8]}..."
                
                if nome not in grouped['cartoes']:
                    grouped['cartoes'][nome] = {
                        'count': 0,
                        'total': 0.0,
                        'valor_individual': 0.0
                    }
                
                grouped['cartoes'][nome]['count'] += 1
                grouped['cartoes'][nome]['total'] += transacao.valor
                grouped['cartoes'][nome]['valor_individual'] = grouped['cartoes'][nome]['total'] / 2
        
        return grouped
    
    def _get_highest_transactions(self, transacoes: List[Transacao], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém as maiores transações
        
        Args:
            transacoes: Lista de transações
            limit: Número máximo de transações
            
        Returns:
            Lista das maiores transações
        """
        debitos = [t for t in transacoes if t.tipo == TipoTransacao.DEBITO]
        debitos_ordenados = sorted(debitos, key=lambda x: x.valor, reverse=True)
        
        return [{
            'descricao': t.descricao,
            'valor': t.valor,
            'valor_individual': t.valor / 2,
            'data': t.data_transacao[:10],
            'categoria': t.categoria or 'Sem categoria'
        } for t in debitos_ordenados[:limit]]
    
    def _group_by_week(self, transacoes: List[Transacao]) -> Dict[str, Dict[str, Any]]:
        """
        Agrupa transações por semana
        
        Args:
            transacoes: Lista de transações
            
        Returns:
            Dicionário agrupado por semana
        """
        weeks = {}
        
        for transacao in transacoes:
            if transacao.tipo == TipoTransacao.DEBITO:
                data = datetime.strptime(transacao.data_transacao[:10], "%Y-%m-%d")
                week_start = data - timedelta(days=data.weekday())
                week_key = week_start.strftime("%Y-%m-%d")
                
                if week_key not in weeks:
                    weeks[week_key] = {
                        'count': 0,
                        'total': 0.0,
                        'valor_individual': 0.0
                    }
                
                weeks[week_key]['count'] += 1
                weeks[week_key]['total'] += transacao.valor
                weeks[week_key]['valor_individual'] = weeks[week_key]['total'] / 2
        
        return weeks
    
    def _calculate_budget_percentage(self, valor_gasto: float, orcamento_mensal: float = 5000.0) -> float:
        """
        Calcula percentual do orçamento utilizado
        
        Args:
            valor_gasto: Valor gasto no período
            orcamento_mensal: Orçamento mensal estimado
            
        Returns:
            Percentual do orçamento
        """
        if orcamento_mensal <= 0:
            return 0
        
        return (valor_gasto / orcamento_mensal) * 100
    
    def _compare_with_previous_month(self, ano: int, mes: int) -> Dict[str, Any]:
        """
        Compara gastos com o mês anterior
        
        Args:
            ano: Ano atual
            mes: Mês atual
            
        Returns:
            Comparação com mês anterior
        """
        try:
            # Calcular mês anterior
            if mes == 1:
                mes_anterior = 12
                ano_anterior = ano - 1
            else:
                mes_anterior = mes - 1
                ano_anterior = ano
            
            resumo_atual = self.get_shared_transactions_summary(ano, mes)
            resumo_anterior = self.get_shared_transactions_summary(ano_anterior, mes_anterior)
            
            diferenca = resumo_atual['total_debitos'] - resumo_anterior['total_debitos']
            percentual = (diferenca / resumo_anterior['total_debitos'] * 100) if resumo_anterior['total_debitos'] > 0 else 0
            
            return {
                'mes_anterior': resumo_anterior['total_debitos'],
                'mes_atual': resumo_atual['total_debitos'],
                'diferenca': diferenca,
                'percentual_variacao': percentual,
                'tendencia': 'aumento' if diferenca > 0 else 'reducao' if diferenca < 0 else 'estavel'
            }
            
        except Exception:
            return {
                'mes_anterior': 0,
                'mes_atual': 0,
                'diferenca': 0,
                'percentual_variacao': 0,
                'tendencia': 'sem_dados'
            }
    
    def _generate_insights(self, resumo: Dict[str, Any], ano: int, mes: int) -> List[str]:
        """
        Gera insights baseado nos dados
        
        Args:
            resumo: Resumo das transações
            ano: Ano
            mes: Mês
            
        Returns:
            Lista de insights
        """
        insights = []
        
        total_debitos = resumo['total_debitos']
        categorias = resumo['transacoes_por_categoria']
        
        if total_debitos > 0:
            # Insight sobre categoria com maior gasto
            if categorias:
                maior_categoria = max(categorias.items(), key=lambda x: x[1]['total'])
                percentual_categoria = (maior_categoria[1]['total'] / total_debitos) * 100
                insights.append(f"A categoria '{maior_categoria[0]}' representa {percentual_categoria:.1f}% dos gastos compartilhados")
            
            # Insight sobre valor individual
            valor_individual = total_debitos / 2
            insights.append(f"Cada pessoa deve pagar R$ {valor_individual:.2f} referente aos gastos compartilhados")
            
            # Insight sobre número de transações
            total_transacoes = resumo['total_transacoes']
            if total_transacoes > 0:
                valor_medio = total_debitos / total_transacoes
                insights.append(f"Valor médio por transação: R$ {valor_medio:.2f}")
        
        return insights
    
    def _find_highest_expense_month(self, resumos_mensais: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Encontra o mês com maior gasto compartilhado
        
        Args:
            resumos_mensais: Lista de resumos mensais
            
        Returns:
            Mês com maior gasto ou None
        """
        if not resumos_mensais:
            return None
        
        return max(resumos_mensais, key=lambda x: x['total_debitos'])
    
    def _find_lowest_expense_month(self, resumos_mensais: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Encontra o mês com menor gasto compartilhado
        
        Args:
            resumos_mensais: Lista de resumos mensais
            
        Returns:
            Mês com menor gasto ou None
        """
        if not resumos_mensais:
            return None
        
        # Filtrar meses com gastos > 0
        meses_com_gastos = [m for m in resumos_mensais if m['total_debitos'] > 0]
        
        if not meses_com_gastos:
            return None
        
        return min(meses_com_gastos, key=lambda x: x['total_debitos'])