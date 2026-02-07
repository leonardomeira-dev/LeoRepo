"""Módulo com as funções de cálculos financeiros."""

from dataclasses import dataclass


@dataclass
class ParcelaAmortizacao:
    """Representa uma parcela em uma tabela de amortização."""

    numero: int
    prestacao: float
    juros: float
    amortizacao: float
    saldo_devedor: float


def juros_simples(capital: float, taxa: float, periodo: int) -> dict:
    """Calcula juros simples.

    Args:
        capital: Valor principal.
        taxa: Taxa de juros por período (em decimal, ex: 0.05 para 5%).
        periodo: Número de períodos.

    Returns:
        Dicionário com juros e montante.
    """
    juros = capital * taxa * periodo
    montante = capital + juros
    return {"capital": capital, "taxa": taxa, "periodo": periodo, "juros": juros, "montante": montante}


def juros_compostos(capital: float, taxa: float, periodo: int) -> dict:
    """Calcula juros compostos.

    Args:
        capital: Valor principal.
        taxa: Taxa de juros por período (em decimal).
        periodo: Número de períodos.

    Returns:
        Dicionário com juros e montante.
    """
    montante = capital * (1 + taxa) ** periodo
    juros = montante - capital
    return {"capital": capital, "taxa": taxa, "periodo": periodo, "juros": juros, "montante": montante}


def valor_presente(valor_futuro: float, taxa: float, periodo: int) -> float:
    """Calcula o valor presente dado um valor futuro.

    Args:
        valor_futuro: Valor futuro desejado.
        taxa: Taxa de desconto por período (em decimal).
        periodo: Número de períodos.

    Returns:
        Valor presente.
    """
    return valor_futuro / (1 + taxa) ** periodo


def valor_futuro(valor_presente_val: float, taxa: float, periodo: int) -> float:
    """Calcula o valor futuro dado um valor presente.

    Args:
        valor_presente_val: Valor presente.
        taxa: Taxa de juros por período (em decimal).
        periodo: Número de períodos.

    Returns:
        Valor futuro.
    """
    return valor_presente_val * (1 + taxa) ** periodo


def amortizacao_sac(capital: float, taxa: float, periodo: int) -> list[ParcelaAmortizacao]:
    """Calcula amortização pelo Sistema de Amortização Constante (SAC).

    Args:
        capital: Valor do empréstimo.
        taxa: Taxa de juros por período (em decimal).
        periodo: Número de parcelas.

    Returns:
        Lista de parcelas com detalhes da amortização.
    """
    amortizacao_fixa = capital / periodo
    saldo = capital
    parcelas = []

    for i in range(1, periodo + 1):
        juros = saldo * taxa
        prestacao = amortizacao_fixa + juros
        saldo -= amortizacao_fixa
        parcelas.append(
            ParcelaAmortizacao(
                numero=i,
                prestacao=round(prestacao, 2),
                juros=round(juros, 2),
                amortizacao=round(amortizacao_fixa, 2),
                saldo_devedor=round(max(saldo, 0), 2),
            )
        )

    return parcelas


def amortizacao_price(capital: float, taxa: float, periodo: int) -> list[ParcelaAmortizacao]:
    """Calcula amortização pela Tabela Price (parcelas fixas).

    Args:
        capital: Valor do empréstimo.
        taxa: Taxa de juros por período (em decimal).
        periodo: Número de parcelas.

    Returns:
        Lista de parcelas com detalhes da amortização.
    """
    prestacao_fixa = capital * (taxa * (1 + taxa) ** periodo) / ((1 + taxa) ** periodo - 1)
    saldo = capital
    parcelas = []

    for i in range(1, periodo + 1):
        juros = saldo * taxa
        amortizacao = prestacao_fixa - juros
        saldo -= amortizacao
        parcelas.append(
            ParcelaAmortizacao(
                numero=i,
                prestacao=round(prestacao_fixa, 2),
                juros=round(juros, 2),
                amortizacao=round(amortizacao, 2),
                saldo_devedor=round(max(saldo, 0), 2),
            )
        )

    return parcelas


def retorno_investimento(ganho: float, custo: float) -> dict:
    """Calcula o Retorno sobre Investimento (ROI).

    Args:
        ganho: Valor ganho com o investimento.
        custo: Custo do investimento.

    Returns:
        Dicionário com lucro, ROI percentual e resultado.
    """
    lucro = ganho - custo
    roi = (lucro / custo) * 100
    return {"ganho": ganho, "custo": custo, "lucro": lucro, "roi_percentual": roi}


def taxa_equivalente(taxa: float, periodo_origem: int, periodo_destino: int) -> float:
    """Converte uma taxa de juros de um período para outro.

    Ex: taxa mensal para anual (periodo_origem=1, periodo_destino=12).

    Args:
        taxa: Taxa no período de origem (em decimal).
        periodo_origem: Período da taxa original.
        periodo_destino: Período desejado.

    Returns:
        Taxa equivalente no período de destino.
    """
    return (1 + taxa) ** (periodo_destino / periodo_origem) - 1


def ponto_equilibrio(custos_fixos: float, preco_venda: float, custo_variavel: float) -> dict:
    """Calcula o ponto de equilíbrio (break-even point).

    Args:
        custos_fixos: Total de custos fixos.
        preco_venda: Preço de venda unitário.
        custo_variavel: Custo variável unitário.

    Returns:
        Dicionário com quantidade e receita no ponto de equilíbrio.
    """
    margem = preco_venda - custo_variavel
    quantidade = custos_fixos / margem
    receita = quantidade * preco_venda
    return {
        "custos_fixos": custos_fixos,
        "preco_venda": preco_venda,
        "custo_variavel": custo_variavel,
        "quantidade_equilibrio": quantidade,
        "receita_equilibrio": receita,
    }
