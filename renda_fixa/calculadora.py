"""
Calculadora de Renda Fixa Brasileira
=====================================

Tipos de investimento suportados:
  - CDB (Certificado de Depósito Bancário)
  - LCI (Letra de Crédito Imobiliário) — isento de IR
  - LCA (Letra de Crédito do Agronegócio) — isento de IR
  - Tesouro Selic
  - Tesouro IPCA+
  - Tesouro Prefixado
  - Poupança — isento de IR

Indexadores:
  - CDI (% do CDI)
  - IPCA + spread
  - Pré-fixado
  - Selic

Impostos calculados:
  - IOF regressivo (dias 1–30)
  - IR regressivo (tabela progressiva de alíquotas decrescentes)

Referências legais:
  - IOF: Decreto 6.306/2007
  - IR: Lei 11.033/2004
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------------------------
# Tabela de IOF (% do rendimento retido, por dia)
# ---------------------------------------------------------------------------
_IOF_TABELA: dict[int, float] = {
    1: 96.0, 2: 93.0, 3: 90.0, 4: 86.0, 5: 83.0,
    6: 80.0, 7: 76.0, 8: 73.0, 9: 70.0, 10: 66.0,
    11: 63.0, 12: 60.0, 13: 56.0, 14: 53.0, 15: 50.0,
    16: 46.0, 17: 43.0, 18: 40.0, 19: 36.0, 20: 33.0,
    21: 30.0, 22: 26.0, 23: 23.0, 24: 20.0, 25: 16.0,
    26: 13.0, 27: 10.0, 28: 6.0, 29: 3.0, 30: 0.0,
}


def aliquota_iof(dias: int) -> float:
    """Retorna a alíquota de IOF aplicável ao rendimento (0–1).

    Após 30 dias corridos: 0%.
    """
    if dias <= 0:
        return _IOF_TABELA[1] / 100.0
    if dias >= 30:
        return 0.0
    return _IOF_TABELA[dias] / 100.0


def aliquota_ir(dias: int, isento: bool = False) -> float:
    """Retorna a alíquota de IR sobre o rendimento após IOF (0–1).

    Tabela regressiva (Lei 11.033/2004):
      ≤ 180 dias   → 22,5%
      181–360 dias → 20,0%
      361–720 dias → 17,5%
      > 720 dias   → 15,0%

    LCI, LCA e Poupança são isentos (isento=True).
    """
    if isento:
        return 0.0
    if dias <= 180:
        return 0.225
    if dias <= 360:
        return 0.20
    if dias <= 720:
        return 0.175
    return 0.15


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TipoIndexador(str, Enum):
    CDI = "CDI"
    IPCA = "IPCA+"
    PREFIXADO = "Pré-fixado"
    SELIC = "Selic"
    POUPANCA = "Poupança"


class TipoInvestimento(str, Enum):
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    TESOURO_SELIC = "Tesouro Selic"
    TESOURO_IPCA = "Tesouro IPCA+"
    TESOURO_PREFIXADO = "Tesouro Prefixado"
    POUPANCA = "Poupança"


# Mapeamento: qual tipo é isento de IR
_ISENTO_IR: dict[TipoInvestimento, bool] = {
    TipoInvestimento.CDB: False,
    TipoInvestimento.LCI: True,
    TipoInvestimento.LCA: True,
    TipoInvestimento.TESOURO_SELIC: False,
    TipoInvestimento.TESOURO_IPCA: False,
    TipoInvestimento.TESOURO_PREFIXADO: False,
    TipoInvestimento.POUPANCA: True,
}


# ---------------------------------------------------------------------------
# Helpers de taxa
# ---------------------------------------------------------------------------

def taxa_efetiva_cdi(cdi_anual: float, percentual: float) -> float:
    """Taxa efetiva anual para investimento atrelado ao CDI.

    Args:
        cdi_anual:  Taxa CDI anual em decimal (ex: 0.1065 = 10,65%).
        percentual: Percentual do CDI contratado (ex: 100.0 = 100% do CDI).
    """
    return cdi_anual * (percentual / 100.0)


def taxa_efetiva_ipca(ipca_anual: float, spread_anual: float) -> float:
    """Taxa efetiva anual para IPCA+.

    Composição: (1 + IPCA) × (1 + spread) − 1
    """
    return (1.0 + ipca_anual) * (1.0 + spread_anual) - 1.0


def taxa_efetiva_poupanca(selic_anual: float) -> float:
    """Taxa efetiva anual da Poupança (ignorando TR, próxima de zero).

    Regra:
      Selic > 8,5% a.a. → 0,5% a.m. (≈ 6,168% a.a.)
      Selic ≤ 8,5% a.a. → 70% da Selic
    """
    if selic_anual > 0.085:
        return (1.0 + 0.005) ** 12 - 1.0
    return selic_anual * 0.70


# ---------------------------------------------------------------------------
# Dataclasses de entrada e saída
# ---------------------------------------------------------------------------

@dataclass
class Investimento:
    """Parâmetros de um investimento a calcular."""

    tipo: TipoInvestimento
    valor_inicial: float
    dias: int
    taxa_anual: float          # Taxa efetiva anual em decimal
    nome: str = ""             # Rótulo personalizado (opcional)

    def __post_init__(self) -> None:
        if not self.nome:
            self.nome = self.tipo.value
        if self.valor_inicial <= 0:
            raise ValueError("valor_inicial deve ser positivo.")
        if self.dias <= 0:
            raise ValueError("dias deve ser positivo.")
        if self.taxa_anual < 0:
            raise ValueError("taxa_anual não pode ser negativa.")

    @property
    def isento_ir(self) -> bool:
        return _ISENTO_IR[self.tipo]


@dataclass
class ResultadoInvestimento:
    """Resultado completo de um investimento."""

    nome: str
    tipo: TipoInvestimento
    valor_inicial: float
    valor_bruto: float
    rendimento_bruto: float
    iof: float
    ir: float
    valor_liquido: float
    rendimento_liquido: float
    rentabilidade_bruta_pct: float   # % do período
    rentabilidade_liquida_pct: float # % do período
    rentabilidade_bruta_aa: float    # % ao ano equivalente
    rentabilidade_liquida_aa: float  # % ao ano equivalente
    aliquota_ir_pct: float
    aliquota_iof_pct: float
    dias: int
    isento_ir: bool

    def _fmt_brl(self, valor: float) -> str:
        return f"R$ {valor:>14,.2f}"

    def __str__(self) -> str:  # noqa: D105
        linha = "─" * 54
        ir_label = "IR (isento)" if self.isento_ir else f"IR ({self.aliquota_ir_pct:.1f}%)"
        iof_label = f"IOF ({self.aliquota_iof_pct:.1f}%)"
        return (
            f"\n┌{linha}┐\n"
            f"│  {self.nome:<52}│\n"
            f"├{linha}┤\n"
            f"│  Valor inicial:       {self._fmt_brl(self.valor_inicial):<20}        │\n"
            f"│  Valor bruto:         {self._fmt_brl(self.valor_bruto):<20}        │\n"
            f"│  {iof_label:<23}{self._fmt_brl(self.iof):<20}        │\n"
            f"│  {ir_label:<23}{self._fmt_brl(self.ir):<20}        │\n"
            f"│  Valor líquido:       {self._fmt_brl(self.valor_liquido):<20}        │\n"
            f"├{linha}┤\n"
            f"│  Rent. bruta:    {self.rentabilidade_bruta_pct:>8.4f}% no período"
            f"  ({self.rentabilidade_bruta_aa:>6.2f}% a.a.)  │\n"
            f"│  Rent. líquida:  {self.rentabilidade_liquida_pct:>8.4f}% no período"
            f"  ({self.rentabilidade_liquida_aa:>6.2f}% a.a.)  │\n"
            f"│  Prazo: {self.dias} dias{'':>43}│\n"
            f"└{linha}┘"
        )


# ---------------------------------------------------------------------------
# Função principal de cálculo
# ---------------------------------------------------------------------------

def calcular(inv: Investimento) -> ResultadoInvestimento:
    """Calcula o retorno líquido de um investimento de renda fixa.

    Fluxo:
        1. Montante bruto: capitalização pelo período (base 365 dias corridos).
        2. IOF sobre o rendimento bruto (se < 30 dias).
        3. IR sobre o rendimento após IOF.
        4. Valor líquido = principal + rendimento pós-IOF − IR.

    Note:
        Para CDI e Selic o mercado usa base 252 dias úteis. Por simplicidade
        e para comparações relativas, este módulo usa 365 dias corridos para
        todos os indexadores. O erro é mínimo (<0,1%) para prazos longos.
    """
    # 1. Valor bruto (juros compostos, base 365 dias corridos)
    valor_bruto = inv.valor_inicial * (1.0 + inv.taxa_anual) ** (inv.dias / 365.0)
    rendimento_bruto = valor_bruto - inv.valor_inicial

    # 2. IOF
    a_iof = aliquota_iof(inv.dias)
    iof = rendimento_bruto * a_iof
    rendimento_apos_iof = rendimento_bruto - iof

    # 3. IR
    a_ir = aliquota_ir(inv.dias, inv.isento_ir)
    ir = rendimento_apos_iof * a_ir

    # 4. Resultado líquido
    rendimento_liquido = rendimento_apos_iof - ir
    valor_liquido = inv.valor_inicial + rendimento_liquido

    # Rentabilidades do período
    rent_bruta_pct = (valor_bruto / inv.valor_inicial - 1.0) * 100.0
    rent_liq_pct = (valor_liquido / inv.valor_inicial - 1.0) * 100.0

    # Rentabilidades anualizadas equivalentes
    rent_bruta_aa = ((1.0 + rent_bruta_pct / 100.0) ** (365.0 / inv.dias) - 1.0) * 100.0
    rent_liq_aa = ((1.0 + rent_liq_pct / 100.0) ** (365.0 / inv.dias) - 1.0) * 100.0

    return ResultadoInvestimento(
        nome=inv.nome,
        tipo=inv.tipo,
        valor_inicial=inv.valor_inicial,
        valor_bruto=valor_bruto,
        rendimento_bruto=rendimento_bruto,
        iof=iof,
        ir=ir,
        valor_liquido=valor_liquido,
        rendimento_liquido=rendimento_liquido,
        rentabilidade_bruta_pct=rent_bruta_pct,
        rentabilidade_liquida_pct=rent_liq_pct,
        rentabilidade_bruta_aa=rent_bruta_aa,
        rentabilidade_liquida_aa=rent_liq_aa,
        aliquota_ir_pct=a_ir * 100.0,
        aliquota_iof_pct=a_iof * 100.0,
        dias=inv.dias,
        isento_ir=inv.isento_ir,
    )


def comparar(investimentos: List[Investimento]) -> List[ResultadoInvestimento]:
    """Calcula e retorna resultados ordenados pela rentabilidade líquida (maior primeiro)."""
    resultados = [calcular(inv) for inv in investimentos]
    return sorted(resultados, key=lambda r: r.rentabilidade_liquida_pct, reverse=True)
