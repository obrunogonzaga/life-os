"""
Testes unitários para PeriodDomain

Testa todas as regras de negócio relacionadas a períodos, datas
e cálculos temporais.
"""

import unittest
from datetime import datetime, date, timedelta
from calendar import monthrange

# Adicionar caminho para imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finances.domains import PeriodDomain


class TestPeriodDomain(unittest.TestCase):
    """Testes para PeriodDomain"""

    def test_get_current_period(self):
        """Testa obtenção do período atual"""
        current = PeriodDomain.get_current_period()
        now = datetime.now()
        
        self.assertEqual(current['mes'], now.month)
        self.assertEqual(current['ano'], now.year)
        self.assertEqual(current['dia'], now.day)

    def test_get_month_name_valid(self):
        """Testa obtenção de nomes de meses válidos"""
        self.assertEqual(PeriodDomain.get_month_name(1), 'Janeiro')
        self.assertEqual(PeriodDomain.get_month_name(6), 'Junho')
        self.assertEqual(PeriodDomain.get_month_name(12), 'Dezembro')

    def test_get_month_name_invalid(self):
        """Testa obtenção de nomes para meses inválidos"""
        self.assertEqual(PeriodDomain.get_month_name(0), 'Mês 0')
        self.assertEqual(PeriodDomain.get_month_name(13), 'Mês 13')
        self.assertEqual(PeriodDomain.get_month_name(-1), 'Mês -1')

    def test_get_month_range_normal(self):
        """Testa obtenção de range de mês normal"""
        first_day, last_day = PeriodDomain.get_month_range(2024, 3)
        
        self.assertEqual(first_day, date(2024, 3, 1))
        self.assertEqual(last_day, date(2024, 3, 31))

    def test_get_month_range_february_leap(self):
        """Testa obtenção de range para fevereiro bissexto"""
        first_day, last_day = PeriodDomain.get_month_range(2024, 2)
        
        self.assertEqual(first_day, date(2024, 2, 1))
        self.assertEqual(last_day, date(2024, 2, 29))  # 2024 é bissexto

    def test_get_month_range_february_normal(self):
        """Testa obtenção de range para fevereiro normal"""
        first_day, last_day = PeriodDomain.get_month_range(2023, 2)
        
        self.assertEqual(first_day, date(2023, 2, 1))
        self.assertEqual(last_day, date(2023, 2, 28))  # 2023 não é bissexto

    def test_get_previous_month_normal(self):
        """Testa obtenção do mês anterior normal"""
        prev_month, prev_year = PeriodDomain.get_previous_month(2024, 6)
        
        self.assertEqual(prev_month, 5)
        self.assertEqual(prev_year, 2024)

    def test_get_previous_month_january(self):
        """Testa obtenção do mês anterior para janeiro"""
        prev_month, prev_year = PeriodDomain.get_previous_month(2024, 1)
        
        self.assertEqual(prev_month, 12)
        self.assertEqual(prev_year, 2023)

    def test_get_next_month_normal(self):
        """Testa obtenção do próximo mês normal"""
        next_month, next_year = PeriodDomain.get_next_month(2024, 6)
        
        self.assertEqual(next_month, 7)
        self.assertEqual(next_year, 2024)

    def test_get_next_month_december(self):
        """Testa obtenção do próximo mês para dezembro"""
        next_month, next_year = PeriodDomain.get_next_month(2024, 12)
        
        self.assertEqual(next_month, 1)
        self.assertEqual(next_year, 2025)

    def test_adjust_day_to_month_normal(self):
        """Testa ajuste de dia normal"""
        adjusted = PeriodDomain.adjust_day_to_month(15, 2024, 3)
        
        self.assertEqual(adjusted, 15)  # Março tem 31 dias

    def test_adjust_day_to_month_february(self):
        """Testa ajuste de dia para fevereiro"""
        adjusted = PeriodDomain.adjust_day_to_month(31, 2024, 2)
        
        self.assertEqual(adjusted, 29)  # Fevereiro 2024 tem 29 dias

    def test_adjust_day_to_month_february_normal_year(self):
        """Testa ajuste de dia para fevereiro ano normal"""
        adjusted = PeriodDomain.adjust_day_to_month(30, 2023, 2)
        
        self.assertEqual(adjusted, 28)  # Fevereiro 2023 tem 28 dias

    def test_calculate_due_date_normal(self):
        """Testa cálculo de data de vencimento normal"""
        base_date = date(2024, 3, 10)
        due_date = PeriodDomain.calculate_due_date(base_date, 15, 1)
        
        self.assertEqual(due_date, date(2024, 4, 15))

    def test_calculate_due_date_multiple_months(self):
        """Testa cálculo de data de vencimento múltiplos meses"""
        base_date = date(2024, 3, 10)
        due_date = PeriodDomain.calculate_due_date(base_date, 15, 3)
        
        self.assertEqual(due_date, date(2024, 6, 15))

    def test_calculate_due_date_year_transition(self):
        """Testa cálculo com transição de ano"""
        base_date = date(2024, 11, 10)
        due_date = PeriodDomain.calculate_due_date(base_date, 15, 3)
        
        self.assertEqual(due_date, date(2025, 2, 15))

    def test_calculate_due_date_february_adjustment(self):
        """Testa cálculo com ajuste para fevereiro"""
        base_date = date(2024, 1, 31)
        due_date = PeriodDomain.calculate_due_date(base_date, 31, 1)
        
        self.assertEqual(due_date, date(2024, 2, 29))  # Ajustado para 29

    def test_is_date_in_period_inclusive_true(self):
        """Testa se data está no período (inclusivo, verdadeiro)"""
        start_date = date(2024, 3, 1)
        end_date = date(2024, 3, 31)
        check_date = date(2024, 3, 15)
        
        result = PeriodDomain.is_date_in_period(check_date, start_date, end_date, True)
        self.assertTrue(result)

    def test_is_date_in_period_inclusive_boundary(self):
        """Testa se data está no período (inclusivo, fronteira)"""
        start_date = date(2024, 3, 1)
        end_date = date(2024, 3, 31)
        
        # Testar início
        result = PeriodDomain.is_date_in_period(start_date, start_date, end_date, True)
        self.assertTrue(result)
        
        # Testar fim
        result = PeriodDomain.is_date_in_period(end_date, start_date, end_date, True)
        self.assertTrue(result)

    def test_is_date_in_period_exclusive_boundary(self):
        """Testa se data está no período (exclusivo, fronteira)"""
        start_date = date(2024, 3, 1)
        end_date = date(2024, 3, 31)
        
        # Testar início (exclusivo)
        result = PeriodDomain.is_date_in_period(start_date, start_date, end_date, False)
        self.assertFalse(result)
        
        # Testar fim (exclusivo)
        result = PeriodDomain.is_date_in_period(end_date, start_date, end_date, False)
        self.assertFalse(result)

    def test_is_date_in_period_false(self):
        """Testa se data está no período (falso)"""
        start_date = date(2024, 3, 1)
        end_date = date(2024, 3, 31)
        check_date = date(2024, 4, 1)
        
        result = PeriodDomain.is_date_in_period(check_date, start_date, end_date, True)
        self.assertFalse(result)

    def test_get_periods_between_dates_same_month(self):
        """Testa períodos entre datas do mesmo mês"""
        start_date = date(2024, 3, 1)
        end_date = date(2024, 3, 31)
        
        periods = PeriodDomain.get_periods_between_dates(start_date, end_date)
        
        self.assertEqual(len(periods), 1)
        self.assertEqual(periods[0]['mes'], 3)
        self.assertEqual(periods[0]['ano'], 2024)
        self.assertEqual(periods[0]['nome'], 'Março')

    def test_get_periods_between_dates_multiple_months(self):
        """Testa períodos entre datas de múltiplos meses"""
        start_date = date(2024, 3, 1)
        end_date = date(2024, 5, 31)
        
        periods = PeriodDomain.get_periods_between_dates(start_date, end_date)
        
        self.assertEqual(len(periods), 3)
        self.assertEqual(periods[0]['mes'], 3)
        self.assertEqual(periods[1]['mes'], 4)
        self.assertEqual(periods[2]['mes'], 5)
        self.assertEqual(periods[0]['nome'], 'Março')
        self.assertEqual(periods[1]['nome'], 'Abril')
        self.assertEqual(periods[2]['nome'], 'Maio')

    def test_get_periods_between_dates_year_transition(self):
        """Testa períodos com transição de ano"""
        start_date = date(2024, 11, 1)
        end_date = date(2025, 2, 28)
        
        periods = PeriodDomain.get_periods_between_dates(start_date, end_date)
        
        self.assertEqual(len(periods), 4)
        self.assertEqual(periods[0]['mes'], 11)
        self.assertEqual(periods[0]['ano'], 2024)
        self.assertEqual(periods[1]['mes'], 12)
        self.assertEqual(periods[1]['ano'], 2024)
        self.assertEqual(periods[2]['mes'], 1)
        self.assertEqual(periods[2]['ano'], 2025)
        self.assertEqual(periods[3]['mes'], 2)
        self.assertEqual(periods[3]['ano'], 2025)

    def test_validate_date_string_iso_format(self):
        """Testa validação de data ISO"""
        result = PeriodDomain.validate_date_string('2024-03-15')
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['date'], date(2024, 3, 15))
        self.assertEqual(result['format_used'], '%Y-%m-%d')

    def test_validate_date_string_brazilian_format(self):
        """Testa validação de data brasileira"""
        result = PeriodDomain.validate_date_string('15/03/2024')
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['date'], date(2024, 3, 15))
        self.assertEqual(result['format_used'], '%d/%m/%Y')

    def test_validate_date_string_datetime(self):
        """Testa validação de data com hora"""
        result = PeriodDomain.validate_date_string('2024-03-15T10:30:00')
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['date'], date(2024, 3, 15))
        self.assertEqual(result['datetime'].hour, 10)
        self.assertEqual(result['datetime'].minute, 30)

    def test_validate_date_string_invalid(self):
        """Testa validação de data inválida"""
        result = PeriodDomain.validate_date_string('data-inválida')
        
        self.assertFalse(result['valid'])
        self.assertIn('Formato de data não reconhecido', result['error'])

    def test_format_date_br(self):
        """Testa formatação brasileira"""
        input_date = date(2024, 3, 15)
        formatted = PeriodDomain.format_date_br(input_date)
        
        self.assertEqual(formatted, '15/03/2024')

    def test_format_period_display(self):
        """Testa formatação de período para exibição"""
        formatted = PeriodDomain.format_period_display(2024, 3)
        
        self.assertEqual(formatted, 'Março/2024')

    def test_calculate_days_between(self):
        """Testa cálculo de dias entre datas"""
        start_date = date(2024, 3, 1)
        end_date = date(2024, 3, 31)
        
        days = PeriodDomain.calculate_days_between(start_date, end_date)
        
        self.assertEqual(days, 30)

    def test_calculate_days_between_negative(self):
        """Testa cálculo de dias com data final antes da inicial"""
        start_date = date(2024, 3, 31)
        end_date = date(2024, 3, 1)
        
        days = PeriodDomain.calculate_days_between(start_date, end_date)
        
        self.assertEqual(days, -30)

    def test_is_business_day_weekday(self):
        """Testa se é dia útil (dia de semana)"""
        # Segunda-feira
        monday = date(2024, 3, 11)  # 11/03/2024 é segunda
        self.assertTrue(PeriodDomain.is_business_day(monday))
        
        # Sexta-feira
        friday = date(2024, 3, 15)  # 15/03/2024 é sexta
        self.assertTrue(PeriodDomain.is_business_day(friday))

    def test_is_business_day_weekend(self):
        """Testa se é dia útil (final de semana)"""
        # Sábado
        saturday = date(2024, 3, 16)  # 16/03/2024 é sábado
        self.assertFalse(PeriodDomain.is_business_day(saturday))
        
        # Domingo
        sunday = date(2024, 3, 17)  # 17/03/2024 é domingo
        self.assertFalse(PeriodDomain.is_business_day(sunday))

    def test_get_next_business_day_from_friday(self):
        """Testa próximo dia útil a partir de sexta"""
        friday = date(2024, 3, 15)  # 15/03/2024 é sexta
        next_business = PeriodDomain.get_next_business_day(friday)
        
        # Deve ser segunda-feira
        self.assertEqual(next_business, date(2024, 3, 18))  # 18/03/2024 é segunda

    def test_get_next_business_day_from_weekday(self):
        """Testa próximo dia útil a partir de dia útil"""
        tuesday = date(2024, 3, 12)  # 12/03/2024 é terça
        next_business = PeriodDomain.get_next_business_day(tuesday)
        
        # Deve ser quarta-feira
        self.assertEqual(next_business, date(2024, 3, 13))  # 13/03/2024 é quarta

    def test_calculate_age_in_days(self):
        """Testa cálculo de idade em dias"""
        # Data de criação há 10 dias
        creation_date = date.today() - timedelta(days=10)
        age = PeriodDomain.calculate_age_in_days(creation_date)
        
        self.assertEqual(age, 10)

    def test_get_quarter_info_q1(self):
        """Testa informações do primeiro trimestre"""
        quarter_info = PeriodDomain.get_quarter_info(2)
        
        self.assertEqual(quarter_info['trimestre'], 1)
        self.assertEqual(quarter_info['meses'], [1, 2, 3])
        self.assertEqual(quarter_info['nome'], '1º Trimestre')

    def test_get_quarter_info_q4(self):
        """Testa informações do quarto trimestre"""
        quarter_info = PeriodDomain.get_quarter_info(11)
        
        self.assertEqual(quarter_info['trimestre'], 4)
        self.assertEqual(quarter_info['meses'], [10, 11, 12])
        self.assertEqual(quarter_info['nome'], '4º Trimestre')

    def test_get_recent_periods(self):
        """Testa obtenção de períodos recentes"""
        periods = PeriodDomain.get_recent_periods(3)
        
        self.assertEqual(len(periods), 3)
        
        # Primeiro período deve ser o atual
        current_month = datetime.now().month
        current_year = datetime.now().year
        self.assertEqual(periods[0]['mes'], current_month)
        self.assertEqual(periods[0]['ano'], current_year)
        self.assertTrue(periods[0]['is_current'])
        
        # Outros períodos não devem ser atuais
        self.assertFalse(periods[1]['is_current'])
        self.assertFalse(periods[2]['is_current'])

    def test_get_recent_periods_year_transition(self):
        """Testa períodos recentes com transição de ano"""
        # Simular que estamos em janeiro para testar transição
        periods = PeriodDomain.get_recent_periods(6)
        
        # Deve retornar 6 períodos
        self.assertEqual(len(periods), 6)
        
        # Todos devem ter 'display' formatado
        for period in periods:
            self.assertIn('display', period)
            self.assertIn('nome', period)
            self.assertIn('is_current', period)

    def test_months_names_constant(self):
        """Testa se a constante de nomes de meses está correta"""
        self.assertEqual(len(PeriodDomain.MONTHS_NAMES), 12)
        self.assertEqual(PeriodDomain.MONTHS_NAMES[0], 'Janeiro')
        self.assertEqual(PeriodDomain.MONTHS_NAMES[11], 'Dezembro')


if __name__ == '__main__':
    unittest.main()