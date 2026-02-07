"""Testes unitários para o módulo de formatação."""

import unittest

from calculadora.calculos import ParcelaAmortizacao
from calculadora.formatacao import exibir_tabela_amortizacao, formatar_moeda, formatar_percentual


class TestFormatarMoeda(unittest.TestCase):
    def test_valor_inteiro(self):
        self.assertEqual(formatar_moeda(1000), "R$ 1.000,00")

    def test_valor_decimal(self):
        self.assertEqual(formatar_moeda(1234.56), "R$ 1.234,56")

    def test_valor_zero(self):
        self.assertEqual(formatar_moeda(0), "R$ 0,00")

    def test_valor_grande(self):
        self.assertEqual(formatar_moeda(1000000), "R$ 1.000.000,00")

    def test_valor_negativo(self):
        self.assertEqual(formatar_moeda(-500.50), "R$ -500,50")


class TestFormatarPercentual(unittest.TestCase):
    def test_percentual(self):
        self.assertEqual(formatar_percentual(5.5), "5.5000%")

    def test_percentual_zero(self):
        self.assertEqual(formatar_percentual(0), "0.0000%")


class TestExibirTabelaAmortizacao(unittest.TestCase):
    def test_tabela_com_parcelas(self):
        parcelas = [
            ParcelaAmortizacao(1, 1100.0, 100.0, 1000.0, 9000.0),
            ParcelaAmortizacao(2, 1090.0, 90.0, 1000.0, 8000.0),
        ]
        tabela = exibir_tabela_amortizacao(parcelas)
        self.assertIn("Prestação", tabela)
        self.assertIn("Juros", tabela)
        self.assertIn("Amortização", tabela)
        self.assertIn("Saldo Devedor", tabela)
        self.assertIn("Tot", tabela)


if __name__ == "__main__":
    unittest.main()
