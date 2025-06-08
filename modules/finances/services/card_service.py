"""
Card Service - Serviços relacionados a cartões de crédito
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..domains.card_domain_data import CardDomainData
from utils.database_manager import DatabaseManager
from utils.finance_models import CartaoCredito, BandeiraCartao


class CardService:
    """
    Service para gerenciamento de cartões de crédito
    Implementa a lógica de negócios para operações com cartões
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.card_data = CardDomainData(db_manager)
    
    def create_card(self, nome: str, banco: str, bandeira: BandeiraCartao, 
                   limite: float, dia_vencimento: int, dia_fechamento: int,
                   conta_vinculada_id: Optional[str] = None,
                   compartilhado_com_alzi: bool = False) -> Optional[CartaoCredito]:
        """
        Cria um novo cartão de crédito com validações de negócio
        
        Args:
            nome: Nome identificador do cartão
            banco: Nome do banco emissor
            bandeira: Bandeira do cartão (Visa, Mastercard, etc.)
            limite: Limite de crédito
            dia_vencimento: Dia do vencimento da fatura (1-31)
            dia_fechamento: Dia de fechamento da fatura (1-31)
            conta_vinculada_id: ID da conta corrente vinculada
            compartilhado_com_alzi: Se o cartão é compartilhado com Alzi
            
        Returns:
            CartaoCredito criado ou None em caso de erro
            
        Raises:
            ValueError: Se os dados de entrada forem inválidos
        """
        # Validações de negócio
        if not nome or not nome.strip():
            raise ValueError("Nome do cartão é obrigatório")
        
        if not banco or not banco.strip():
            raise ValueError("Nome do banco é obrigatório")
        
        if limite <= 0:
            raise ValueError("Limite deve ser maior que zero")
        
        if not (1 <= dia_vencimento <= 31):
            raise ValueError("Dia de vencimento deve estar entre 1 e 31")
        
        if not (1 <= dia_fechamento <= 31):
            raise ValueError("Dia de fechamento deve estar entre 1 e 31")
        
        if dia_vencimento == dia_fechamento:
            raise ValueError("Dia de vencimento e fechamento não podem ser iguais")
        
        # Verificar se a conta vinculada existe (se informada)
        if conta_vinculada_id:
            from .account_service import AccountService
            account_service = AccountService(self.db_manager)
            if not account_service.get_account_by_id(conta_vinculada_id):
                raise ValueError("Conta vinculada não encontrada")
        
        # Verificar se já existe cartão com mesmo nome no mesmo banco
        if self._card_exists(nome, banco):
            raise ValueError(f"Já existe um cartão '{nome}' no banco {banco}")
        
        return self.card_data.create_card(
            nome=nome.strip(),
            banco=banco.strip(),
            bandeira=bandeira,
            limite=limite,
            dia_vencimento=dia_vencimento,
            dia_fechamento=dia_fechamento,
            conta_vinculada_id=conta_vinculada_id,
            compartilhado_com_alzi=compartilhado_com_alzi
        )
    
    def get_card_by_id(self, card_id: str) -> Optional[CartaoCredito]:
        """
        Obtém um cartão pelo ID
        
        Args:
            card_id: ID do cartão
            
        Returns:
            CartaoCredito ou None se não encontrado
        """
        if not card_id:
            return None
        
        return self.card_data.get_card_by_id(card_id)
    
    def list_cards(self, active_only: bool = True, 
                  shared_with_alzi_only: bool = False) -> List[CartaoCredito]:
        """
        Lista cartões com filtros opcionais
        
        Args:
            active_only: Se deve listar apenas cartões ativos
            shared_with_alzi_only: Se deve listar apenas cartões compartilhados com Alzi
            
        Returns:
            Lista de cartões que atendem aos critérios
        """
        cards = self.card_data.list_cards(active_only)
        
        if shared_with_alzi_only:
            cards = [card for card in cards if card.compartilhado_com_alzi]
        
        return cards
    
    def update_card(self, card_id: str, **kwargs) -> bool:
        """
        Atualiza dados de um cartão com validações
        
        Args:
            card_id: ID do cartão a ser atualizado
            **kwargs: Campos a serem atualizados
            
        Returns:
            True se a atualização foi bem-sucedida
            
        Raises:
            ValueError: Se os dados de entrada forem inválidos
        """
        if not card_id:
            raise ValueError("ID do cartão é obrigatório")
        
        # Verificar se o cartão existe
        card = self.get_card_by_id(card_id)
        if not card:
            raise ValueError("Cartão não encontrado")
        
        # Validações específicas para campos que podem ser atualizados
        if 'nome' in kwargs and (not kwargs['nome'] or not kwargs['nome'].strip()):
            raise ValueError("Nome do cartão não pode ser vazio")
        
        if 'banco' in kwargs and (not kwargs['banco'] or not kwargs['banco'].strip()):
            raise ValueError("Nome do banco não pode ser vazio")
        
        if 'limite' in kwargs and kwargs['limite'] <= 0:
            raise ValueError("Limite deve ser maior que zero")
        
        if 'dia_vencimento' in kwargs and not (1 <= kwargs['dia_vencimento'] <= 31):
            raise ValueError("Dia de vencimento deve estar entre 1 e 31")
        
        if 'dia_fechamento' in kwargs and not (1 <= kwargs['dia_fechamento'] <= 31):
            raise ValueError("Dia de fechamento deve estar entre 1 e 31")
        
        # Verificar se vencimento e fechamento serão diferentes
        new_venc = kwargs.get('dia_vencimento', card.dia_vencimento)
        new_fech = kwargs.get('dia_fechamento', card.dia_fechamento)
        if new_venc == new_fech:
            raise ValueError("Dia de vencimento e fechamento não podem ser iguais")
        
        # Verificar conta vinculada se estiver sendo alterada
        if 'conta_vinculada_id' in kwargs and kwargs['conta_vinculada_id']:
            from .account_service import AccountService
            account_service = AccountService(self.db_manager)
            if not account_service.get_account_by_id(kwargs['conta_vinculada_id']):
                raise ValueError("Conta vinculada não encontrada")
        
        # Verificar duplicação de nome se estiver sendo alterado
        if 'nome' in kwargs or 'banco' in kwargs:
            new_nome = kwargs.get('nome', card.nome)
            new_banco = kwargs.get('banco', card.banco)
            
            if self._card_exists(new_nome, new_banco, exclude_id=card_id):
                raise ValueError(f"Já existe um cartão '{new_nome}' no banco {new_banco}")
        
        # Validar limite disponível se limite estiver sendo alterado
        if 'limite' in kwargs:
            new_limite = kwargs['limite']
            # O limite disponível não pode exceder o novo limite
            if card.limite_disponivel > new_limite:
                kwargs['limite_disponivel'] = new_limite
        
        return self.card_data.update_card(card_id, **kwargs)
    
    def deactivate_card(self, card_id: str) -> bool:
        """
        Desativa um cartão (soft delete)
        
        Args:
            card_id: ID do cartão a ser desativado
            
        Returns:
            True se a desativação foi bem-sucedida
        """
        if not card_id:
            raise ValueError("ID do cartão é obrigatório")
        
        card = self.get_card_by_id(card_id)
        if not card:
            raise ValueError("Cartão não encontrado")
        
        return self.card_data.update_card(card_id, ativo=False)
    
    def activate_card(self, card_id: str) -> bool:
        """
        Reativa um cartão desativado
        
        Args:
            card_id: ID do cartão a ser reativado
            
        Returns:
            True se a reativação foi bem-sucedida
        """
        if not card_id:
            raise ValueError("ID do cartão é obrigatório")
        
        return self.card_data.update_card(card_id, ativo=True)
    
    def update_available_limit(self, card_id: str, valor: float, operation: str = 'decrease') -> bool:
        """
        Atualiza o limite disponível de um cartão
        
        Args:
            card_id: ID do cartão
            valor: Valor a ser adicionado ou subtraído
            operation: 'decrease' para diminuir (compra) ou 'increase' para aumentar (pagamento)
            
        Returns:
            True se a atualização foi bem-sucedida
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
        """
        if not card_id:
            raise ValueError("ID do cartão é obrigatório")
        
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")
        
        if operation not in ['decrease', 'increase']:
            raise ValueError("Operação deve ser 'decrease' ou 'increase'")
        
        card = self.get_card_by_id(card_id)
        if not card:
            raise ValueError("Cartão não encontrado")
        
        # Calcular novo limite disponível
        if operation == 'decrease':
            novo_limite_disponivel = card.limite_disponivel - valor
            # Não permitir que fique negativo
            if novo_limite_disponivel < 0:
                raise ValueError("Limite insuficiente para esta operação")
        else:  # increase
            novo_limite_disponivel = card.limite_disponivel + valor
            # Não permitir que exceda o limite total
            novo_limite_disponivel = min(novo_limite_disponivel, card.limite)
        
        return self.card_data.update_card(card_id, limite_disponivel=novo_limite_disponivel)
    
    def get_total_limit(self, active_only: bool = True) -> Dict[str, float]:
        """
        Calcula os limites totais de todos os cartões
        
        Args:
            active_only: Se deve considerar apenas cartões ativos
            
        Returns:
            Dicionário com limite total e disponível
        """
        cards = self.list_cards(active_only=active_only)
        
        return {
            'total_limit': sum(card.limite for card in cards),
            'available_limit': sum(card.limite_disponivel for card in cards),
            'used_limit': sum(card.limite - card.limite_disponivel for card in cards)
        }
    
    def get_shared_cards_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo dos cartões compartilhados com Alzi
        
        Returns:
            Dicionário com estatísticas dos cartões compartilhados
        """
        shared_cards = self.list_cards(shared_with_alzi_only=True)
        
        return {
            'total_cards': len(shared_cards),
            'total_limit': sum(card.limite for card in shared_cards),
            'available_limit': sum(card.limite_disponivel for card in shared_cards),
            'used_limit': sum(card.limite - card.limite_disponivel for card in shared_cards),
            'cards_by_brand': self._group_cards_by_brand(shared_cards),
            'cards': shared_cards
        }
    
    def get_cards_by_due_date(self, active_only: bool = True) -> Dict[int, List[CartaoCredito]]:
        """
        Agrupa cartões por dia de vencimento
        
        Args:
            active_only: Se deve considerar apenas cartões ativos
            
        Returns:
            Dicionário com cartões agrupados por dia de vencimento
        """
        cards = self.list_cards(active_only=active_only)
        grouped = {}
        
        for card in cards:
            day = card.dia_vencimento
            if day not in grouped:
                grouped[day] = []
            grouped[day].append(card)
        
        return grouped
    
    def validate_billing_dates(self, dia_vencimento: int, dia_fechamento: int) -> bool:
        """
        Valida se as datas de vencimento e fechamento fazem sentido
        
        Args:
            dia_vencimento: Dia do vencimento
            dia_fechamento: Dia do fechamento
            
        Returns:
            True se as datas são válidas
        """
        # Validações básicas
        if not (1 <= dia_vencimento <= 31) or not (1 <= dia_fechamento <= 31):
            return False
        
        if dia_vencimento == dia_fechamento:
            return False
        
        # O vencimento deve ser após o fechamento (considerando mês seguinte)
        # Ex: fechamento dia 20, vencimento dia 10 do mês seguinte
        return True
    
    def _card_exists(self, nome: str, banco: str, exclude_id: Optional[str] = None) -> bool:
        """
        Verifica se já existe um cartão com os mesmos dados
        
        Args:
            nome: Nome do cartão
            banco: Nome do banco
            exclude_id: ID de cartão a ser excluído da verificação
            
        Returns:
            True se o cartão já existe
        """
        cards = self.card_data.list_cards(active_only=False)
        
        for card in cards:
            if (card.nome.lower() == nome.lower() and 
                card.banco.lower() == banco.lower() and
                card.id != exclude_id):
                return True
        
        return False
    
    def _group_cards_by_brand(self, cards: List[CartaoCredito]) -> Dict[str, int]:
        """
        Agrupa cartões por bandeira
        
        Args:
            cards: Lista de cartões
            
        Returns:
            Dicionário com contagem por bandeira
        """
        grouped = {}
        for card in cards:
            brand = card.bandeira.value if hasattr(card.bandeira, 'value') else str(card.bandeira)
            grouped[brand] = grouped.get(brand, 0) + 1
        
        return grouped