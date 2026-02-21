import { InvestmentTypeSelector } from '@/components/inputs/InvestmentTypeSelector'
import { IndexerSelector } from '@/components/inputs/IndexerSelector'
import { AmountInput } from '@/components/inputs/AmountInput'
import { PeriodInput } from '@/components/inputs/PeriodInput'
import { RateInput } from '@/components/inputs/RateInput'
import { MarketRatesPanel } from '@/components/inputs/MarketRatesPanel'
import type { useCalculator } from '@/hooks/useCalculator'
import styles from './Sidebar.module.css'

type CalculatorContext = ReturnType<typeof useCalculator>

interface Props {
  calculator: CalculatorContext
}

export function Sidebar({ calculator }: Props) {
  const { input, allowedIndexers, handleInvestmentTypeChange, handleIndexerChange, updateField } =
    calculator

  return (
    <aside className={styles.root}>
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Tipo de Investimento</h2>
        <InvestmentTypeSelector
          value={input.investmentType}
          onChange={handleInvestmentTypeChange}
        />
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Indexador</h2>
        <IndexerSelector
          value={input.indexer}
          allowed={allowedIndexers}
          onChange={handleIndexerChange}
        />
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Dados do Investimento</h2>
        <div className={styles.fields}>
          <AmountInput
            value={input.initialAmount}
            onChange={(v) => updateField('initialAmount', v)}
          />
          <PeriodInput
            value={input.periodValue}
            unit={input.periodUnit}
            onValueChange={(v) => updateField('periodValue', v)}
            onUnitChange={(u) => updateField('periodUnit', u)}
          />
          <RateInput
            value={input.investmentRate}
            indexer={input.indexer}
            onChange={(v) => updateField('investmentRate', v)}
          />
        </div>
      </section>

      <section className={styles.section}>
        <MarketRatesPanel input={input} updateField={updateField} />
      </section>

      {calculator.investmentMeta.taxRegime === 'ISENTO' && (
        <div className={styles.isentoAlert}>
          <span className={styles.isentoIcon}>★</span>
          <span>
            <strong>Isento de IR</strong> para pessoa física —{' '}
            {calculator.investmentMeta.description}
          </span>
        </div>
      )}
    </aside>
  )
}
