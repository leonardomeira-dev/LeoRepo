import type { InvestmentType } from '@/types/investment'
import { INVESTMENT_META, INVESTMENT_GROUPS } from '@/constants/investmentTypes'
import styles from './InvestmentTypeSelector.module.css'

interface Props {
  value: InvestmentType
  onChange: (type: InvestmentType) => void
}

export function InvestmentTypeSelector({ value, onChange }: Props) {
  return (
    <div className={styles.root}>
      {Object.entries(INVESTMENT_GROUPS).map(([groupKey, group]) => (
        <div key={groupKey} className={styles.group}>
          <span className={styles.groupLabel}>{group.label}</span>
          <div className={styles.buttons}>
            {group.types.map((type) => (
              <button
                key={type}
                className={`${styles.btn} ${value === type ? styles.active : ''} ${
                  INVESTMENT_META[type].taxRegime === 'ISENTO' ? styles.isento : ''
                }`}
                onClick={() => onChange(type)}
                title={INVESTMENT_META[type].description}
              >
                {INVESTMENT_META[type].shortLabel}
                {INVESTMENT_META[type].taxRegime === 'ISENTO' && (
                  <span className={styles.badge}>IR</span>
                )}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
