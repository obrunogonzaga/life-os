from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TipoTransacao(Enum):
    DEBITO = "debito"
    CREDITO = "credito"

class StatusTransacao(Enum):
    PENDENTE = "pendente"
    PROCESSADA = "processada"
    CANCELADA = "cancelada"

class TipoConta(Enum):
    CORRENTE = "corrente"
    POUPANCA = "poupanca"
    INVESTIMENTO = "investimento"

class BandeiraCartao(Enum):
    VISA = "visa"
    MASTERCARD = "mastercard"
    ELO = "elo"
    AMERICAN_EXPRESS = "american_express"
    HIPERCARD = "hipercard"

@dataclass
class ContaCorrente:
    id: str
    nome: str
    banco: str
    agencia: str
    conta: str
    tipo: TipoConta
    saldo_inicial: float
    saldo_atual: float
    compartilhado_com_alzi: bool = False
    ativa: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'nome': self.nome,
            'banco': self.banco,
            'agencia': self.agencia,
            'conta': self.conta,
            'tipo': self.tipo.value if isinstance(self.tipo, TipoConta) else self.tipo,
            'saldo_inicial': self.saldo_inicial,
            'saldo_atual': self.saldo_atual,
            'compartilhado_com_alzi': self.compartilhado_com_alzi,
            'ativa': self.ativa,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContaCorrente':
        return cls(
            id=data['id'],
            nome=data['nome'],
            banco=data['banco'],
            agencia=data['agencia'],
            conta=data['conta'],
            tipo=TipoConta(data['tipo']) if isinstance(data['tipo'], str) else data['tipo'],
            saldo_inicial=data['saldo_inicial'],
            saldo_atual=data['saldo_atual'],
            compartilhado_com_alzi=data.get('compartilhado_com_alzi', False),
            ativa=data.get('ativa', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass
class CartaoCredito:
    id: str
    nome: str
    banco: str
    bandeira: BandeiraCartao
    limite: float
    limite_disponivel: float
    conta_vinculada_id: Optional[str]
    dia_vencimento: int
    dia_fechamento: int
    compartilhado_com_alzi: bool = False
    ativo: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'nome': self.nome,
            'banco': self.banco,
            'bandeira': self.bandeira.value if isinstance(self.bandeira, BandeiraCartao) else self.bandeira,
            'limite': self.limite,
            'limite_disponivel': self.limite_disponivel,
            'conta_vinculada_id': self.conta_vinculada_id,
            'dia_vencimento': self.dia_vencimento,
            'dia_fechamento': self.dia_fechamento,
            'compartilhado_com_alzi': self.compartilhado_com_alzi,
            'ativo': self.ativo,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CartaoCredito':
        return cls(
            id=data['id'],
            nome=data['nome'],
            banco=data['banco'],
            bandeira=BandeiraCartao(data['bandeira']) if isinstance(data['bandeira'], str) else data['bandeira'],
            limite=data['limite'],
            limite_disponivel=data['limite_disponivel'],
            conta_vinculada_id=data.get('conta_vinculada_id'),
            dia_vencimento=data['dia_vencimento'],
            dia_fechamento=data['dia_fechamento'],
            compartilhado_com_alzi=data.get('compartilhado_com_alzi', False),
            ativo=data.get('ativo', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass
class Parcelamento:
    numero_parcela: int
    total_parcelas: int
    valor_parcela: float
    data_vencimento: str
    pago: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'numero_parcela': self.numero_parcela,
            'total_parcelas': self.total_parcelas,
            'valor_parcela': self.valor_parcela,
            'data_vencimento': self.data_vencimento,
            'pago': self.pago
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Parcelamento':
        return cls(
            numero_parcela=data['numero_parcela'],
            total_parcelas=data['total_parcelas'],
            valor_parcela=data['valor_parcela'],
            data_vencimento=data['data_vencimento'],
            pago=data.get('pago', False)
        )

@dataclass
class Transacao:
    id: str
    descricao: str
    valor: float
    tipo: TipoTransacao
    data_transacao: str
    categoria: Optional[str]
    conta_id: Optional[str] = None
    cartao_id: Optional[str] = None
    parcelamento: Optional[List[Parcelamento]] = None
    observacoes: Optional[str] = None
    status: StatusTransacao = StatusTransacao.PROCESSADA
    compartilhado_com_alzi: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if self.parcelamento is None:
            self.parcelamento = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': self.valor,
            'tipo': self.tipo.value if isinstance(self.tipo, TipoTransacao) else self.tipo,
            'data_transacao': self.data_transacao,
            'categoria': self.categoria,
            'conta_id': self.conta_id,
            'cartao_id': self.cartao_id,
            'parcelamento': [p.to_dict() if hasattr(p, 'to_dict') else p for p in self.parcelamento],
            'observacoes': self.observacoes,
            'status': self.status.value if isinstance(self.status, StatusTransacao) else self.status,
            'compartilhado_com_alzi': self.compartilhado_com_alzi,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transacao':
        parcelamento = []
        if data.get('parcelamento'):
            parcelamento = [
                Parcelamento.from_dict(p) if isinstance(p, dict) else p 
                for p in data['parcelamento']
            ]
        
        return cls(
            id=data['id'],
            descricao=data['descricao'],
            valor=data['valor'],
            tipo=TipoTransacao(data['tipo']) if isinstance(data['tipo'], str) else data['tipo'],
            data_transacao=data['data_transacao'],
            categoria=data.get('categoria'),
            conta_id=data.get('conta_id'),
            cartao_id=data.get('cartao_id'),
            parcelamento=parcelamento,
            observacoes=data.get('observacoes'),
            status=StatusTransacao(data.get('status', 'processada')) if isinstance(data.get('status'), str) else data.get('status', StatusTransacao.PROCESSADA),
            compartilhado_com_alzi=data.get('compartilhado_com_alzi', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    @property
    def eh_parcelada(self) -> bool:
        return len(self.parcelamento) > 1

    @property
    def valor_total_parcelado(self) -> float:
        if not self.parcelamento:
            return self.valor
        return sum(p.valor_parcela for p in self.parcelamento)

    @property
    def parcelas_pagas(self) -> int:
        return sum(1 for p in self.parcelamento if p.pago)

    @property
    def parcelas_pendentes(self) -> int:
        return len(self.parcelamento) - self.parcelas_pagas

@dataclass
class ResumoFinanceiro:
    total_contas: int
    total_cartoes: int
    total_transacoes: int
    saldo_total_contas: float
    limite_total_cartoes: float
    limite_disponivel_cartoes: float
    valor_total_gastos_mes: float
    valor_compartilhado_alzi_mes: float
    contas_compartilhadas: int
    cartoes_compartilhados: int
    transacoes_compartilhadas_mes: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_contas': self.total_contas,
            'total_cartoes': self.total_cartoes,
            'total_transacoes': self.total_transacoes,
            'saldo_total_contas': self.saldo_total_contas,
            'limite_total_cartoes': self.limite_total_cartoes,
            'limite_disponivel_cartoes': self.limite_disponivel_cartoes,
            'valor_total_gastos_mes': self.valor_total_gastos_mes,
            'valor_compartilhado_alzi_mes': self.valor_compartilhado_alzi_mes,
            'contas_compartilhadas': self.contas_compartilhadas,
            'cartoes_compartilhados': self.cartoes_compartilhados,
            'transacoes_compartilhadas_mes': self.transacoes_compartilhadas_mes
        }