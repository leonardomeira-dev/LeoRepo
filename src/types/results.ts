import type { TaxRegime } from './investment'

export interface CalculationResult {
  grossFinalValue: number
  grossYieldAmount: number
  grossYieldPercent: number

  irAmount: number
  irRate: number
  iofAmount: number
  totalTaxAmount: number

  netFinalValue: number
  netYieldAmount: number
  netYieldPercent: number

  netEffectiveRatePA: number
  realReturnPercent: number
  cdiEquivalentPercent: number

  taxRegime: TaxRegime
  daysElapsed: number
  isIofApplicable: boolean
}
