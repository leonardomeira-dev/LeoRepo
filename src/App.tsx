import { AppLayout } from '@/components/layout/AppLayout'
import { Sidebar } from '@/components/layout/Sidebar'
import { ResultsPanel } from '@/components/layout/ResultsPanel'
import { useCalculator } from '@/hooks/useCalculator'

export function App() {
  const calculator = useCalculator()

  return (
    <AppLayout>
      <Sidebar calculator={calculator} />
      <ResultsPanel
        result={calculator.result}
        investmentMeta={calculator.investmentMeta}
      />
    </AppLayout>
  )
}
