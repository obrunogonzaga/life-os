"""
Finance Service - Serviço principal que orquestra todos os outros services
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import csv
import re
from pathlib import Path

from .account_service import AccountService
from .card_service import CardService
from .transaction_service import TransactionService
from .period_service import PeriodService
from .alzi_service import AlziService
from utils.database_manager import DatabaseManager
from utils.finance_models import (
    ContaCorrente, CartaoCredito, Transacao, ResumoFinanceiro,
    TipoTransacao, StatusTransacao, TipoConta, BandeiraCartao
)


class FinanceService:
    """
    Serviço principal do módulo de finanças
    Coordena todos os outros services e fornece interface unificada
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or DatabaseManager()
        
        # Inicializar services
        self.account_service = AccountService(self.db_manager)
        self.card_service = CardService(self.db_manager)
        self.transaction_service = TransactionService(self.db_manager)
        self.period_service = PeriodService(self.db_manager)
        self.alzi_service = AlziService(self.db_manager)
    
    # =================
    # MÉTODOS DE CONTAS
    # =================
    
    def criar_conta(self, nome: str, banco: str, agencia: str, conta: str, 
                   tipo: TipoConta, saldo_inicial: float, 
                   compartilhado_com_alzi: bool = False) -> Optional[ContaCorrente]:
        """Cria uma nova conta corrente"""
        return self.account_service.create_account(
            nome, banco, agencia, conta, tipo, saldo_inicial, compartilhado_com_alzi
        )
    
    def listar_contas(self, ativas_apenas: bool = True) -> List[ContaCorrente]:
        """Lista todas as contas correntes"""
        return self.account_service.list_accounts(active_only=ativas_apenas)
    
    def obter_conta(self, conta_id: str) -> Optional[ContaCorrente]:
        """Obtém uma conta específica"""
        return self.account_service.get_account_by_id(conta_id)
    
    def atualizar_conta(self, conta_id: str, **kwargs) -> bool:
        """Atualiza uma conta corrente"""
        return self.account_service.update_account(conta_id, **kwargs)
    
    def excluir_conta(self, conta_id: str) -> bool:
        """Exclui (desativa) uma conta corrente"""
        return self.account_service.deactivate_account(conta_id)
    
    # ==================
    # MÉTODOS DE CARTÕES
    # ==================
    
    def criar_cartao(self, nome: str, banco: str, bandeira: BandeiraCartao, 
                    limite: float, dia_vencimento: int, dia_fechamento: int,
                    conta_vinculada_id: Optional[str] = None,
                    compartilhado_com_alzi: bool = False) -> Optional[CartaoCredito]:
        """Cria um novo cartão de crédito"""
        return self.card_service.create_card(
            nome, banco, bandeira, limite, dia_vencimento, dia_fechamento,
            conta_vinculada_id, compartilhado_com_alzi
        )
    
    def listar_cartoes(self, ativos_apenas: bool = True) -> List[CartaoCredito]:
        """Lista todos os cartões de crédito"""
        return self.card_service.list_cards(active_only=ativos_apenas)
    
    def obter_cartao(self, cartao_id: str) -> Optional[CartaoCredito]:
        """Obtém um cartão específico"""
        return self.card_service.get_card_by_id(cartao_id)
    
    def atualizar_cartao(self, cartao_id: str, **kwargs) -> bool:
        """Atualiza um cartão de crédito"""
        return self.card_service.update_card(cartao_id, **kwargs)
    
    def excluir_cartao(self, cartao_id: str) -> bool:
        """Exclui (desativa) um cartão de crédito"""
        return self.card_service.deactivate_card(cartao_id)
    
    # ======================
    # MÉTODOS DE TRANSAÇÕES
    # ======================
    
    def criar_transacao(self, descricao: str, valor: float, tipo: TipoTransacao,
                       data_transacao: str, categoria: Optional[str] = None,
                       conta_id: Optional[str] = None, cartao_id: Optional[str] = None,
                       parcelas: int = 1, observacoes: Optional[str] = None,
                       compartilhado_com_alzi: bool = False) -> Optional[Transacao]:
        """Cria uma nova transação"""
        return self.transaction_service.create_transaction(
            descricao, valor, tipo, data_transacao, categoria,
            conta_id, cartao_id, parcelas, observacoes, compartilhado_com_alzi
        )
    
    def listar_transacoes(self, filtros: Optional[Dict[str, Any]] = None) -> List[Transacao]:
        """Lista transações com filtros opcionais"""
        return self.transaction_service.list_transactions(filtros)
    
    def obter_transacao(self, transacao_id: str) -> Optional[Transacao]:
        """Obtém uma transação específica"""
        return self.transaction_service.get_transaction_by_id(transacao_id)
    
    def atualizar_transacao(self, transacao_id: str, **kwargs) -> bool:
        """Atualiza uma transação"""
        return self.transaction_service.update_transaction(transacao_id, **kwargs)
    
    def excluir_transacao(self, transacao_id: str) -> bool:
        """Exclui uma transação"""
        return self.transaction_service.delete_transaction(transacao_id)
    
    def excluir_multiplas_transacoes(self, transacao_ids: List[str]) -> Dict[str, Any]:
        """Exclui múltiplas transações"""
        return self.transaction_service.delete_multiple_transactions(transacao_ids)
    
    # ===================
    # MÉTODOS DE PERÍODOS
    # ===================
    
    def obter_transacoes_mes(self, ano: int, mes: int, 
                           compartilhadas_apenas: bool = False) -> List[Transacao]:
        """Obtém transações de um mês específico"""
        return self.transaction_service.get_transactions_by_month(ano, mes, compartilhadas_apenas)
    
    def obter_transacoes_fatura_cartao(self, cartao_id: str, mes_fatura: int, ano_fatura: int) -> List[Transacao]:
        """Obtém transações de uma fatura específica do cartão"""
        return self.period_service.get_billing_period_transactions(cartao_id, mes_fatura, ano_fatura)
    
    def listar_faturas_cartao(self, cartao_id: str, ano: int = None) -> List[Dict[str, Any]]:
        """Lista todas as faturas que possuem transações para um cartão específico"""
        return self.period_service.list_card_invoices(cartao_id, ano)
    
    def excluir_fatura_completa(self, cartao_id: str, mes_fatura: int, ano_fatura: int) -> Dict[str, Any]:
        """Exclui todas as transações de uma fatura específica"""
        try:
            # Obter todas as transações da fatura
            transacoes = self.obter_transacoes_fatura_cartao(cartao_id, mes_fatura, ano_fatura)
            
            if not transacoes:
                return {
                    'sucesso': True,
                    'total_transacoes': 0,
                    'excluidas': 0,
                    'erros': []
                }
            
            # Coletar IDs das transações
            transacao_ids = [t.id for t in transacoes]
            
            # Excluir em lote
            resultado = self.excluir_multiplas_transacoes(transacao_ids)
            resultado['total_transacoes'] = len(transacoes)
            resultado['mes_fatura'] = mes_fatura
            resultado['ano_fatura'] = ano_fatura
            
            return resultado
            
        except Exception as e:
            return {
                'sucesso': False,
                'total_transacoes': 0,
                'excluidas': 0,
                'erros': [f"Erro ao excluir fatura: {e}"]
            }
    
    # =================
    # MÉTODOS DE ALZI
    # =================
    
    def obter_resumo_compartilhado_mes(self, ano: int, mes: int) -> Dict[str, Any]:
        """Obtém resumo das transações compartilhadas de um mês"""
        return self.alzi_service.get_shared_transactions_summary(ano, mes)
    
    def obter_resumo_compartilhado_atual(self) -> Dict[str, Any]:
        """Obtém resumo das transações compartilhadas do mês atual"""
        return self.alzi_service.get_current_month_summary()
    
    def obter_relatorio_completo_alzi(self, ano: int, mes: int) -> Dict[str, Any]:
        """Gera relatório completo dos gastos compartilhados"""
        return self.alzi_service.get_comprehensive_shared_report(ano, mes)
    
    # ===================
    # MÉTODOS DE RESUMO
    # ===================
    
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
    
    # ========================
    # MÉTODOS DE IMPORTAÇÃO
    # ========================
    
    def detectar_formato_csv(self, arquivo_path: str) -> Optional[str]:
        """Detecta o formato do arquivo CSV (Bradesco, Itaú, BTG)"""
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
    
    def importar_transacoes_csv(self, arquivo_path: str, cartao_id: str) -> Dict[str, Any]:
        """Importa transações de um arquivo CSV"""
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
            transacoes_data, total_linhas, transacoes_encontradas = self._processar_csv_bradesco(arquivo_path, cartao_id)
            
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
    
    def _processar_csv_bradesco(self, arquivo_path: str, cartao_id: str) -> Tuple[List[Dict], int, int]:
        """Processa arquivo CSV do Bradesco e retorna transações processadas"""
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
    
    def _gerar_csv_limpo(self, transacoes_data: List[Dict], arquivo_original: str) -> str:
        """Gera um arquivo CSV limpo com as transações processadas"""
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