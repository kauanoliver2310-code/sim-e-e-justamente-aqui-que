"""Validação e normalização de CNPJ (numérico e alfanumérico).

Desde julho de 2026 a Receita Federal emite CNPJ alfanumérico
(IN RFB nº 2.229/2024): as 12 primeiras posições aceitam letras A-Z e
dígitos; os 2 dígitos verificadores continuam numéricos. O cálculo do DV
usa o valor (código ASCII - 48) de cada caractere, com os mesmos pesos do
módulo 11. Para dígitos o resultado é idêntico ao algoritmo antigo.

Conferido contra o exemplo publicado pela Receita: 12.ABC.345/01DE-35.
"""

from __future__ import annotations

import re

_PESOS_DV1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_PESOS_DV2 = (6,) + _PESOS_DV1
_FORMATO = re.compile(r"^[0-9A-Z]{12}[0-9]{2}$")


class CNPJInvalido(ValueError):
    """CNPJ com formato ou dígito verificador inválido."""


def normalizar(cnpj: str) -> str:
    """Remove pontuação e espaços e coloca letras em maiúsculo."""
    if not isinstance(cnpj, str):
        raise CNPJInvalido(f"CNPJ deve ser texto, recebido {type(cnpj).__name__}")
    return re.sub(r"[.\-/\s]", "", cnpj).upper()


def _dv(valores: list[int], pesos: tuple[int, ...]) -> int:
    resto = sum(v * p for v, p in zip(valores, pesos)) % 11
    return 0 if resto < 2 else 11 - resto


def calcular_dv(base12: str) -> str:
    """Calcula os dois dígitos verificadores para as 12 primeiras posições."""
    base12 = normalizar(base12)
    if not re.fullmatch(r"[0-9A-Z]{12}", base12):
        raise CNPJInvalido(f"Base de CNPJ inválida: {base12!r}")
    valores = [ord(c) - 48 for c in base12]
    d1 = _dv(valores, _PESOS_DV1)
    d2 = _dv(valores + [d1], _PESOS_DV2)
    return f"{d1}{d2}"


def validar(cnpj: str) -> str:
    """Valida e devolve o CNPJ normalizado (14 caracteres). Lança CNPJInvalido."""
    n = normalizar(cnpj)
    if not _FORMATO.fullmatch(n):
        raise CNPJInvalido(f"Formato inválido: {cnpj!r}")
    if len(set(n)) == 1:
        raise CNPJInvalido(f"Sequência repetida não é CNPJ válido: {cnpj!r}")
    if calcular_dv(n[:12]) != n[12:]:
        raise CNPJInvalido(f"Dígito verificador não confere: {cnpj!r}")
    return n


def eh_valido(cnpj: str) -> bool:
    try:
        validar(cnpj)
        return True
    except CNPJInvalido:
        return False


def formatar(cnpj: str) -> str:
    n = validar(cnpj)
    return f"{n[:2]}.{n[2:5]}.{n[5:8]}/{n[8:12]}-{n[12:]}"


def raiz(cnpj: str) -> str:
    """Raiz (8 primeiras posições): identifica a empresa, todas as filiais juntas."""
    return validar(cnpj)[:8]
