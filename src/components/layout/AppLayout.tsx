import type { ReactNode } from 'react'
import styles from './AppLayout.module.css'

interface Props {
  children: ReactNode
}

export function AppLayout({ children }: Props) {
  return (
    <div className={styles.root}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.logo}>
            <span className={styles.logoIcon}>₿</span>
            <span className={styles.logoText}>Calculadora Renda Fixa</span>
          </div>
          <span className={styles.subtitle}>Simulação completa com IR e IOF</span>
        </div>
      </header>
      <main className={styles.main}>
        {children}
      </main>
    </div>
  )
}
