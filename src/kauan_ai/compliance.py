"""Motor de decisão de compliance — determinístico, auditável, sem IA.

Princípios (corrigem o SOP original):
1. Fonte indisponível, com erro ou desatualizada  -> PENDENTE. Nunca aprovação automática.
2. Coincidência só de NOME nunca gera restrição    -> REVISAO_HUMANA, confiança BAIXA.
3. Restrição com CNPJ exato                         -> RESTRICAO_A_CONFIRMAR (humano decide).
   O sistema não "reprova" sozinho: ele apresenta evidência e um humano confirma.
4. Toda conclusão carrega evidências: fonte, data da consulta, data da base e referência.
5. Situação cadastral != ATIVA na Receita           -> INAPTO_CADASTRAL (regra objetiva).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum


class StatusFonte(str, Enum):
    NADA_CONSTA = "NADA_CONSTA"
    CONSTA = "CONSTA"
    INDISPONIVEL = "INDISPONIVEL"
    ERRO = "ERRO"


class TipoCorrespondencia(str, Enum):
    CNPJ_EXATO = "CNPJ_EXATO"
    RAIZ_CNPJ = "RAIZ_CNPJ"           # mesma empresa, outro estabelecimento
    NOME_APROXIMADO = "NOME_APROXIMADO"
    NENHUMA = "NENHUMA"


class Parecer(str, Enum):
    APTO = "APTO"
    PENDENTE = "PENDENTE"
    REVISAO_HUMANA = "REVISAO_HUMANA"
    RESTRICAO_A_CONFIRMAR = "RESTRICAO_A_CONFIRMAR"
    INAPTO_CADASTRAL = "INAPTO_CADASTRAL"


class Confianca(str, Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"


# Idade máxima aceitável da BASE consultada (não da consulta).
# MTE publica a Lista Suja semestralmente (abr/out) -> ~6 meses + folga.
# IBAMA informa atualização diária no portal -> 7 dias de tolerância.
# Receita/BrasilAPI: espelho de dados abertos mensais -> 45 dias.
IDADE_MAXIMA_BASE = {
    "RECEITA": timedelta(days=45),
    "IBAMA_EMBARGOS": timedelta(days=7),
    "MTE_LISTA_SUJA": timedelta(days=200),
    "JUDICIAL_FALENCIA_RJ": timedelta(days=30),
}

FONTES_OBRIGATORIAS_PADRAO = ("RECEITA", "IBAMA_EMBARGOS", "MTE_LISTA_SUJA")


@dataclass(frozen=True)
class ResultadoFonte:
    fonte: str
    status: StatusFonte
    consultado_em: datetime
    data_base: datetime | None = None          # data de atualização da base consultada
    correspondencia: TipoCorrespondencia = TipoCorrespondencia.NENHUMA
    referencia: str = ""                       # URL, nº do auto, id do registro, etc.
    detalhe: str = ""
    situacao_cadastral: str | None = None      # só para RECEITA (ATIVA, BAIXADA, INAPTA...)


@dataclass
class ResultadoCompliance:
    cnpj: str
    parecer: Parecer
    confianca: Confianca
    motivos: list[str] = field(default_factory=list)
    evidencias: list[dict] = field(default_factory=list)
    fontes_pendentes: list[str] = field(default_factory=list)
    requer_revisao_humana: bool = False
    avaliado_em: datetime | None = None


def _evidencia(r: ResultadoFonte) -> dict:
    return {
        "fonte": r.fonte,
        "status": r.status.value,
        "consultado_em": r.consultado_em.isoformat(),
        "data_base": r.data_base.isoformat() if r.data_base else None,
        "correspondencia": r.correspondencia.value,
        "referencia": r.referencia,
        "detalhe": r.detalhe,
    }


def avaliar(
    cnpj: str,
    resultados: list[ResultadoFonte],
    agora: datetime | None = None,
    fontes_obrigatorias: tuple[str, ...] = FONTES_OBRIGATORIAS_PADRAO,
) -> ResultadoCompliance:
    agora = agora or datetime.now(timezone.utc)
    por_fonte = {r.fonte: r for r in resultados}
    res = ResultadoCompliance(
        cnpj=cnpj,
        parecer=Parecer.APTO,
        confianca=Confianca.ALTA,
        evidencias=[_evidencia(r) for r in resultados],
        avaliado_em=agora,
    )

    # 1. Fontes ausentes, indisponíveis, com erro ou desatualizadas -> pendentes
    for fonte in fontes_obrigatorias:
        r = por_fonte.get(fonte)
        if r is None:
            res.fontes_pendentes.append(fonte)
            res.motivos.append(f"PENDENTE: {fonte} não consultada")
            continue
        if r.status in (StatusFonte.INDISPONIVEL, StatusFonte.ERRO):
            res.fontes_pendentes.append(fonte)
            res.motivos.append(f"PENDENTE: {fonte} {r.status.value}")
            continue
        limite = IDADE_MAXIMA_BASE.get(fonte)
        if limite is not None:
            if r.data_base is None:
                res.fontes_pendentes.append(fonte)
                res.motivos.append(f"PENDENTE: {fonte} sem data de atualização da base")
            elif agora - r.data_base > limite:
                res.fontes_pendentes.append(fonte)
                res.motivos.append(
                    f"PENDENTE: base {fonte} desatualizada ({r.data_base.date()})"
                )

    # 2. Situação cadastral (regra objetiva, só se a consulta da Receita é válida)
    receita = por_fonte.get("RECEITA")
    if receita and "RECEITA" not in res.fontes_pendentes:
        situacao = (receita.situacao_cadastral or "").upper()
        if situacao and situacao != "ATIVA":
            res.parecer = Parecer.INAPTO_CADASTRAL
            res.confianca = Confianca.ALTA
            res.motivos.append(f"Situação cadastral na Receita: {situacao}")
            return res
        if not situacao:
            res.fontes_pendentes.append("RECEITA")
            res.motivos.append("PENDENTE: RECEITA sem situação cadastral no retorno")

    # 3. Ocorrências encontradas
    restricao_exata = False
    so_nome = False
    for r in resultados:
        if r.status != StatusFonte.CONSTA or r.fonte == "RECEITA":
            continue
        if r.correspondencia in (TipoCorrespondencia.CNPJ_EXATO, TipoCorrespondencia.RAIZ_CNPJ):
            restricao_exata = True
            res.motivos.append(
                f"{r.fonte}: ocorrência por {r.correspondencia.value} ({r.referencia or 'sem ref.'})"
            )
        else:
            so_nome = True
            res.motivos.append(
                f"{r.fonte}: possível homônimo ({r.correspondencia.value}) — não confirma restrição"
            )

    if restricao_exata:
        res.parecer = Parecer.RESTRICAO_A_CONFIRMAR
        res.confianca = Confianca.ALTA
        res.requer_revisao_humana = True
    elif res.fontes_pendentes:
        res.parecer = Parecer.PENDENTE
        res.confianca = Confianca.BAIXA
    elif so_nome:
        res.parecer = Parecer.REVISAO_HUMANA
        res.confianca = Confianca.BAIXA
        res.requer_revisao_humana = True
    else:
        res.parecer = Parecer.APTO
        res.confianca = Confianca.ALTA
        res.motivos.append("Nada consta em todas as fontes obrigatórias, bases dentro da validade")

    return res


def pode_seguir_para_abordagem(r: ResultadoCompliance) -> bool:
    """Só APTO segue automaticamente para a fila de rascunho de abordagem."""
    return r.parecer == Parecer.APTO
