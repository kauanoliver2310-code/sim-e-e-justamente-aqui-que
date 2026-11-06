"""Validação da saída da IA (classificação de lead / intenção de resposta).

A IA devolve JSON. Este módulo garante que só uma saída estruturalmente
válida e coerente seja usada; qualquer outra coisa vira FALHA_CLASSIFICACAO
e vai para revisão humana — nunca é interpretada "no chute".
"""

from __future__ import annotations

import json
from dataclasses import dataclass

INTENCOES = {"INTERESSADO", "QUER_AGENDAR", "DUVIDA", "SEM_INTERESSE", "OPOSICAO", "INDEFINIDO"}
ICP = {"DENTRO", "FORA", "INCERTO"}


@dataclass
class SaidaClassificacao:
    valida: bool
    intencao: str | None = None
    icp: str | None = None
    confianca: float | None = None
    justificativa: str = ""
    erro: str = ""

    @property
    def status(self) -> str:
        if not self.valida:
            return "FALHA_CLASSIFICACAO"
        if self.intencao == "OPOSICAO":
            return "REGISTRAR_OPOSICAO"       # obrigatório processar descadastro
        if self.confianca is not None and self.confianca < 0.7:
            return "REVISAO_HUMANA"
        return "OK"


def validar_saida(texto: str) -> SaidaClassificacao:
    try:
        dados = json.loads(texto)
    except (json.JSONDecodeError, TypeError) as e:
        return SaidaClassificacao(False, erro=f"JSON inválido: {e}")
    if not isinstance(dados, dict):
        return SaidaClassificacao(False, erro="Saída não é objeto JSON")
    intencao = dados.get("intencao")
    icp = dados.get("icp")
    conf = dados.get("confianca")
    just = dados.get("justificativa", "")
    if intencao not in INTENCOES:
        return SaidaClassificacao(False, erro=f"intencao fora do domínio: {intencao!r}")
    if icp not in ICP:
        return SaidaClassificacao(False, erro=f"icp fora do domínio: {icp!r}")
    if isinstance(conf, bool) or not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        return SaidaClassificacao(False, erro=f"confianca inválida: {conf!r}")
    if not isinstance(just, str) or not just.strip():
        return SaidaClassificacao(False, erro="justificativa ausente")
    return SaidaClassificacao(True, intencao, icp, float(conf), just.strip())
