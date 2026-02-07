"""Interface de linha de comando interativa da calculadora financeira."""

from calculadora.calculos import (
    amortizacao_price,
    amortizacao_sac,
    juros_compostos,
    juros_simples,
    ponto_equilibrio,
    retorno_investimento,
    taxa_equivalente,
    valor_futuro,
    valor_presente,
)
from calculadora.formatacao import exibir_tabela_amortizacao, formatar_moeda, formatar_percentual

MENU = """
╔══════════════════════════════════════════════╗
║        CALCULADORA FINANCEIRA               ║
╠══════════════════════════════════════════════╣
║  1. Juros Simples                           ║
║  2. Juros Compostos                         ║
║  3. Valor Presente                          ║
║  4. Valor Futuro                            ║
║  5. Amortização SAC                         ║
║  6. Amortização Price (Tabela Price)        ║
║  7. Retorno sobre Investimento (ROI)        ║
║  8. Taxa Equivalente                        ║
║  9. Ponto de Equilíbrio                     ║
║  0. Sair                                    ║
╚══════════════════════════════════════════════╝
"""


def ler_float(mensagem: str) -> float:
    """Lê um valor float do usuário com validação."""
    while True:
        try:
            valor = input(mensagem).strip().replace(",", ".")
            return float(valor)
        except ValueError:
            print("  Valor inválido. Digite um número válido.")


def ler_int(mensagem: str) -> int:
    """Lê um valor inteiro do usuário com validação."""
    while True:
        try:
            return int(input(mensagem).strip())
        except ValueError:
            print("  Valor inválido. Digite um número inteiro.")


def ler_taxa(mensagem: str = "  Taxa de juros (% por período): ") -> float:
    """Lê uma taxa percentual e converte para decimal."""
    return ler_float(mensagem) / 100


def opcao_juros_simples():
    """Interface para cálculo de juros simples."""
    print("\n── Juros Simples ──")
    capital = ler_float("  Capital (R$): ")
    taxa = ler_taxa()
    periodo = ler_int("  Número de períodos: ")

    resultado = juros_simples(capital, taxa, periodo)
    print(f"\n  Capital:  {formatar_moeda(resultado['capital'])}")
    print(f"  Taxa:     {formatar_percentual(resultado['taxa'] * 100)} por período")
    print(f"  Período:  {resultado['periodo']} períodos")
    print(f"  Juros:    {formatar_moeda(resultado['juros'])}")
    print(f"  Montante: {formatar_moeda(resultado['montante'])}")


def opcao_juros_compostos():
    """Interface para cálculo de juros compostos."""
    print("\n── Juros Compostos ──")
    capital = ler_float("  Capital (R$): ")
    taxa = ler_taxa()
    periodo = ler_int("  Número de períodos: ")

    resultado = juros_compostos(capital, taxa, periodo)
    print(f"\n  Capital:  {formatar_moeda(resultado['capital'])}")
    print(f"  Taxa:     {formatar_percentual(resultado['taxa'] * 100)} por período")
    print(f"  Período:  {resultado['periodo']} períodos")
    print(f"  Juros:    {formatar_moeda(resultado['juros'])}")
    print(f"  Montante: {formatar_moeda(resultado['montante'])}")


def opcao_valor_presente():
    """Interface para cálculo de valor presente."""
    print("\n── Valor Presente ──")
    vf = ler_float("  Valor Futuro (R$): ")
    taxa = ler_taxa("  Taxa de desconto (% por período): ")
    periodo = ler_int("  Número de períodos: ")

    vp = valor_presente(vf, taxa, periodo)
    print(f"\n  Valor Futuro:   {formatar_moeda(vf)}")
    print(f"  Valor Presente: {formatar_moeda(vp)}")


def opcao_valor_futuro():
    """Interface para cálculo de valor futuro."""
    print("\n── Valor Futuro ──")
    vp = ler_float("  Valor Presente (R$): ")
    taxa = ler_taxa()
    periodo = ler_int("  Número de períodos: ")

    vf = valor_futuro(vp, taxa, periodo)
    print(f"\n  Valor Presente: {formatar_moeda(vp)}")
    print(f"  Valor Futuro:   {formatar_moeda(vf)}")


def opcao_amortizacao_sac():
    """Interface para cálculo de amortização SAC."""
    print("\n── Amortização SAC ──")
    capital = ler_float("  Valor do empréstimo (R$): ")
    taxa = ler_taxa("  Taxa de juros (% por período): ")
    periodo = ler_int("  Número de parcelas: ")

    parcelas = amortizacao_sac(capital, taxa, periodo)
    print(f"\n  Empréstimo: {formatar_moeda(capital)}")
    print(f"  Parcelas:   {periodo}\n")
    print(exibir_tabela_amortizacao(parcelas))


def opcao_amortizacao_price():
    """Interface para cálculo de amortização Price."""
    print("\n── Amortização Price (Tabela Price) ──")
    capital = ler_float("  Valor do empréstimo (R$): ")
    taxa = ler_taxa("  Taxa de juros (% por período): ")
    periodo = ler_int("  Número de parcelas: ")

    parcelas = amortizacao_price(capital, taxa, periodo)
    print(f"\n  Empréstimo: {formatar_moeda(capital)}")
    print(f"  Parcelas:   {periodo}")
    print(f"  Prestação fixa: {formatar_moeda(parcelas[0].prestacao)}\n")
    print(exibir_tabela_amortizacao(parcelas))


def opcao_roi():
    """Interface para cálculo de ROI."""
    print("\n── Retorno sobre Investimento (ROI) ──")
    ganho = ler_float("  Valor ganho com o investimento (R$): ")
    custo = ler_float("  Custo do investimento (R$): ")

    resultado = retorno_investimento(ganho, custo)
    print(f"\n  Ganho:  {formatar_moeda(resultado['ganho'])}")
    print(f"  Custo:  {formatar_moeda(resultado['custo'])}")
    print(f"  Lucro:  {formatar_moeda(resultado['lucro'])}")
    print(f"  ROI:    {formatar_percentual(resultado['roi_percentual'])}")


def opcao_taxa_equivalente():
    """Interface para conversão de taxa equivalente."""
    print("\n── Taxa Equivalente ──")
    print("  Exemplos de períodos:")
    print("    Diário=1, Mensal=30, Bimestral=60, Trimestral=90")
    print("    Semestral=180, Anual=360")
    taxa = ler_taxa("  Taxa de juros conhecida (%): ")
    origem = ler_int("  Período da taxa conhecida (dias): ")
    destino = ler_int("  Período desejado (dias): ")

    taxa_eq = taxa_equivalente(taxa, origem, destino)
    print(f"\n  Taxa original:    {formatar_percentual(taxa * 100)} para {origem} dias")
    print(f"  Taxa equivalente: {formatar_percentual(taxa_eq * 100)} para {destino} dias")


def opcao_ponto_equilibrio():
    """Interface para cálculo do ponto de equilíbrio."""
    print("\n── Ponto de Equilíbrio ──")
    custos_fixos = ler_float("  Custos fixos totais (R$): ")
    preco_venda = ler_float("  Preço de venda unitário (R$): ")
    custo_variavel = ler_float("  Custo variável unitário (R$): ")

    resultado = ponto_equilibrio(custos_fixos, preco_venda, custo_variavel)
    print(f"\n  Custos Fixos:           {formatar_moeda(resultado['custos_fixos'])}")
    print(f"  Preço de Venda:         {formatar_moeda(resultado['preco_venda'])}")
    print(f"  Custo Variável:         {formatar_moeda(resultado['custo_variavel'])}")
    print(f"  Quantidade Equilíbrio:  {resultado['quantidade_equilibrio']:.2f} unidades")
    print(f"  Receita Equilíbrio:     {formatar_moeda(resultado['receita_equilibrio'])}")


OPCOES = {
    "1": opcao_juros_simples,
    "2": opcao_juros_compostos,
    "3": opcao_valor_presente,
    "4": opcao_valor_futuro,
    "5": opcao_amortizacao_sac,
    "6": opcao_amortizacao_price,
    "7": opcao_roi,
    "8": opcao_taxa_equivalente,
    "9": opcao_ponto_equilibrio,
}


def main():
    """Loop principal da calculadora financeira."""
    print("\nBem-vindo à Calculadora Financeira!")

    while True:
        print(MENU)
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("\nObrigado por usar a Calculadora Financeira. Até logo!")
            break

        funcao = OPCOES.get(escolha)
        if funcao:
            funcao()
            input("\nPressione Enter para continuar...")
        else:
            print("\nOpção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
