import type { CalculationResult } from '@/types/results'
import type { InvestmentMeta } from '@/constants/investmentTypes'
import { SummaryBanner } from '@/components/results/SummaryBanner'
import { GrossResultCard } from '@/components/results/GrossResultCard'
import { TaxCard } from '@/components/results/TaxCard'
import { NetResultCard } from '@/components/results/NetResultCard'
import { EffectiveRateCard } from '@/components/results/EffectiveRateCard'
import { CDIComparisonCard } from '@/components/results/CDIComparisonCard'
import styles from './ResultsPanel.module.css'

interface Props {
  result: CalculationResult
  investmentMeta: InvestmentMeta
}

export function ResultsPanel({ result, investmentMeta }: Props) {
  return (
    <div className={styles.root}>
      <SummaryBanner result={result} />

      <div className={styles.grid}>
        <GrossResultCard result={result} />
        <TaxCard result={result} />
        <NetResultCard result={result} />
        <EffectiveRateCard result={result} />
        <div className={styles.wide}>
          <CDIComparisonCard result={result} />
        </div>
      </div>

      <div className={styles.footer}>
        <p>
          Regime tributário:{' '}
          <strong>
            {investmentMeta.taxRegime === 'ISENTO'
              ? 'Isento de IR para pessoa física'
              : 'IR Regressivo (Lei 11.033/2004)'}
          </strong>
          . IOF: Decreto 6.306/2007.
          Simulação para fins educacionais — consulte um assessor financeiro.
        </p>
      </div>
    </div>
  )
}
