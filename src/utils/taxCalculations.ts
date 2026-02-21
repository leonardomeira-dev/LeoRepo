import { IR_TABLE, IOF_DAILY_RATES } from '@/constants/taxRules'
import type { TaxRegime } from '@/types/investment'

export function getIRRate(days: number, taxRegime: TaxRegime): number {
  if (taxRegime === 'ISENTO') return 0
  const bracket = IR_TABLE.find((b) => days <= b.maxDays)
  return bracket?.rate ?? 0.15
}

export function getIOFRate(days: number): number {
  if (days >= 30) return 0
  if (days <= 0) return 1
  return IOF_DAILY_RATES[Math.min(days, 29)] ?? 0
}

export interface TaxResult {
  iofAmount: number
  irAmount: number
  irRate: number
  netYield: number
}

export function calculateTaxes(
  grossYield: number,
  days: number,
  taxRegime: TaxRegime
): TaxResult {
  const iofRate = getIOFRate(days)
  const iofAmount = grossYield * iofRate
  const yieldAfterIOF = grossYield - iofAmount
  const irRate = getIRRate(days, taxRegime)
  const irAmount = yieldAfterIOF * irRate
  const netYield = yieldAfterIOF - irAmount
  return { iofAmount, irAmount, irRate, netYield }
}
