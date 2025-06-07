"""
Domínio de Períodos - Regras de Negócio para Datas e Períodos

Esta classe contém todas as regras de negócio relacionadas a cálculos de períodos,
datas de vencimento, fechamento e validações temporais.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from calendar import monthrange
import locale

# Tentar configurar locale brasileiro
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except:
        pass  # Usar locale padrão se não conseguir


class PeriodDomain:
    """
    Domínio responsável pelas regras de negócio de períodos e datas
    """

    # Constantes de período
    MONTHS_NAMES = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    @staticmethod
    def get_current_period() -> Dict[str, int]:
        """
        Retorna período atual (mês/ano)
        
        Returns:
            Dict com mês e ano atuais
        """
        now = datetime.now()
        return {
            'mes': now.month,
            'ano': now.year,
            'dia': now.day
        }

    @staticmethod
    def get_month_name(month: int) -> str:
        """
        Retorna nome do mês em português
        
        Args:
            month: Número do mês (1-12)
            
        Returns:
            Nome do mês
        """
        if 1 <= month <= 12:
            return PeriodDomain.MONTHS_NAMES[month - 1]
        return f"Mês {month}"

    @staticmethod
    def get_month_range(year: int, month: int) -> Tuple[date, date]:
        """
        Retorna primeiro e último dia do mês
        
        Args:
            year: Ano
            month: Mês
            
        Returns:
            Tupla com (primeiro_dia, ultimo_dia)
        """
        first_day = date(year, month, 1)
        last_day_num = monthrange(year, month)[1]
        last_day = date(year, month, last_day_num)
        
        return first_day, last_day

    @staticmethod
    def get_previous_month(year: int, month: int) -> Tuple[int, int]:
        """
        Retorna mês anterior
        
        Args:
            year: Ano
            month: Mês
            
        Returns:
            Tupla com (mês, ano) anterior
        """
        if month == 1:
            return 12, year - 1
        else:
            return month - 1, year

    @staticmethod
    def get_next_month(year: int, month: int) -> Tuple[int, int]:
        """
        Retorna próximo mês
        
        Args:
            year: Ano
            month: Mês
            
        Returns:
            Tupla com (mês, ano) seguinte
        """
        if month == 12:
            return 1, year + 1
        else:
            return month + 1, year

    @staticmethod
    def adjust_day_to_month(day: int, year: int, month: int) -> int:
        """
        Ajusta dia para ser válido no mês especificado
        
        Args:
            day: Dia desejado
            year: Ano
            month: Mês
            
        Returns:
            Dia ajustado válido para o mês
        """
        last_day = monthrange(year, month)[1]
        return min(day, last_day)

    @staticmethod
    def calculate_due_date(
        base_date: date,
        due_day: int,
        months_ahead: int = 1
    ) -> date:
        """
        Calcula data de vencimento baseada numa data base
        
        Args:
            base_date: Data base para cálculo
            due_day: Dia de vencimento desejado
            months_ahead: Meses à frente (default: 1)
            
        Returns:
            Data de vencimento calculada
        """
        target_month = base_date.month + months_ahead
        target_year = base_date.year
        
        # Ajustar ano se necessário
        while target_month > 12:
            target_month -= 12
            target_year += 1
            
        # Ajustar dia se não existir no mês alvo
        adjusted_day = PeriodDomain.adjust_day_to_month(due_day, target_year, target_month)
        
        return date(target_year, target_month, adjusted_day)

    @staticmethod
    def is_date_in_period(
        check_date: date,
        start_date: date,
        end_date: date,
        inclusive: bool = True
    ) -> bool:
        """
        Verifica se uma data está dentro de um período
        
        Args:
            check_date: Data a ser verificada
            start_date: Data de início do período
            end_date: Data de fim do período
            inclusive: Se as datas limites são inclusivas
            
        Returns:
            True se a data está no período
        """
        if inclusive:
            return start_date <= check_date <= end_date
        else:
            return start_date < check_date < end_date

    @staticmethod
    def get_periods_between_dates(
        start_date: date,
        end_date: date
    ) -> List[Dict[str, int]]:
        """
        Retorna lista de períodos (mês/ano) entre duas datas
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Lista de dicionários com mês e ano
        """
        periods = []
        current = date(start_date.year, start_date.month, 1)
        end_month = date(end_date.year, end_date.month, 1)
        
        while current <= end_month:
            periods.append({
                'mes': current.month,
                'ano': current.year,
                'nome': PeriodDomain.get_month_name(current.month)
            })
            
            # Avançar para próximo mês
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
                
        return periods

    @staticmethod
    def validate_date_string(date_string: str) -> Dict[str, Any]:
        """
        Valida string de data em vários formatos
        
        Args:
            date_string: String da data
            
        Returns:
            Dict com resultado da validação
        """
        formats_to_try = [
            '%Y-%m-%d',           # 2024-03-15
            '%d/%m/%Y',           # 15/03/2024
            '%d-%m-%Y',           # 15-03-2024
            '%Y-%m-%dT%H:%M:%S',  # 2024-03-15T10:30:00
            '%Y-%m-%d %H:%M:%S',  # 2024-03-15 10:30:00
        ]
        
        for date_format in formats_to_try:
            try:
                parsed_date = datetime.strptime(date_string, date_format)
                return {
                    'valid': True,
                    'date': parsed_date.date(),
                    'datetime': parsed_date,
                    'format_used': date_format
                }
            except ValueError:
                continue
                
        return {
            'valid': False,
            'error': 'Formato de data não reconhecido'
        }

    @staticmethod
    def format_date_br(input_date: date) -> str:
        """
        Formata data no padrão brasileiro (dd/mm/yyyy)
        
        Args:
            input_date: Data a ser formatada
            
        Returns:
            Data formatada em string
        """
        return input_date.strftime('%d/%m/%Y')

    @staticmethod
    def format_period_display(year: int, month: int) -> str:
        """
        Formata período para exibição (Mês/Ano)
        
        Args:
            year: Ano
            month: Mês
            
        Returns:
            Período formatado
        """
        month_name = PeriodDomain.get_month_name(month)
        return f"{month_name}/{year}"

    @staticmethod
    def calculate_days_between(start_date: date, end_date: date) -> int:
        """
        Calcula número de dias entre duas datas
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Número de dias
        """
        delta = end_date - start_date
        return delta.days

    @staticmethod
    def is_business_day(check_date: date) -> bool:
        """
        Verifica se uma data é dia útil (segunda a sexta)
        
        Args:
            check_date: Data a ser verificada
            
        Returns:
            True se é dia útil
        """
        # weekday(): 0=segunda, 6=domingo
        return check_date.weekday() < 5

    @staticmethod
    def get_next_business_day(check_date: date) -> date:
        """
        Retorna próximo dia útil após a data informada
        
        Args:
            check_date: Data base
            
        Returns:
            Próximo dia útil
        """
        current = check_date + timedelta(days=1)
        
        while not PeriodDomain.is_business_day(current):
            current += timedelta(days=1)
            
        return current

    @staticmethod
    def calculate_age_in_days(creation_date: date) -> int:
        """
        Calcula idade em dias a partir de uma data de criação
        
        Args:
            creation_date: Data de criação
            
        Returns:
            Idade em dias
        """
        today = date.today()
        return PeriodDomain.calculate_days_between(creation_date, today)

    @staticmethod
    def get_quarter_info(month: int) -> Dict[str, Any]:
        """
        Retorna informações do trimestre baseado no mês
        
        Args:
            month: Mês (1-12)
            
        Returns:
            Dict com informações do trimestre
        """
        if 1 <= month <= 3:
            quarter = 1
            quarter_months = [1, 2, 3]
        elif 4 <= month <= 6:
            quarter = 2
            quarter_months = [4, 5, 6]
        elif 7 <= month <= 9:
            quarter = 3
            quarter_months = [7, 8, 9]
        else:  # 10-12
            quarter = 4
            quarter_months = [10, 11, 12]
            
        return {
            'trimestre': quarter,
            'meses': quarter_months,
            'nome': f"{quarter}º Trimestre"
        }

    @staticmethod
    def get_recent_periods(count: int = 6) -> List[Dict[str, Any]]:
        """
        Retorna lista dos últimos períodos (meses)
        
        Args:
            count: Quantidade de períodos a retornar
            
        Returns:
            Lista dos últimos períodos
        """
        periods = []
        current = datetime.now()
        
        for i in range(count):
            year = current.year
            month = current.month - i
            
            # Ajustar ano se necessário
            while month <= 0:
                month += 12
                year -= 1
                
            periods.append({
                'mes': month,
                'ano': year,
                'nome': PeriodDomain.get_month_name(month),
                'display': PeriodDomain.format_period_display(year, month),
                'is_current': (month == datetime.now().month and year == datetime.now().year)
            })
            
        return periods