"""Testes unitários para o módulo de cálculos financeiros."""

import unittest

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


class TestJurosSimples(unittest.TestCase):
    def test_calculo_basico(self):
        resultado = juros_simples(1000, 0.05, 12)
        self.assertAlmostEqual(resultado["juros"], 600.0)
        self.assertAlmostEqual(resultado["montante"], 1600.0)

    def test_taxa_zero(self):
        resultado = juros_simples(1000, 0, 12)
        self.assertAlmostEqual(resultado["juros"], 0.0)
        self.assertAlmostEqual(resultado["montante"], 1000.0)

    def test_periodo_zero(self):
        resultado = juros_simples(1000, 0.05, 0)
        self.assertAlmostEqual(resultado["juros"], 0.0)
        self.assertAlmostEqual(resultado["montante"], 1000.0)


class TestJurosCompostos(unittest.TestCase):
    def test_calculo_basico(self):
        resultado = juros_compostos(1000, 0.10, 3)
        self.assertAlmostEqual(resultado["montante"], 1331.0, places=2)
        self.assertAlmostEqual(resultado["juros"], 331.0, places=2)

    def test_taxa_zero(self):
        resultado = juros_compostos(1000, 0, 12)
        self.assertAlmostEqual(resultado["montante"], 1000.0)

    def test_um_periodo(self):
        resultado = juros_compostos(1000, 0.10, 1)
        self.assertAlmostEqual(resultado["montante"], 1100.0)


class TestValorPresente(unittest.TestCase):
    def test_calculo_basico(self):
        vp = valor_presente(1331, 0.10, 3)
        self.assertAlmostEqual(vp, 1000.0, places=0)

    def test_periodo_zero(self):
        vp = valor_presente(1000, 0.10, 0)
        self.assertAlmostEqual(vp, 1000.0)


class TestValorFuturo(unittest.TestCase):
    def test_calculo_basico(self):
        vf = valor_futuro(1000, 0.10, 3)
        self.assertAlmostEqual(vf, 1331.0, places=2)

    def test_periodo_zero(self):
        vf = valor_futuro(1000, 0.10, 0)
        self.assertAlmostEqual(vf, 1000.0)


class TestAmortizacaoSAC(unittest.TestCase):
    def test_numero_parcelas(self):
        parcelas = amortizacao_sac(12000, 0.01, 12)
        self.assertEqual(len(parcelas), 12)

    def test_amortizacao_constante(self):
        parcelas = amortizacao_sac(12000, 0.01, 12)
        for p in parcelas:
            self.assertAlmostEqual(p.amortizacao, 1000.0, places=2)

    def test_prestacao_decrescente(self):
        parcelas = amortizacao_sac(12000, 0.01, 12)
        for i in range(1, len(parcelas)):
            self.assertLess(parcelas[i].prestacao, parcelas[i - 1].prestacao)

    def test_saldo_final_zero(self):
        parcelas = amortizacao_sac(12000, 0.01, 12)
        self.assertAlmostEqual(parcelas[-1].saldo_devedor, 0.0, places=2)


class TestAmortizacaoPrice(unittest.TestCase):
    def test_numero_parcelas(self):
        parcelas = amortizacao_price(12000, 0.01, 12)
        self.assertEqual(len(parcelas), 12)

    def test_prestacao_constante(self):
        parcelas = amortizacao_price(12000, 0.01, 12)
        for p in parcelas:
            self.assertAlmostEqual(p.prestacao, parcelas[0].prestacao, places=2)

    def test_saldo_final_zero(self):
        parcelas = amortizacao_price(12000, 0.01, 12)
        self.assertAlmostEqual(parcelas[-1].saldo_devedor, 0.0, places=1)

    def test_juros_decrescente(self):
        parcelas = amortizacao_price(12000, 0.01, 12)
        for i in range(1, len(parcelas)):
            self.assertLess(parcelas[i].juros, parcelas[i - 1].juros)


class TestROI(unittest.TestCase):
    def test_lucro_positivo(self):
        resultado = retorno_investimento(15000, 10000)
        self.assertAlmostEqual(resultado["lucro"], 5000.0)
        self.assertAlmostEqual(resultado["roi_percentual"], 50.0)

    def test_lucro_negativo(self):
        resultado = retorno_investimento(8000, 10000)
        self.assertAlmostEqual(resultado["lucro"], -2000.0)
        self.assertAlmostEqual(resultado["roi_percentual"], -20.0)


class TestTaxaEquivalente(unittest.TestCase):
    def test_mensal_para_anual(self):
        taxa_anual = taxa_equivalente(0.01, 1, 12)
        self.assertAlmostEqual(taxa_anual, 0.126825, places=4)

    def test_mesma_taxa(self):
        taxa_eq = taxa_equivalente(0.05, 1, 1)
        self.assertAlmostEqual(taxa_eq, 0.05)


class TestPontoEquilibrio(unittest.TestCase):
    def test_calculo_basico(self):
        resultado = ponto_equilibrio(10000, 50, 30)
        self.assertAlmostEqual(resultado["quantidade_equilibrio"], 500.0)
        self.assertAlmostEqual(resultado["receita_equilibrio"], 25000.0)


if __name__ == "__main__":
    unittest.main()
