import type { PeriodUnit } from '@/types/investment'
import styles from './FormField.module.css'

interface Props {
  value: number
  unit: PeriodUnit
  onValueChange: (value: number) => void
  onUnitChange: (unit: PeriodUnit) => void
}

export function PeriodInput({ value, unit, onValueChange, onUnitChange }: Props) {
  function handleToggle() {
    if (unit === 'months') {
      onUnitChange('days')
      onValueChange(Math.round(value * 30))
    } else {
      onUnitChange('months')
      onValueChange(Math.max(1, Math.round(value / 30)))
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const v = parseInt(e.target.value, 10)
    onValueChange(isNaN(v) || v < 1 ? 1 : v)
  }

  return (
    <div className={styles.field}>
      <label className={styles.label}>Prazo</label>
      <div className={styles.inputWrapper}>
        <input
          className={styles.input}
          type="number"
          min={1}
          value={value}
          onChange={handleChange}
        />
        <button
          className={styles.toggleBtn}
          onClick={handleToggle}
          title="Alternar entre meses e dias"
          type="button"
        >
          {unit === 'months' ? 'MESES' : 'DIAS'}
        </button>
      </div>
    </div>
  )
}
