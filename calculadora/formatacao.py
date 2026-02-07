"""Módulo de formatação para exibição dos resultados."""


def formatar_moeda(valor: float) -> str:
    """Formata um valor como moeda brasileira (R$)."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_percentual(valor: float) -> str:
    """Formata um valor como percentual."""
    return f"{valor:.4f}%"


def exibir_tabela_amortizacao(parcelas: list) -> str:
    """Formata a tabela de amortização para exibição."""
    linhas = []
    header = f"{'Nº':>4} | {'Prestação':>14} | {'Juros':>14} | {'Amortização':>14} | {'Saldo Devedor':>14}"
    separador = "-" * len(header)

    linhas.append(separador)
    linhas.append(header)
    linhas.append(separador)

    total_prestacao = 0.0
    total_juros = 0.0
    total_amortizacao = 0.0

    for p in parcelas:
        linhas.append(
            f"{p.numero:>4} | {formatar_moeda(p.prestacao):>14} | "
            f"{formatar_moeda(p.juros):>14} | {formatar_moeda(p.amortizacao):>14} | "
            f"{formatar_moeda(p.saldo_devedor):>14}"
        )
        total_prestacao += p.prestacao
        total_juros += p.juros
        total_amortizacao += p.amortizacao

    linhas.append(separador)
    linhas.append(
        f"{'Tot':>4} | {formatar_moeda(total_prestacao):>14} | "
        f"{formatar_moeda(total_juros):>14} | {formatar_moeda(total_amortizacao):>14} | "
        f"{'':>14}"
    )
    linhas.append(separador)

    return "\n".join(linhas)
