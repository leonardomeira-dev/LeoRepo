import type { CalculationResult } from '@/types/results'
import { formatBRL, formatPercent } from '@/utils/formatters'
import styles from './ResultCard.module.css'

interface Props {
  result: CalculationResult
}

export function GrossResultCard({ result }: Props) {
  return (
    <div className={`${styles.card} ${styles.info}`}>
      <h3 className={styles.title}>Rendimento Bruto</h3>
      <div className={styles.rows}>
        <div className={styles.row}>
          <span className={styles.rowLabel}>Valor bruto final</span>
          <span className={styles.rowValue}>{formatBRL(result.grossFinalValue)}</span>
        </div>
        <div className={styles.row}>
          <span className={styles.rowLabel}>Rendimento bruto</span>
          <span className={styles.rowValue}>
            +{formatBRL(result.grossYieldAmount)}
          </span>
        </div>
        <div className={`${styles.row} ${styles.highlight}`}>
          <span className={styles.rowLabel}>Rentabilidade bruta</span>
          <span className={styles.rowValue}>+{formatPercent(result.grossYieldPercent)}</span>
        </div>
      </div>
    </div>
  )
}
