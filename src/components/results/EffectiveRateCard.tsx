import type { CalculationResult } from '@/types/results'
import { formatPercent } from '@/utils/formatters'
import styles from './ResultCard.module.css'
import rateStyles from './EffectiveRateCard.module.css'

interface Props {
  result: CalculationResult
}

export function EffectiveRateCard({ result }: Props) {
  const realIsPositive = result.realReturnPercent >= 0

  return (
    <div className={`${styles.card} ${styles.neutral}`}>
      <h3 className={styles.title}>Taxas Efetivas</h3>
      <div className={styles.rows}>
        <div className={styles.row}>
          <span className={styles.rowLabel}>Taxa efetiva líquida a.a.</span>
          <span className={styles.rowValue}>
            {formatPercent(result.netEffectiveRatePA)}
          </span>
        </div>
        <div className={`${styles.row} ${styles.highlight}`}>
          <span className={styles.rowLabel}>Retorno real (após inflação)</span>
          <span
            className={`${styles.rowValue} ${
              realIsPositive ? rateStyles.positive : rateStyles.negative
            }`}
          >
            {realIsPositive ? '+' : ''}{formatPercent(result.realReturnPercent)}
          </span>
        </div>
      </div>
    </div>
  )
}
