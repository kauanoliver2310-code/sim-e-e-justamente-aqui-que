#!/usr/bin/env python3
"""Gera relatorios/simulacao_custos.md e .csv a partir de config/premissas.json.

Uso:  python3 scripts/simular_custos.py [caminho_premissas]
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from kauan_ai.custos import calcular, carregar_premissas, simular  # noqa: E402


def brl(v: float) -> str:
    if math.isinf(v):
        return "—"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def reproduzir_calculo_chatgpt() -> list[tuple[int, float, float, float]]:
    """Reproduz a tabela da auditoria do ChatGPT com as premissas dele:
    US$0,10/0,60 por MTok, 2.000/500 tokens, R$5,50, R$0,3217/msg, 1 msg por lead,
    R$30 hospedagem, e-mail grátis. Serve para conferir a aritmética dele."""
    p = {
        "cambio_brl_usd": 5.50, "infra_mensal_brl": 30.0, "dominio_mensal_brl": 0.0,
        "llm_preco_entrada_usd_mtok": 0.10, "llm_preco_saida_usd_mtok": 0.60,
        "llm_usa_batch": False, "llm_tokens_entrada_por_lead": 2000,
        "llm_tokens_saida_por_lead": 500, "custo_enriquecimento_por_lead_brl": 0.0,
        "taxa_qualificacao": 1.0, "fracao_qualificados_whatsapp": 1.0,
        "mensagens_whatsapp_por_lead": 1, "preco_whatsapp_marketing_brl": 0.3217,
        "emails_por_lead_qualificado": 0, "email_gratis_mes": 3000, "email_gratis_dia": 100,
        "email_plano_pago_usd": 20.0, "email_plano_pago_limite_mes": 50000,
        "taxa_resposta": 0.05, "taxa_reuniao_sobre_resposta": 0.4,
        "horas_manutencao_mes": 0, "valor_hora_brl": 0.0,
        "llm_chamadas_por_lead": 1, "mensagens_servico_por_lead": 0,
        "franquia_servico_mes": 1000, "preco_whatsapp_servico_brl": 0.035,
    }
    out = []
    for v in (100, 500, 1000, 3000, 5000):
        r = calcular(v, p, "chatgpt")
        out.append((v, r.custo_ia_brl, r.custo_whatsapp_brl, r.total_caixa_brl))
    return out


def main() -> None:
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "config" / "premissas.json"
    dados = carregar_premissas(caminho)
    resultados = simular(dados)
    pasta = RAIZ / "relatorios"
    pasta.mkdir(exist_ok=True)

    with open(pasta / "simulacao_custos.csv", "w", newline="", encoding="utf-8") as f:
        campos = [k for k in resultados[0].como_dict() if k != "alertas"] + ["alertas"]
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in resultados:
            d = r.como_dict()
            d["alertas"] = " | ".join(d["alertas"])
            w.writerow(d)

    linhas = [
        "# Simulação de custos — gerada por código",
        "",
        f"Premissas: `{caminho.relative_to(RAIZ) if caminho.is_relative_to(RAIZ) else caminho}` "
        f"(data de referência {dados.get('data_referencia')}). "
        f"Orçamento de caixa: {brl(dados['orcamento_mensal_brl'])}/mês.",
        "",
        "> ESTIMATIVA, não cotação. Ver status de cada premissa no JSON. "
        "'Caixa' = dinheiro que sai; 'Econômico' = caixa + horas de manutenção.",
        "",
    ]
    for cen in dados["cenarios"]:
        linhas += [f"## Cenário {cen}", "",
                   "| Leads/mês | IA | E-mail | WhatsApp | Fixo | **Caixa** | Econômico | Reuniões | R$/lead | R$/reunião | ≤ orçamento |",
                   "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|"]
        alertas = []
        for r in (x for x in resultados if x.cenario == cen):
            linhas.append(
                f"| {r.leads} | {brl(r.custo_ia_brl)} | {brl(r.custo_email_brl)} | "
                f"{brl(r.custo_whatsapp_brl)} | {brl(r.custo_fixo_brl)} | **{brl(r.total_caixa_brl)}** | "
                f"{brl(r.total_economico_brl)} | {r.reunioes:.1f} | {brl(r.custo_por_lead_brl)} | "
                f"{brl(r.custo_por_reuniao_brl)} | {'sim' if r.cabe_no_orcamento else 'NÃO'} |"
            )
            for a in r.alertas:
                alertas.append(f"- {r.leads} leads: {a}")
        if alertas:
            linhas += ["", "Alertas:", *alertas]
        linhas.append("")

    linhas += ["## Conferência da tabela do ChatGPT (mesmas premissas dele)", "",
               "| Leads | IA | WhatsApp | Total |", "|---:|---:|---:|---:|"]
    for v, ia, wa, tot in reproduzir_calculo_chatgpt():
        linhas.append(f"| {v} | {brl(ia)} | {brl(wa)} | {brl(tot)} |")
    linhas += ["", "Resultado: 4 de 5 linhas conferem. **A linha de 5.000 leads do ChatGPT está "
               "errada**: ele publicou R$ 1.762,25; o correto é 30 + 13,75 + 1.608,50 = "
               "R$ 1.652,25 (erro de soma de R$ 110). Fora isso, o problema não é a conta, "
               "são as premissas: WhatsApp de marketing para 100% dos leads, hospedagem de R$ 30 "
               "não cotada, preço do WhatsApp não confirmado no rate card oficial, nenhum custo "
               "de manutenção e nenhum custo por reunião.", ""]

    (pasta / "simulacao_custos.md").write_text("\n".join(linhas), encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
