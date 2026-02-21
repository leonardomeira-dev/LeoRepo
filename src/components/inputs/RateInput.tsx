import type { Indexer } from '@/types/investment'
import styles from './FormField.module.css'

const RATE_CONFIG: Record<Indexer, { label: string; suffix: string; placeholder: string }> = {
  CDI_PERCENT: { label: 'Taxa do investimento', suffix: '% CDI', placeholder: '100,00' },
  PREFIXADO: { label: 'Taxa prefixada a.a.', suffix: '% a.a.', placeholder: '12,00' },
  IPCA_PLUS: { label: 'Spread sobre IPCA', suffix: '% a.a.', placeholder: '6,00' },
  SELIC: { label: 'Taxa do investimento', suffix: '% SELIC', placeholder: '100,00' },
  SELIC_PLUS: { label: 'Spread sobre SELIC', suffix: '% a.a.', placeholder: '0,07' },
}

interface Props {
  value: number
  indexer: Indexer
  onChange: (value: number) => void
}

export function RateInput({ value, indexer, onChange }: Props) {
  const config = RATE_CONFIG[indexer]

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const v = parseFloat(e.target.value.replace(',', '.'))
    onChange(isNaN(v) ? 0 : v)
  }

  return (
    <div className={styles.field}>
      <label className={styles.label}>{config.label}</label>
      <div className={styles.inputWrapper}>
        <input
          className={styles.input}
          type="number"
          step="0.01"
          min={0}
          value={value}
          onChange={handleChange}
          placeholder={config.placeholder}
        />
        <span className={styles.suffix}>{config.suffix}</span>
      </div>
    </div>
  )
}
