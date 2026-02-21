"""
Testes unitários para a Calculadora de Renda Fixa Brasileira.
"""

import math
import pytest

from renda_fixa.calculadora import (
    Investimento,
    ResultadoInvestimento,
    TipoInvestimento,
    aliquota_iof,
    aliquota_ir,
    calcular,
    comparar,
    taxa_efetiva_cdi,
    taxa_efetiva_ipca,
    taxa_efetiva_poupanca,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _approx(valor: float, rel: float = 1e-6) -> pytest.approx:  # type: ignore[type-arg]
    return pytest.approx(valor, rel=rel)


# ---------------------------------------------------------------------------
# aliquota_iof
# ---------------------------------------------------------------------------

class TestAliquotaIOF:
    def test_dia_1(self):
        assert aliquota_iof(1) == pytest.approx(0.96)

    def test_dia_15(self):
        assert aliquota_iof(15) == pytest.approx(0.50)

    def test_dia_30(self):
        assert aliquota_iof(30) == 0.0

    def test_apos_30_dias(self):
        assert aliquota_iof(31) == 0.0
        assert aliquota_iof(365) == 0.0

    def test_dia_29(self):
        assert aliquota_iof(29) == pytest.approx(0.03)


# ---------------------------------------------------------------------------
# aliquota_ir
# ---------------------------------------------------------------------------

class TestAliquotaIR:
    def test_ate_180_dias(self):
        assert aliquota_ir(180) == pytest.approx(0.225)
        assert aliquota_ir(1) == pytest.approx(0.225)

    def test_181_a_360_dias(self):
        assert aliquota_ir(181) == pytest.approx(0.20)
        assert aliquota_ir(360) == pytest.approx(0.20)

    def test_361_a_720_dias(self):
        assert aliquota_ir(361) == pytest.approx(0.175)
        assert aliquota_ir(720) == pytest.approx(0.175)

    def test_acima_720_dias(self):
        assert aliquota_ir(721) == pytest.approx(0.15)
        assert aliquota_ir(1000) == pytest.approx(0.15)

    def test_isento(self):
        assert aliquota_ir(30, isento=True) == 0.0
        assert aliquota_ir(365, isento=True) == 0.0
        assert aliquota_ir(1000, isento=True) == 0.0


# ---------------------------------------------------------------------------
# Helpers de taxa
# ---------------------------------------------------------------------------

class TestTaxaEfetivaCDI:
    def test_100_pct_cdi(self):
        cdi = 0.1065
        assert taxa_efetiva_cdi(cdi, 100.0) == pytest.approx(0.1065)

    def test_110_pct_cdi(self):
        cdi = 0.1065
        assert taxa_efetiva_cdi(cdi, 110.0) == pytest.approx(0.11715)

    def test_zero_cdi(self):
        assert taxa_efetiva_cdi(0.1065, 0.0) == 0.0


class TestTaxaEfetivaIPCA:
    def test_composicao(self):
        ipca = 0.048
        spread = 0.065
        esperado = (1.048) * (1.065) - 1.0
        assert taxa_efetiva_ipca(ipca, spread) == pytest.approx(esperado)

    def test_zero_spread(self):
        ipca = 0.048
        assert taxa_efetiva_ipca(ipca, 0.0) == pytest.approx(ipca)


class TestTaxaEfetivaPoupanca:
    def test_selic_acima_8_5(self):
        # 0.5% a.m. → (1.005)^12 - 1
        esperado = (1.005) ** 12 - 1.0
        assert taxa_efetiva_poupanca(0.1075) == pytest.approx(esperado, rel=1e-9)

    def test_selic_igual_8_5(self):
        # Exatamente 8.5% → fronteira: usa 70% do Selic
        esperado = 0.085 * 0.70
        assert taxa_efetiva_poupanca(0.085) == pytest.approx(esperado)

    def test_selic_abaixo_8_5(self):
        esperado = 0.06 * 0.70
        assert taxa_efetiva_poupanca(0.06) == pytest.approx(esperado)


# ---------------------------------------------------------------------------
# calcular — CDB por 1 ano (365 dias)
# ---------------------------------------------------------------------------

class TestCalcularCDB:
    """CDB 110% CDI, CDI = 10,65% a.a., 365 dias."""

    @pytest.fixture
    def resultado(self) -> ResultadoInvestimento:
        taxa = taxa_efetiva_cdi(0.1065, 110.0)  # 11,715% a.a.
        inv = Investimento(
            tipo=TipoInvestimento.CDB,
            valor_inicial=10_000.0,
            dias=365,
            taxa_anual=taxa,
            nome="CDB 110% CDI",
        )
        return calcular(inv)

    def test_sem_iof_apos_30_dias(self, resultado):
        assert resultado.iof == 0.0

    def test_aliquota_ir_365_dias(self, resultado):
        # 181–360 → 20%; 365 dias entra na faixa 361–720 → 17,5%
        assert resultado.aliquota_ir_pct == pytest.approx(17.5)

    def test_valor_bruto_positivo(self, resultado):
        assert resultado.valor_bruto > resultado.valor_inicial

    def test_valor_liquido_menor_bruto(self, resultado):
        assert resultado.valor_liquido < resultado.valor_bruto

    def test_rentabilidade_positiva(self, resultado):
        assert resultado.rentabilidade_liquida_pct > 0.0

    def test_calculo_manual(self, resultado):
        """Verifica o cálculo passo a passo manualmente."""
        taxa = 0.11715
        bruto = 10_000.0 * (1 + taxa) ** (365 / 365.0)
        rendimento_bruto = bruto - 10_000.0
        # IOF = 0 (365 dias > 30)
        ir = rendimento_bruto * 0.175  # 17,5% para 361–720 dias
        liquido = 10_000.0 + rendimento_bruto - ir

        assert resultado.valor_bruto == pytest.approx(bruto, rel=1e-9)
        assert resultado.ir == pytest.approx(ir, rel=1e-9)
        assert resultado.valor_liquido == pytest.approx(liquido, rel=1e-9)


# ---------------------------------------------------------------------------
# calcular — LCI por 1 ano (isento IR)
# ---------------------------------------------------------------------------

class TestCalcularLCI:
    """LCI 92% CDI, CDI = 10,65% a.a., 365 dias — isento IR."""

    @pytest.fixture
    def resultado(self) -> ResultadoInvestimento:
        taxa = taxa_efetiva_cdi(0.1065, 92.0)
        inv = Investimento(
            tipo=TipoInvestimento.LCI,
            valor_inicial=10_000.0,
            dias=365,
            taxa_anual=taxa,
            nome="LCI 92% CDI",
        )
        return calcular(inv)

    def test_ir_zero(self, resultado):
        assert resultado.ir == 0.0

    def test_isento_ir_flag(self, resultado):
        assert resultado.isento_ir is True

    def test_valor_liquido_igual_bruto_menos_iof(self, resultado):
        # Sem IR e sem IOF (> 30 dias): líquido == bruto
        assert resultado.valor_liquido == pytest.approx(resultado.valor_bruto, rel=1e-9)


# ---------------------------------------------------------------------------
# calcular — Curto prazo (IOF incide)
# ---------------------------------------------------------------------------

class TestCalcularCurtoPrazo:
    """CDB 100% CDI, CDI = 10,65% a.a., 15 dias — IOF deve incidir."""

    @pytest.fixture
    def resultado(self) -> ResultadoInvestimento:
        inv = Investimento(
            tipo=TipoInvestimento.CDB,
            valor_inicial=1_000.0,
            dias=15,
            taxa_anual=0.1065,
            nome="CDB 100% CDI curto prazo",
        )
        return calcular(inv)

    def test_iof_positivo(self, resultado):
        assert resultado.iof > 0.0

    def test_aliquota_iof_15_dias(self, resultado):
        # Dia 15 → 50%
        assert resultado.aliquota_iof_pct == pytest.approx(50.0)

    def test_aliquota_ir_curto_prazo(self, resultado):
        # ≤ 180 dias → 22,5%
        assert resultado.aliquota_ir_pct == pytest.approx(22.5)

    def test_sequencia_tributacao(self, resultado):
        """IOF incide antes do IR."""
        # IOF é sobre o rendimento bruto; IR é sobre o rendimento pós-IOF
        assert resultado.iof <= resultado.rendimento_bruto
        rendimento_apos_iof = resultado.rendimento_bruto - resultado.iof
        assert resultado.ir == pytest.approx(rendimento_apos_iof * 0.225, rel=1e-9)


# ---------------------------------------------------------------------------
# calcular — Poupança
# ---------------------------------------------------------------------------

class TestCalcularPoupanca:
    def test_isento_ir(self):
        inv = Investimento(
            tipo=TipoInvestimento.POUPANCA,
            valor_inicial=5_000.0,
            dias=365,
            taxa_anual=taxa_efetiva_poupanca(0.1075),
        )
        r = calcular(inv)
        assert r.ir == 0.0
        assert r.isento_ir is True

    def test_rendimento_positivo(self):
        inv = Investimento(
            tipo=TipoInvestimento.POUPANCA,
            valor_inicial=5_000.0,
            dias=365,
            taxa_anual=taxa_efetiva_poupanca(0.1075),
        )
        r = calcular(inv)
        assert r.valor_liquido > r.valor_inicial


# ---------------------------------------------------------------------------
# comparar
# ---------------------------------------------------------------------------

class TestComparar:
    def test_ordenacao_decrescente(self):
        investimentos = [
            Investimento(
                tipo=TipoInvestimento.CDB,
                valor_inicial=1_000.0,
                dias=365,
                taxa_anual=0.08,
                nome="CDB 8%",
            ),
            Investimento(
                tipo=TipoInvestimento.CDB,
                valor_inicial=1_000.0,
                dias=365,
                taxa_anual=0.15,
                nome="CDB 15%",
            ),
            Investimento(
                tipo=TipoInvestimento.LCI,
                valor_inicial=1_000.0,
                dias=365,
                taxa_anual=0.10,
                nome="LCI 10%",
            ),
        ]
        ranking = comparar(investimentos)
        for i in range(len(ranking) - 1):
            assert ranking[i].rentabilidade_liquida_pct >= ranking[i + 1].rentabilidade_liquida_pct

    def test_lista_vazia(self):
        assert comparar([]) == []

    def test_retorna_todos(self):
        investimentos = [
            Investimento(
                tipo=TipoInvestimento.CDB,
                valor_inicial=1_000.0,
                dias=365,
                taxa_anual=0.12,
            ),
            Investimento(
                tipo=TipoInvestimento.POUPANCA,
                valor_inicial=1_000.0,
                dias=365,
                taxa_anual=taxa_efetiva_poupanca(0.1075),
            ),
        ]
        ranking = comparar(investimentos)
        assert len(ranking) == 2


# ---------------------------------------------------------------------------
# Validação de entrada
# ---------------------------------------------------------------------------

class TestValidacaoEntrada:
    def test_valor_inicial_zero(self):
        with pytest.raises(ValueError, match="valor_inicial"):
            Investimento(
                tipo=TipoInvestimento.CDB,
                valor_inicial=0.0,
                dias=365,
                taxa_anual=0.1065,
            )

    def test_valor_inicial_negativo(self):
        with pytest.raises(ValueError, match="valor_inicial"):
            Investimento(
                tipo=TipoInvestimento.CDB,
                valor_inicial=-100.0,
                dias=365,
                taxa_anual=0.1065,
            )

    def test_dias_zero(self):
        with pytest.raises(ValueError, match="dias"):
            Investimento(
                tipo=TipoInvestimento.CDB,
                valor_inicial=1_000.0,
                dias=0,
                taxa_anual=0.1065,
            )

    def test_taxa_negativa(self):
        with pytest.raises(ValueError, match="taxa_anual"):
            Investimento(
                tipo=TipoInvestimento.CDB,
                valor_inicial=1_000.0,
                dias=365,
                taxa_anual=-0.01,
            )


# ---------------------------------------------------------------------------
# Rentabilidade anualizada
# ---------------------------------------------------------------------------

class TestRentabilidadeAnualizada:
    def test_365_dias_aa_igual_periodo(self):
        """Para 365 dias, rent. a.a. deve ser igual à rent. do período."""
        inv = Investimento(
            tipo=TipoInvestimento.LCI,
            valor_inicial=1_000.0,
            dias=365,
            taxa_anual=0.10,
        )
        r = calcular(inv)
        # Sem IR e sem IOF: líquido == bruto
        assert r.rentabilidade_bruta_pct == pytest.approx(r.rentabilidade_bruta_aa, rel=1e-6)

    def test_anualizada_maior_para_prazo_curto(self):
        """Para prazo < 365 dias, a taxa a.a. deve ser maior que a do período."""
        inv = Investimento(
            tipo=TipoInvestimento.LCI,
            valor_inicial=1_000.0,
            dias=180,
            taxa_anual=0.10,
        )
        r = calcular(inv)
        assert r.rentabilidade_bruta_aa > r.rentabilidade_bruta_pct
