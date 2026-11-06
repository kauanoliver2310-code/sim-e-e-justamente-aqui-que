"""Agendamento com tratamento de falha, idempotência e escalonamento humano."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Protocol


class StatusAgendamento(str, Enum):
    SOLICITADO = "SOLICITADO"
    CONFIRMADO = "CONFIRMADO"
    FALHA = "FALHA"
    ESCALADO_HUMANO = "ESCALADO_HUMANO"


class ProvedorAgenda(Protocol):
    def horario_livre(self, inicio: datetime, fim: datetime) -> bool: ...
    def criar_evento(self, inicio: datetime, fim: datetime, titulo: str) -> str: ...


@dataclass
class Agendamento:
    cnpj: str
    inicio: datetime
    fim: datetime
    status: StatusAgendamento = StatusAgendamento.SOLICITADO
    evento_id: str | None = None
    tentativas: int = 0
    erros: list[str] = field(default_factory=list)


class ServicoAgenda:
    def __init__(self, provedor: ProvedorAgenda, max_tentativas: int = 3):
        self.provedor = provedor
        self.max_tentativas = max_tentativas
        self._por_cnpj: dict[str, Agendamento] = {}

    def agendar(self, cnpj: str, inicio: datetime, fim: datetime, titulo: str) -> Agendamento:
        if fim <= inicio:
            raise ValueError("Fim deve ser depois do início")
        ag = self._por_cnpj.get(cnpj)
        if ag and ag.status == StatusAgendamento.CONFIRMADO:
            return ag  # idempotente: não cria evento duplicado
        if ag is None or (ag.inicio, ag.fim) != (inicio, fim):
            ag = Agendamento(cnpj, inicio, fim)
            self._por_cnpj[cnpj] = ag
        ag.tentativas += 1
        try:
            if not self.provedor.horario_livre(inicio, fim):
                ag.status = StatusAgendamento.FALHA
                ag.erros.append("horario_ocupado")
            else:
                ag.evento_id = self.provedor.criar_evento(inicio, fim, titulo)
                ag.status = StatusAgendamento.CONFIRMADO
                return ag
        except Exception as e:  # noqa: BLE001
            ag.status = StatusAgendamento.FALHA
            ag.erros.append(f"erro_provedor: {e}")
        if ag.tentativas >= self.max_tentativas:
            ag.status = StatusAgendamento.ESCALADO_HUMANO
        return ag
