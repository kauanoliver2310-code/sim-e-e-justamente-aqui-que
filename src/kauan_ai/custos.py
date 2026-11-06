"""Modelo de custos reproduzível do sistema de prospecção.

Fórmulas (L = leads processados no mês):
  qualificados      = L × taxa_qualificacao
  custo_ia_usd      = L × (tok_in × preço_in + tok_out × preço_out) / 1e6  × (0,5 se batch)
  custo_ia_brl      = custo_ia_usd × câmbio
  emails            = qualificados × emails_por_lead
  custo_email_brl   = 0 se emails ≤ grátis_mês E emails/dias_úteis ≤ grátis_dia
                      senão plano_pago_usd × câmbio
  msgs_whatsapp     = qualificados × fração_whatsapp × msgs_por_lead
  custo_whatsapp    = msgs_whatsapp × preço_msg_marketing
  custo_enriq       = L × custo_enriquecimento_por_lead
  fixo              = infra + domínio
  total_caixa       = fixo + ia + email + whatsapp + enriquecimento
  manutencao        = horas × valor_hora        (custo de tempo, não sai do caixa)
  total_economico   = total_caixa + manutencao
  reunioes          = qualificados × taxa_resposta × taxa_reunião
  custo_por_lead    = total_caixa / L
  custo_por_reuniao = total_caixa / reunioes
Todos os valores são ESTIMATIVAS a partir de premissas (config/premissas.json).
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path

CAMPOS_TAXA = (
    "taxa_qualificacao", "fracao_qualificados_whatsapp",
    "taxa_resposta", "taxa_reuniao_sobre_resposta",
)
CAMPOS_OBRIGATORIOS = (
    "cambio_brl_usd", "infra_mensal_brl", "dominio_mensal_brl",
    "llm_preco_entrada_usd_mtok", "llm_preco_saida_usd_mtok", "llm_usa_batch",
    "llm_tokens_entrada_por_lead", "llm_tokens_saida_por_lead",
    "custo_enriquecimento_por_lead_brl", "taxa_qualificacao",
    "fracao_qualificados_whatsapp", "mensagens_whatsapp_por_lead",
    "preco_whatsapp_marketing_brl", "emails_por_lead_qualificado",
    "email_gratis_mes", "email_gratis_dia", "email_plano_pago_usd",
    "email_plano_pago_limite_mes", "taxa_resposta", "taxa_reuniao_sobre_resposta",
    "horas_manutencao_mes", "valor_hora_brl",
)


class PremissaInvalida(ValueError):
    pass


@dataclass
class ResultadoCusto:
    cenario: str
    leads: int
    qualificados: float
    custo_ia_brl: float
    emails: float
    custo_email_brl: float
    msgs_whatsapp: float
    custo_whatsapp_brl: float
    custo_enriquecimento_brl: float
    custo_fixo_brl: float
    total_caixa_brl: float
    manutencao_brl: float
    total_economico_brl: float
    reunioes: float
    custo_por_lead_brl: float
    custo_por_reuniao_brl: float
    cabe_no_orcamento: bool
    alertas: list[str] = field(default_factory=list)

    def como_dict(self) -> dict:
        return asdict(self)


def validar_premissas(p: dict, nome: str = "") -> None:
    faltando = [c for c in CAMPOS_OBRIGATORIOS if c not in p]
    if faltando:
        raise PremissaInvalida(f"[{nome}] premissas ausentes: {faltando}")
    for c in CAMPOS_OBRIGATORIOS:
        v = p[c]
        if c == "llm_usa_batch":
            if not isinstance(v, bool):
                raise PremissaInvalida(f"[{nome}] {c} deve ser true/false")
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)) or math.isnan(v):
            raise PremissaInvalida(f"[{nome}] {c} deve ser número, recebido {v!r}")
        if v < 0:
            raise PremissaInvalida(f"[{nome}] {c} não pode ser negativo ({v})")
    for c in CAMPOS_TAXA:
        if not 0 <= p[c] <= 1:
            raise PremissaInvalida(f"[{nome}] {c} deve estar entre 0 e 1 ({p[c]})")
    if p["cambio_brl_usd"] == 0:
        raise PremissaInvalida(f"[{nome}] câmbio não pode ser zero")
    if p["email_gratis_dia"] == 0 and p["email_gratis_mes"] > 0:
        raise PremissaInvalida(f"[{nome}] limite diário grátis zero com mensal positivo")


def calcular(leads: int, p: dict, cenario: str = "", orcamento_brl: float | None = None,
             dias_uteis: int = 22) -> ResultadoCusto:
    if isinstance(leads, bool) or not isinstance(leads, int) or leads <= 0:
        raise PremissaInvalida(f"Volume de leads deve ser inteiro positivo, recebido {leads!r}")
    if dias_uteis <= 0:
        raise PremissaInvalida("dias_uteis deve ser positivo")
    validar_premissas(p, cenario)
    alertas: list[str] = []

    qualificados = leads * p["taxa_qualificacao"]

    ia_usd = leads * (
        p["llm_tokens_entrada_por_lead"] * p["llm_preco_entrada_usd_mtok"]
        + p["llm_tokens_saida_por_lead"] * p["llm_preco_saida_usd_mtok"]
    ) / 1_000_000
    if p["llm_usa_batch"]:
        ia_usd *= 0.5
    ia_brl = ia_usd * p["cambio_brl_usd"]

    emails = qualificados * p["emails_por_lead_qualificado"]
    emails_dia = emails / dias_uteis
    if emails <= p["email_gratis_mes"] and emails_dia <= p["email_gratis_dia"]:
        email_brl = 0.0
    else:
        email_brl = p["email_plano_pago_usd"] * p["cambio_brl_usd"]
        motivo = "mensal" if emails > p["email_gratis_mes"] else "diário"
        alertas.append(f"E-mail excede faixa grátis ({motivo}): plano pago necessário")
        if emails > p["email_plano_pago_limite_mes"]:
            alertas.append("E-mail excede também o plano pago de entrada: recotar")

    msgs_wa = qualificados * p["fracao_qualificados_whatsapp"] * p["mensagens_whatsapp_por_lead"]
    wa_brl = msgs_wa * p["preco_whatsapp_marketing_brl"]

    enriq_brl = leads * p["custo_enriquecimento_por_lead_brl"]
    fixo = p["infra_mensal_brl"] + p["dominio_mensal_brl"]
    total = fixo + ia_brl + email_brl + wa_brl + enriq_brl
    manut = p["horas_manutencao_mes"] * p["valor_hora_brl"]

    reunioes = qualificados * p["taxa_resposta"] * p["taxa_reuniao_sobre_resposta"]
    por_reuniao = total / reunioes if reunioes > 0 else math.inf
    if reunioes < 1:
        alertas.append("Menos de 1 reunião esperada no mês: volume baixo demais para medir")

    cabe = orcamento_brl is None or total <= orcamento_brl
    if not cabe:
        alertas.append(f"Custo de caixa R$ {total:.2f} acima do orçamento R$ {orcamento_brl:.2f}")
    if total > 0 and wa_brl / total > 0.5:
        alertas.append("WhatsApp marketing é mais da metade do custo")

    return ResultadoCusto(
        cenario=cenario, leads=leads, qualificados=qualificados,
        custo_ia_brl=ia_brl, emails=emails, custo_email_brl=email_brl,
        msgs_whatsapp=msgs_wa, custo_whatsapp_brl=wa_brl,
        custo_enriquecimento_brl=enriq_brl, custo_fixo_brl=fixo,
        total_caixa_brl=total, manutencao_brl=manut, total_economico_brl=total + manut,
        reunioes=reunioes, custo_por_lead_brl=total / leads,
        custo_por_reuniao_brl=por_reuniao, cabe_no_orcamento=cabe, alertas=alertas,
    )


def ponto_de_equilibrio(r: ResultadoCusto, comissao_por_venda_brl: float,
                        taxa_fechamento_reuniao: float) -> dict:
    """Quanto a operação precisa vender para pagar o custo de caixa.

    A comissão do programa de indicação NÃO é inventada aqui: o Kauan
    informa o valor real do regulamento do parceiro.
    """
    if comissao_por_venda_brl <= 0:
        raise PremissaInvalida("Comissão por venda deve ser positiva")
    if not 0 < taxa_fechamento_reuniao <= 1:
        raise PremissaInvalida("Taxa de fechamento deve estar em (0, 1]")
    vendas_esperadas = r.reunioes * taxa_fechamento_reuniao
    receita = vendas_esperadas * comissao_por_venda_brl
    vendas_necessarias = math.ceil(r.total_caixa_brl / comissao_por_venda_brl)
    return {
        "vendas_esperadas": vendas_esperadas,
        "receita_esperada_brl": receita,
        "lucro_caixa_brl": receita - r.total_caixa_brl,
        "vendas_para_empatar": vendas_necessarias,
    }


def carregar_premissas(caminho: str | Path) -> dict:
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    if "cenarios" not in dados or not dados["cenarios"]:
        raise PremissaInvalida("Arquivo sem cenários")
    for nome, p in dados["cenarios"].items():
        validar_premissas(p, nome)
    return dados


def simular(dados: dict) -> list[ResultadoCusto]:
    orc = dados.get("orcamento_mensal_brl")
    dias = dados.get("dias_uteis_mes", 22)
    out = []
    for nome, p in dados["cenarios"].items():
        for v in dados["volumes_leads_mes"]:
            out.append(calcular(v, p, nome, orc, dias))
    return out
