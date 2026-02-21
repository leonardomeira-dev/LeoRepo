import type { InvestmentInput } from '@/types/investment'
import styles from './MarketRatesPanel.module.css'
import fieldStyles from './FormField.module.css'

interface Props {
  input: InvestmentInput
  updateField: <K extends keyof InvestmentInput>(field: K, value: InvestmentInput[K]) => void
}

interface RateFieldProps {
  label: string
  value: number
  field: keyof InvestmentInput
  onChange: (field: keyof InvestmentInput, value: number) => void
  hint?: string
}

function RateField({ label, value, field, onChange, hint }: RateFieldProps) {
  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const v = parseFloat(e.target.value)
    onChange(field, isNaN(v) ? 0 : v)
  }

  return (
    <div className={fieldStyles.field}>
      <label className={fieldStyles.label}>
        {label}
        {hint && <span className={styles.hint}> ({hint})</span>}
      </label>
      <div className={fieldStyles.inputWrapper}>
        <input
          className={fieldStyles.input}
          type="number"
          step="0.01"
          min={0}
          max={100}
          value={value}
          onChange={handleChange}
        />
        <span className={fieldStyles.suffix}>% a.a.</span>
      </div>
    </div>
  )
}

export function MarketRatesPanel({ input, updateField }: Props) {
  function handleChange(field: keyof InvestmentInput, value: number) {
    updateField(field, value as InvestmentInput[typeof field])
  }

  return (
    <div className={styles.root}>
      <div className={styles.header}>
        <span className={styles.title}>Taxas de Referência</span>
        <span className={styles.info}>Ajuste conforme cenário esperado</span>
      </div>
      <div className={styles.grid}>
        <RateField label="CDI" value={input.cdiRate} field="cdiRate" onChange={handleChange} hint="ao ano" />
        <RateField label="SELIC" value={input.selicRate} field="selicRate" onChange={handleChange} hint="ao ano" />
        <RateField label="IPCA" value={input.ipcaRate} field="ipcaRate" onChange={handleChange} hint="projetado" />
        <RateField
          label="Inflação projetada"
          value={input.projectedInflation}
          field="projectedInflation"
          onChange={handleChange}
          hint="retorno real"
        />
      </div>
    </div>
  )
}
