"""Fila de saída de mensagens (outbox) com idempotência, aprovação humana
e modo simulação obrigatório por padrão.

NENHUM envio real acontece neste módulo. O envio é feito por um
`Enviador` injetado; o padrão é `EnviadorSimulado`. Trocar para envio real
exige decisão explícita do Kauan (ver docs/06-plano-implantacao.md).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol

from .leads import CadastroLeads


class Canal(str, Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"


class StatusMensagem(str, Enum):
    RASCUNHO = "RASCUNHO"
    APROVADA = "APROVADA"
    ENVIADA = "ENVIADA"
    BLOQUEADA = "BLOQUEADA"
    FALHA = "FALHA"


class MensagemDuplicada(Exception):
    pass


@dataclass
class Mensagem:
    chave: str
    cnpj: str
    canal: Canal
    destino: str
    texto: str
    campanha: str
    etapa: str
    status: StatusMensagem = StatusMensagem.RASCUNHO
    aprovada_por: str | None = None
    historico: list[dict] = field(default_factory=list)


class Enviador(Protocol):
    def enviar(self, m: Mensagem) -> str: ...


class EnviadorSimulado:
    """Não envia nada. Registra o que teria sido enviado."""

    def __init__(self) -> None:
        self.enviadas: list[Mensagem] = []

    def enviar(self, m: Mensagem) -> str:
        self.enviadas.append(m)
        return f"simulado-{len(self.enviadas)}"


def chave_idempotencia(cnpj: str, canal: Canal, campanha: str, etapa: str) -> str:
    base = f"{cnpj}|{canal.value}|{campanha}|{etapa}"
    return hashlib.sha256(base.encode()).hexdigest()[:32]


class Outbox:
    def __init__(self, cadastro: CadastroLeads, enviador: Enviador | None = None,
                 limite_diario_email: int | None = 100):
        self.cadastro = cadastro
        self.enviador = enviador or EnviadorSimulado()
        self.limite_diario_email = limite_diario_email
        self._msgs: dict[str, Mensagem] = {}
        self._enviados_por_dia: dict[tuple[str, str], int] = {}

    def criar_rascunho(self, cnpj: str, canal: Canal, destino: str, texto: str,
                       campanha: str, etapa: str) -> Mensagem:
        chave = chave_idempotencia(cnpj, canal, campanha, etapa)
        if chave in self._msgs:
            raise MensagemDuplicada(f"Já existe mensagem {etapa}/{campanha} para {cnpj} via {canal.value}")
        if not texto.strip():
            raise ValueError("Texto vazio")
        m = Mensagem(chave, cnpj, canal, destino, texto, campanha, etapa)
        self._msgs[chave] = m
        return m

    def aprovar(self, chave: str, operador: str) -> Mensagem:
        m = self._msgs[chave]
        if m.status != StatusMensagem.RASCUNHO:
            raise ValueError(f"Só rascunho pode ser aprovado (atual: {m.status.value})")
        m.status = StatusMensagem.APROVADA
        m.aprovada_por = operador
        m.historico.append({"evento": "APROVADA", "por": operador})
        return m

    def enviar(self, chave: str, agora: datetime | None = None) -> Mensagem:
        agora = agora or datetime.now(timezone.utc)
        m = self._msgs[chave]
        if m.status == StatusMensagem.ENVIADA:
            return m  # idempotente: reprocessar não reenviar
        if m.status != StatusMensagem.APROVADA:
            raise PermissionError("Mensagem sem aprovação humana não pode ser enviada")
        kw = {"email": m.destino} if m.canal == Canal.EMAIL else {"telefone": m.destino}
        if self.cadastro.esta_suprimido(cnpj=m.cnpj, **kw):
            m.status = StatusMensagem.BLOQUEADA
            m.historico.append({"evento": "BLOQUEADA_OPOSICAO", "em": agora.isoformat()})
            return m
        dia = agora.date().isoformat()
        if m.canal == Canal.EMAIL and self.limite_diario_email is not None:
            usados = self._enviados_por_dia.get((dia, "EMAIL"), 0)
            if usados >= self.limite_diario_email:
                raise RuntimeError(f"Limite diário de e-mail atingido ({self.limite_diario_email})")
        try:
            ref = self.enviador.enviar(m)
        except Exception as e:  # noqa: BLE001 — registramos qualquer falha do provedor
            m.status = StatusMensagem.FALHA
            m.historico.append({"evento": "FALHA_ENVIO", "erro": str(e), "em": agora.isoformat()})
            return m
        m.status = StatusMensagem.ENVIADA
        m.historico.append({"evento": "ENVIADA", "ref": ref, "em": agora.isoformat()})
        self._enviados_por_dia[(dia, m.canal.value)] = self._enviados_por_dia.get((dia, m.canal.value), 0) + 1
        return m

    def reprocessar_falhas(self, agora: datetime | None = None) -> list[Mensagem]:
        out = []
        for m in self._msgs.values():
            if m.status == StatusMensagem.FALHA:
                m.status = StatusMensagem.APROVADA
                out.append(self.enviar(m.chave, agora))
        return out

    def obter(self, chave: str) -> Mensagem:
        return self._msgs[chave]
