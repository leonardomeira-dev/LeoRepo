import type { CalculationResult } from '@/types/results'
import { formatBRL, formatPercent } from '@/utils/formatters'
import styles from './ResultCard.module.css'

interface Props {
  result: CalculationResult
}

const IR_BRACKET_LABELS: Record<number, string> = {
  0.225: '≤ 180 dias',
  0.2: '181 a 360 dias',
  0.175: '361 a 720 dias',
  0.15: '> 720 dias',
}

export function TaxCard({ result }: Props) {
  const isIsento = result.taxRegime === 'ISENTO'

  return (
    <div className={`${styles.card} ${isIsento ? styles.success : styles.danger}`}>
      <h3 className={styles.title}>Tributação</h3>

      {isIsento ? (
        <div className={styles.rows}>
          <div className={styles.row}>
            <span className={styles.rowLabel}>Regime tributário</span>
            <span className={`${styles.badge} ${styles.isento}`}>ISENTO DE IR</span>
          </div>
          <div className={styles.row}>
            <span className={styles.rowLabel}>IR</span>
            <span className={styles.rowValue}>{formatBRL(0)}</span>
          </div>
          <div className={styles.row}>
            <span className={styles.rowLabel}>IOF</span>
            <span className={styles.rowValue}>
              {result.isIofApplicable ? formatBRL(result.iofAmount) : formatBRL(0)}
            </span>
          </div>
          <div className={`${styles.row} ${styles.highlight}`}>
            <span className={styles.rowLabel}>Total de impostos</span>
            <span className={styles.rowValue}>{formatBRL(result.iofAmount)}</span>
          </div>
        </div>
      ) : (
        <div className={styles.rows}>
          <div className={styles.row}>
            <span className={styles.rowLabel}>Alíquota IR</span>
            <span className={`${styles.badge} ${styles.ir}`}>
              {formatPercent(result.irRate * 100, 1)} — {IR_BRACKET_LABELS[result.irRate] ?? ''}
            </span>
          </div>
          <div className={styles.row}>
            <span className={styles.rowLabel}>IR a pagar</span>
            <span className={styles.rowValue}>-{formatBRL(result.irAmount)}</span>
          </div>
          {result.isIofApplicable && (
            <div className={styles.row}>
              <span className={styles.rowLabel}>
                IOF{' '}
                <span className={`${styles.badge} ${styles.iof}`}>
                  {result.daysElapsed}d
                </span>
              </span>
              <span className={styles.rowValue}>-{formatBRL(result.iofAmount)}</span>
            </div>
          )}
          <div className={`${styles.row} ${styles.highlight}`}>
            <span className={styles.rowLabel}>Total de impostos</span>
            <span className={styles.rowValue}>-{formatBRL(result.totalTaxAmount)}</span>
          </div>
        </div>
      )}
    </div>
  )
}
