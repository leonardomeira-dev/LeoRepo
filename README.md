# Calculadora de Renda Fixa Brasileira

Calculadora de investimentos de renda fixa com suporte a múltiplos produtos, indexadores e cálculo correto de IOF e IR.

## Produtos suportados

| Produto | Indexador | IR |
|---|---|---|
| CDB | % do CDI | Tabela regressiva |
| LCI | % do CDI | **Isento** |
| LCA | % do CDI | **Isento** |
| Tesouro Selic | Selic | Tabela regressiva |
| Tesouro IPCA+ | IPCA + spread | Tabela regressiva |
| Tesouro Prefixado | Taxa fixa | Tabela regressiva |
| Poupança | Regra da Selic | **Isento** |

## Impostos calculados

**IOF** (Decreto 6.306/2007) — regressivo, incide nos primeiros 30 dias:

| Dia | Alíquota sobre rendimento |
|-----|--------------------------|
| 1 | 96% |
| 15 | 50% |
| 29 | 3% |
| ≥ 30 | 0% |

**IR** (Lei 11.033/2004) — tabela regressiva:

| Prazo | Alíquota |
|-------|----------|
| Até 180 dias | 22,5% |
| 181 a 360 dias | 20,0% |
| 361 a 720 dias | 17,5% |
| Acima de 720 dias | 15,0% |

## Instalação

Requer Python 3.9+. Sem dependências externas para uso; `pytest` apenas para testes.

```bash
git clone <url-do-repo>
cd LeoRepo
```

## Uso

### Modo interativo

```bash
python main.py
```

Você será guiado a informar:
- Valor inicial e prazo
- Taxas de mercado (CDI, Selic, IPCA)
- Parâmetros de cada produto (% CDI, spread IPCA+, taxa prefixada)

### Modo exemplo (valores pré-definidos)

```bash
python main.py --exemplo
```

Exemplo de saída:

```
RANKING — Rentabilidade Líquida no Período

  #    Investimento                          Rent. Líq.       R$ Líquido
  1    Tesouro Prefixado 14,50%               11.9625%  R$     11,196.25 ◄ MELHOR
  2    LCA 93% CDI (isento IR)                 9.9045%  R$     10,990.45
  3    LCI 92% CDI (isento IR)                 9.7980%  R$     10,979.80
  4    CDB 110% CDI                            9.6649%  R$     10,966.49
  5    Tesouro IPCA+ 6,50%                     9.5799%  R$     10,957.99
  6    Tesouro Selic                           8.8688%  R$     10,886.88
  7    Poupança (isento IR)                    6.1678%  R$     10,616.78
```

## Uso como biblioteca

```python
from renda_fixa import Investimento, TipoInvestimento, calcular, comparar
from renda_fixa.calculadora import taxa_efetiva_cdi, taxa_efetiva_ipca, taxa_efetiva_poupanca

# CDB 110% CDI por 1 ano
cdb = Investimento(
    tipo=TipoInvestimento.CDB,
    valor_inicial=10_000.0,
    dias=365,
    taxa_anual=taxa_efetiva_cdi(cdi_anual=0.1065, percentual=110.0),
    nome="CDB 110% CDI",
)

resultado = calcular(cdb)
print(f"Valor líquido: R$ {resultado.valor_liquido:,.2f}")
print(f"Rentabilidade líquida: {resultado.rentabilidade_liquida_pct:.2f}%")

# Comparar múltiplos investimentos (retorna ordenado pelo melhor líquido)
ranking = comparar([cdb, lci, poupanca])
```

## Estrutura do projeto

```
LeoRepo/
├── main.py                     # CLI entry point
├── renda_fixa/
│   ├── __init__.py
│   └── calculadora.py          # Cálculos, tipos e helpers
└── tests/
    └── test_calculadora.py     # 42 testes unitários
```

## Testes

```bash
pip install pytest
pytest tests/ -v
```

## Limitações e notas técnicas

- **Base de dias**: usa 365 dias corridos para todos os indexadores. O mercado usa 252 dias úteis para CDI/Selic; o erro é mínimo (<0,1%) para comparações relativas.
- **TR (Taxa Referencial)**: ignorada no cálculo da Poupança (próxima de zero desde 2017).
- **Custódia do Tesouro Direto**: não inclui a taxa de custódia da B3 (0,20% a.a.).
- **Taxas administrativas**: não consideradas (variam por banco/corretora).
