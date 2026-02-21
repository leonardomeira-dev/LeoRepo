import { useState, useMemo, useCallback } from 'react'
import { DEFAULT_INPUT } from '@/constants/defaults'
import { INVESTMENT_META } from '@/constants/investmentTypes'
import { calculateInvestment } from '@/utils/calculatorEngine'
import type { InvestmentInput, InvestmentType, Indexer } from '@/types/investment'
import type { CalculationResult } from '@/types/results'

export function useCalculator() {
  const [input, setInput] = useState<InvestmentInput>(DEFAULT_INPUT)

  const handleInvestmentTypeChange = useCallback((type: InvestmentType) => {
    const meta = INVESTMENT_META[type]
    const firstAllowed = meta.allowedIndexers[0] as Indexer
    setInput((prev) => ({
      ...prev,
      investmentType: type,
      indexer: firstAllowed,
    }))
  }, [])

  const handleIndexerChange = useCallback((indexer: Indexer) => {
    setInput((prev) => ({ ...prev, indexer }))
  }, [])

  const updateField = useCallback(
    <K extends keyof InvestmentInput>(field: K, value: InvestmentInput[K]) => {
      setInput((prev) => ({ ...prev, [field]: value }))
    },
    []
  )

  const allowedIndexers = useMemo(
    () => INVESTMENT_META[input.investmentType].allowedIndexers,
    [input.investmentType]
  )

  const result: CalculationResult = useMemo(
    () => calculateInvestment(input),
    [input]
  )

  const investmentMeta = INVESTMENT_META[input.investmentType]

  return {
    input,
    result,
    allowedIndexers,
    investmentMeta,
    handleInvestmentTypeChange,
    handleIndexerChange,
    updateField,
  }
}
