import type { CalculationResult } from '@/types/results'
import { formatPercent } from '@/utils/formatters'
import styles from './ResultCard.module.css'
import cdiStyles from './CDIComparisonCard.module.css'

interface Props {
  result: CalculationResult
}

export function CDIComparisonCard({ result }: Props) {
  const pct = result.cdiEquivalentPercent
  const barWidth = Math.min(Math.max(pct, 0), 200)
  const isAbove100 = pct >= 100

  return (
    <div className={`${styles.card} ${styles.neutral}`}>
      <h3 className={styles.title}>Equivalência ao CDI</h3>
      <div className={cdiStyles.main}>
        <div className={cdiStyles.pctValue}>
          <span className={`${cdiStyles.number} ${isAbove100 ? cdiStyles.above : cdiStyles.below}`}>
            {formatPercent(pct)}
          </span>
          <span className={cdiStyles.label}>do CDI líquido</span>
        </div>
        <div className={cdiStyles.barWrapper}>
          <div
            className={`${cdiStyles.bar} ${isAbove100 ? cdiStyles.barAbove : cdiStyles.barBelow}`}
            style={{ width: `${(barWidth / 200) * 100}%` }}
          />
          <div className={cdiStyles.barMarker} />
          <span className={cdiStyles.barLabel100}>100%</span>
        </div>
        <p className={cdiStyles.desc}>
          {isAbove100
            ? `Supera o CDI em ${formatPercent(pct - 100)} (taxa efetiva líquida a.a.)`
            : `Abaixo do CDI em ${formatPercent(100 - pct)} (taxa efetiva líquida a.a.)`}
        </p>
      </div>
    </div>
  )
}
