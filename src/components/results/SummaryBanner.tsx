import type { CalculationResult } from '@/types/results'
import { formatBRL, formatPercent } from '@/utils/formatters'
import styles from './SummaryBanner.module.css'

interface Props {
  result: CalculationResult
}

export function SummaryBanner({ result }: Props) {
  const isPositive = result.netYieldAmount >= 0

  return (
    <div className={`${styles.root} ${isPositive ? styles.positive : styles.negative}`}>
      <div className={styles.left}>
        <span className={styles.label}>Valor líquido final</span>
        <span className={styles.value}>{formatBRL(result.netFinalValue)}</span>
        <span className={styles.yield}>
          {isPositive ? '+' : ''}{formatBRL(result.netYieldAmount)} (
          {isPositive ? '+' : ''}{formatPercent(result.netYieldPercent)})
        </span>
      </div>
      <div className={styles.right}>
        {result.taxRegime === 'ISENTO' ? (
          <div className={styles.badge} data-variant="isento">
            Isento de IR
          </div>
        ) : (
          <div className={styles.taxSummary}>
            <span className={styles.taxLabel}>Impostos</span>
            <span className={styles.taxValue}>-{formatBRL(result.totalTaxAmount)}</span>
          </div>
        )}
        <div className={styles.days}>
          {result.daysElapsed} {result.daysElapsed === 1 ? 'dia' : 'dias'} de aplicação
        </div>
      </div>
    </div>
  )
}
