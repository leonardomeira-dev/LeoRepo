import type { CalculationResult } from '@/types/results'
import { formatBRL, formatPercent } from '@/utils/formatters'
import styles from './ResultCard.module.css'

interface Props {
  result: CalculationResult
}

export function NetResultCard({ result }: Props) {
  return (
    <div className={`${styles.card} ${styles.success}`}>
      <h3 className={styles.title}>Resultado Líquido</h3>
      <div className={styles.rows}>
        <div className={styles.row}>
          <span className={styles.rowLabel}>Valor líquido final</span>
          <span className={styles.rowValue}>{formatBRL(result.netFinalValue)}</span>
        </div>
        <div className={styles.row}>
          <span className={styles.rowLabel}>Rendimento líquido</span>
          <span className={styles.rowValue}>+{formatBRL(result.netYieldAmount)}</span>
        </div>
        <div className={`${styles.row} ${styles.highlight}`}>
          <span className={styles.rowLabel}>Rentabilidade líquida</span>
          <span className={styles.rowValue}>+{formatPercent(result.netYieldPercent)}</span>
        </div>
      </div>
    </div>
  )
}
