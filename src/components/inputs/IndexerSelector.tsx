import type { Indexer } from '@/types/investment'
import styles from './IndexerSelector.module.css'

const INDEXER_LABELS: Record<Indexer, string> = {
  CDI_PERCENT: '% do CDI',
  PREFIXADO: 'Prefixado',
  IPCA_PLUS: 'IPCA+',
  SELIC: '% da SELIC',
  SELIC_PLUS: 'SELIC+',
}

interface Props {
  value: Indexer
  allowed: Indexer[]
  onChange: (indexer: Indexer) => void
}

export function IndexerSelector({ value, allowed, onChange }: Props) {
  return (
    <div className={styles.root}>
      {allowed.map((indexer) => (
        <button
          key={indexer}
          className={`${styles.btn} ${value === indexer ? styles.active : ''}`}
          onClick={() => onChange(indexer)}
        >
          {INDEXER_LABELS[indexer]}
        </button>
      ))}
    </div>
  )
}
