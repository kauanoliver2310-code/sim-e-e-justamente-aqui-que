"""Cadastro de leads com deduplicação, registro de base legal (LGPD),
oposição/descadastramento e retenção.

Implementação em memória para teste das regras. Em produção o mesmo
contrato é persistido no PostgreSQL (ver docs/03-arquitetura.md, tabelas
`leads`, `supressao`, `eventos_lgpd`).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum

from . import cnpj as cnpj_mod


class OrigemLead(str, Enum):
    INBOUND_WHATSAPP = "INBOUND_WHATSAPP"   # o lead chamou (vídeo -> WhatsApp)
    INBOUND_FORMULARIO = "INBOUND_FORMULARIO"
    DADOS_ABERTOS_CNPJ = "DADOS_ABERTOS_CNPJ"
    INDICACAO = "INDICACAO"
    MANUAL = "MANUAL"


class BaseLegal(str, Enum):
    CONSENTIMENTO = "CONSENTIMENTO"
    LEGITIMO_INTERESSE = "LEGITIMO_INTERESSE"   # exige LIA registrada
    PROCEDIMENTOS_PRELIMINARES = "PROCEDIMENTOS_PRELIMINARES"  # titular pediu proposta


class LeadDuplicado(Exception):
    pass


class LeadSuprimido(Exception):
    """Titular pediu oposição/descadastro: não pode ser recadastrado para contato."""


class BaseLegalAusente(ValueError):
    pass


def _hash_contato(valor: str) -> str:
    """Guardamos hash do contato na lista de supressão (minimização)."""
    v = re.sub(r"\s", "", valor).lower()
    if "@" not in v:
        v = re.sub(r"\D", "", v)
    return hashlib.sha256(v.encode()).hexdigest()


@dataclass
class Lead:
    cnpj: str
    razao_social: str
    origem: OrigemLead
    base_legal: BaseLegal
    criado_em: datetime
    telefone: str | None = None
    email: str | None = None
    cnae: str | None = None
    municipio: str | None = None
    uf: str | None = None
    lia_referencia: str | None = None     # id do teste de legítimo interesse
    ultima_interacao: datetime | None = None
    historico: list[dict] = field(default_factory=list)


class CadastroLeads:
    def __init__(self, retencao_sem_interacao: timedelta = timedelta(days=180)):
        self._leads: dict[str, Lead] = {}
        self._supressao: dict[str, dict] = {}   # hash -> registro
        self.eventos_lgpd: list[dict] = []
        self.retencao = retencao_sem_interacao

    # ---------- cadastro ----------
    def adicionar(self, lead: Lead, atualizar_se_existir: bool = False) -> Lead:
        lead.cnpj = cnpj_mod.validar(lead.cnpj)
        if lead.base_legal == BaseLegal.LEGITIMO_INTERESSE and not lead.lia_referencia:
            raise BaseLegalAusente(
                "Legítimo interesse exige referência ao teste de balanceamento (LIA)"
            )
        if self.esta_suprimido(cnpj=lead.cnpj, telefone=lead.telefone, email=lead.email):
            raise LeadSuprimido(f"{lead.cnpj} está na lista de oposição/descadastro")
        existente = self._leads.get(lead.cnpj)
        if existente:
            if not atualizar_se_existir:
                raise LeadDuplicado(lead.cnpj)
            for campo in ("telefone", "email", "cnae", "municipio", "uf"):
                novo = getattr(lead, campo)
                if novo:
                    setattr(existente, campo, novo)
            existente.historico.append({"evento": "ATUALIZADO", "em": lead.criado_em.isoformat()})
            return existente
        lead.historico.append({"evento": "CRIADO", "em": lead.criado_em.isoformat(),
                               "origem": lead.origem.value, "base_legal": lead.base_legal.value})
        self._leads[lead.cnpj] = lead
        return lead

    def obter(self, cnpj: str) -> Lead | None:
        return self._leads.get(cnpj_mod.validar(cnpj))

    def __len__(self) -> int:
        return len(self._leads)

    # ---------- LGPD: oposição / descadastro ----------
    def registrar_oposicao(self, cnpj: str | None = None, telefone: str | None = None,
                           email: str | None = None, canal: str = "", em: datetime | None = None,
                           motivo: str = "oposicao") -> None:
        em = em or datetime.now(timezone.utc)
        chaves = []
        if cnpj:
            chaves.append(("cnpj", cnpj_mod.validar(cnpj)))
        if telefone:
            chaves.append(("telefone", _hash_contato(telefone)))
        if email:
            chaves.append(("email", _hash_contato(email)))
        if not chaves:
            raise ValueError("Informe ao menos um identificador para oposição")
        for tipo, valor in chaves:
            self._supressao[f"{tipo}:{valor}"] = {"em": em.isoformat(), "canal": canal, "motivo": motivo}
        self.eventos_lgpd.append({"evento": "OPOSICAO", "em": em.isoformat(), "canal": canal,
                                  "identificadores": [t for t, _ in chaves], "motivo": motivo})
        # elimina dados de contato do lead (mantém só o necessário para supressão)
        if cnpj:
            lead = self._leads.pop(cnpj_mod.validar(cnpj), None)
            if lead:
                self.eventos_lgpd.append({"evento": "DADOS_ELIMINADOS", "em": em.isoformat(),
                                          "cnpj": lead.cnpj})

    def esta_suprimido(self, cnpj: str | None = None, telefone: str | None = None,
                       email: str | None = None) -> bool:
        if cnpj and f"cnpj:{cnpj_mod.normalizar(cnpj)}" in self._supressao:
            return True
        if telefone and f"telefone:{_hash_contato(telefone)}" in self._supressao:
            return True
        if email and f"email:{_hash_contato(email)}" in self._supressao:
            return True
        return False

    # ---------- retenção ----------
    def aplicar_retencao(self, agora: datetime | None = None) -> list[str]:
        agora = agora or datetime.now(timezone.utc)
        removidos = []
        for c, lead in list(self._leads.items()):
            referencia = lead.ultima_interacao or lead.criado_em
            if agora - referencia > self.retencao:
                del self._leads[c]
                removidos.append(c)
                self.eventos_lgpd.append({"evento": "DESCARTE_RETENCAO", "em": agora.isoformat(),
                                          "cnpj": c})
        return removidos
