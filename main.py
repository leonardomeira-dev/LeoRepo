#!/usr/bin/env python3
"""
Calculadora de Renda Fixa Brasileira — Interface de Linha de Comando
=====================================================================

Uso:
    python main.py              # modo interativo
    python main.py --exemplo    # roda com valores de exemplo pré-definidos
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from renda_fixa.calculadora import (
    Investimento,
    ResultadoInvestimento,
    TipoInvestimento,
    calcular,
    comparar,
    taxa_efetiva_cdi,
    taxa_efetiva_ipca,
    taxa_efetiva_poupanca,
)


# ---------------------------------------------------------------------------
# Helpers de I/O
# ---------------------------------------------------------------------------

def _cabecalho(titulo: str) -> None:
    largura = 60
    print()
    print("=" * largura)
    print(f"  {titulo}")
    print("=" * largura)


def _ler_float(prompt: str, minimo: float = 0.0) -> float:
    while True:
        try:
            valor = float(input(f"  {prompt}").replace(",", "."))
            if valor < minimo:
                print(f"  [erro] Valor deve ser >= {minimo}. Tente novamente.")
                continue
            return valor
        except ValueError:
            print("  [erro] Entrada inválida. Use números (ex: 10.5 ou 10,5).")


def _ler_int(prompt: str, minimo: int = 1) -> int:
    while True:
        try:
            valor = int(input(f"  {prompt}"))
            if valor < minimo:
                print(f"  [erro] Valor deve ser >= {minimo}. Tente novamente.")
                continue
            return valor
        except ValueError:
            print("  [erro] Entrada inválida. Use números inteiros.")


def _ler_dias() -> int:
    """Lê o prazo em dias, meses ou anos e converte para dias corridos."""
    print()
    print("  Informe o prazo de investimento:")
    print("    1 - Dias")
    print("    2 - Meses")
    print("    3 - Anos")
    while True:
        opcao = input("  Opção (1/2/3): ").strip()
        if opcao == "1":
            return _ler_int("Quantidade de dias: ")
        if opcao == "2":
            meses = _ler_int("Quantidade de meses: ")
            return meses * 30
        if opcao == "3":
            anos = _ler_int("Quantidade de anos: ")
            return anos * 365
        print("  [erro] Opção inválida. Digite 1, 2 ou 3.")


# ---------------------------------------------------------------------------
# Modo interativo
# ---------------------------------------------------------------------------

def _modo_interativo() -> None:
    _cabecalho("CALCULADORA DE RENDA FIXA BRASILEIRA")

    # --- Valor e prazo ---
    print()
    print("  --- Dados Gerais ---")
    valor_inicial = _ler_float("Valor a investir (R$): ", minimo=0.01)
    dias = _ler_dias()

    # --- Taxas de mercado ---
    print()
    print("  --- Taxas de Mercado (valores atuais aproximados) ---")
    cdi_anual = _ler_float("CDI anual (%): ", minimo=0.0) / 100.0
    selic_anual = _ler_float("Selic anual (%): ", minimo=0.0) / 100.0
    ipca_anual = _ler_float("IPCA anual (%) [expectativa]: ", minimo=0.0) / 100.0

    # --- Parâmetros de cada produto ---
    print()
    print("  --- Parâmetros dos Investimentos ---")

    perc_cdi_cdb = _ler_float("CDB: % do CDI oferecido (ex: 110): ", minimo=0.0)
    perc_cdi_lci = _ler_float("LCI: % do CDI oferecido (ex: 92): ", minimo=0.0)
    perc_cdi_lca = _ler_float("LCA: % do CDI oferecido (ex: 93): ", minimo=0.0)
    spread_ipca = _ler_float("Tesouro IPCA+: spread anual (% acima do IPCA, ex: 6.5): ", minimo=0.0) / 100.0
    taxa_pre = _ler_float("Tesouro Prefixado: taxa anual (%, ex: 14.5): ", minimo=0.0) / 100.0

    # --- Montar lista de investimentos ---
    investimentos: List[Investimento] = [
        Investimento(
            tipo=TipoInvestimento.CDB,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_cdi(cdi_anual, perc_cdi_cdb),
            nome=f"CDB {perc_cdi_cdb:.0f}% CDI",
        ),
        Investimento(
            tipo=TipoInvestimento.LCI,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_cdi(cdi_anual, perc_cdi_lci),
            nome=f"LCI {perc_cdi_lci:.0f}% CDI (isento IR)",
        ),
        Investimento(
            tipo=TipoInvestimento.LCA,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_cdi(cdi_anual, perc_cdi_lca),
            nome=f"LCA {perc_cdi_lca:.0f}% CDI (isento IR)",
        ),
        Investimento(
            tipo=TipoInvestimento.TESOURO_SELIC,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=selic_anual,
            nome="Tesouro Selic",
        ),
        Investimento(
            tipo=TipoInvestimento.TESOURO_IPCA,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_ipca(ipca_anual, spread_ipca),
            nome=f"Tesouro IPCA+ {spread_ipca * 100:.2f}%",
        ),
        Investimento(
            tipo=TipoInvestimento.TESOURO_PREFIXADO,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_pre,
            nome=f"Tesouro Prefixado {taxa_pre * 100:.2f}%",
        ),
        Investimento(
            tipo=TipoInvestimento.POUPANCA,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_poupanca(selic_anual),
            nome="Poupança (isento IR)",
        ),
    ]

    _exibir_resultados(investimentos, dias)


# ---------------------------------------------------------------------------
# Modo exemplo (valores pré-definidos)
# ---------------------------------------------------------------------------

def _modo_exemplo() -> None:
    _cabecalho("CALCULADORA DE RENDA FIXA — MODO EXEMPLO")

    valor_inicial = 10_000.00
    dias = 365           # 1 ano
    cdi_anual = 0.1065   # 10,65% a.a.
    selic_anual = 0.1075 # 10,75% a.a.
    ipca_anual = 0.0480  # 4,80% a.a.

    print()
    print("  Parâmetros utilizados:")
    print(f"    Valor inicial:  R$ {valor_inicial:,.2f}")
    print(f"    Prazo:          {dias} dias (1 ano)")
    print(f"    CDI:            {cdi_anual * 100:.2f}% a.a.")
    print(f"    Selic:          {selic_anual * 100:.2f}% a.a.")
    print(f"    IPCA esperado:  {ipca_anual * 100:.2f}% a.a.")

    investimentos: List[Investimento] = [
        Investimento(
            tipo=TipoInvestimento.CDB,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_cdi(cdi_anual, 110.0),
            nome="CDB 110% CDI",
        ),
        Investimento(
            tipo=TipoInvestimento.LCI,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_cdi(cdi_anual, 92.0),
            nome="LCI 92% CDI (isento IR)",
        ),
        Investimento(
            tipo=TipoInvestimento.LCA,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_cdi(cdi_anual, 93.0),
            nome="LCA 93% CDI (isento IR)",
        ),
        Investimento(
            tipo=TipoInvestimento.TESOURO_SELIC,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=selic_anual,
            nome="Tesouro Selic",
        ),
        Investimento(
            tipo=TipoInvestimento.TESOURO_IPCA,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_ipca(ipca_anual, 0.065),
            nome="Tesouro IPCA+ 6,50%",
        ),
        Investimento(
            tipo=TipoInvestimento.TESOURO_PREFIXADO,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=0.1450,
            nome="Tesouro Prefixado 14,50%",
        ),
        Investimento(
            tipo=TipoInvestimento.POUPANCA,
            valor_inicial=valor_inicial,
            dias=dias,
            taxa_anual=taxa_efetiva_poupanca(selic_anual),
            nome="Poupança (isento IR)",
        ),
    ]

    _exibir_resultados(investimentos, dias)


# ---------------------------------------------------------------------------
# Exibição de resultados
# ---------------------------------------------------------------------------

def _exibir_resultados(investimentos: List[Investimento], dias: int) -> None:
    ranking = comparar(investimentos)

    _cabecalho("RESULTADOS DETALHADOS")
    for resultado in ranking:
        print(resultado)

    _cabecalho("RANKING — Rentabilidade Líquida no Período")
    print()
    print(f"  {'#':<4} {'Investimento':<35} {'Rent. Líq.':>12} {'R$ Líquido':>16}")
    print(f"  {'─'*4} {'─'*35} {'─'*12} {'─'*16}")
    for i, r in enumerate(ranking, 1):
        destaque = " ◄ MELHOR" if i == 1 else ""
        print(
            f"  {i:<4} {r.nome:<35} "
            f"{r.rentabilidade_liquida_pct:>10.4f}%  "
            f"R$ {r.valor_liquido:>13,.2f}"
            f"{destaque}"
        )
    print()

    # Resumo: CDB equivalente para produtos isentos
    _cabecalho("CDI EQUIVALENTE (CDB bruto equivalente para produtos isentos de IR)")
    print()
    aliquota_ir_1ano = 0.20  # 20% para 1 ano (181–360 dias)
    if dias > 720:
        aliquota_ir_1ano = 0.15
    elif dias > 360:
        aliquota_ir_1ano = 0.175
    elif dias > 180:
        aliquota_ir_1ano = 0.20
    else:
        aliquota_ir_1ano = 0.225

    cdi_base: float | None = None
    for inv in investimentos:
        if inv.tipo == TipoInvestimento.CDB:
            # extrai o CDI base da taxa do CDB: taxa_cdb = cdi * perc/100
            # não temos acesso direto aqui, mas podemos derivar do resultado
            pass

    isentos = [r for r in ranking if r.isento_ir]
    if isentos:
        print(f"  (Base: alíquota IR de {aliquota_ir_1ano * 100:.1f}% para o prazo de {dias} dias)")
        print()
        for r in isentos:
            # taxa bruta equivalente: taxa_liq / (1 - aliquota_ir)
            taxa_bruta_equiv = r.rentabilidade_liquida_pct / (1.0 - aliquota_ir_1ano)
            print(
                f"  {r.nome:<35}  →  CDB equivalente: {taxa_bruta_equiv:>7.4f}% no período"
            )
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculadora de Renda Fixa Brasileira",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--exemplo",
        action="store_true",
        help="Executa com valores de exemplo pré-definidos (sem precisar digitar).",
    )
    args = parser.parse_args()

    try:
        if args.exemplo:
            _modo_exemplo()
        else:
            _modo_interativo()
    except KeyboardInterrupt:
        print("\n\n  Cálculo cancelado pelo usuário.")
        sys.exit(0)


if __name__ == "__main__":
    main()
