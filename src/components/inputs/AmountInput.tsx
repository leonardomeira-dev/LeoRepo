import { useState } from 'react'
import { formatBRL, parseBRL } from '@/utils/formatters'
import styles from './FormField.module.css'

interface Props {
  value: number
  onChange: (value: number) => void
}

export function AmountInput({ value, onChange }: Props) {
  const [focused, setFocused] = useState(false)
  const [raw, setRaw] = useState('')

  function handleFocus() {
    setFocused(true)
    setRaw(value > 0 ? value.toFixed(2).replace('.', ',') : '')
  }

  function handleBlur() {
    setFocused(false)
    const parsed = parseBRL(raw)
    onChange(parsed > 0 ? parsed : 0)
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    // Allow only digits, comma, dot
    const cleaned = e.target.value.replace(/[^\d,.]/g, '')
    setRaw(cleaned)
  }

  return (
    <div className={styles.field}>
      <label className={styles.label}>Valor investido</label>
      <div className={styles.inputWrapper}>
        <span className={styles.prefix}>R$</span>
        <input
          className={styles.input}
          type="text"
          inputMode="decimal"
          value={focused ? raw : formatBRL(value).replace('R$\u00a0', '').replace('R$ ', '')}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onChange={handleChange}
          placeholder="0,00"
        />
      </div>
    </div>
  )
}
