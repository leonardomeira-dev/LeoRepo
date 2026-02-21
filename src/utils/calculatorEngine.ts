import type { InvestmentInput } from '@/types/investment'
import type { CalculationResult } from '@/types/results'
import { INVESTMENT_META } from '@/constants/investmentTypes'
import { periodToDays } from '@/utils/dateHelpers'
import {
  calcCDIPercent,
  calcPrefixado,
  calcIPCAPlus,
  calcSELICPercent,
  calcSELICPlus,
} from '@/utils/interestCalculations'
import { calculateTaxes } from '@/utils/taxCalculations'

export function calculateInvestment(input: InvestmentInput): CalculationResult {
  const {
    investmentType,
    indexer,
    initialAmount: pv,
    investmentRate,
    cdiRate,
    selicRate,
    ipcaRate,
    projectedInflation,
    periodValue,
    periodUnit,
  } = input

  const totalDays = periodToDays(periodValue, periodUnit)
  const taxRegime = INVESTMENT_META[investmentType].taxRegime

  // Passo 1: Cálculo do rendimento bruto
  let gross
  switch (indexer) {
    case 'CDI_PERCENT':
      gross = calcCDIPercent(pv, investmentRate, cdiRate, totalDays)
      break
    case 'PREFIXADO':
      gross = calcPrefixado(pv, investmentRate, totalDays)
      break
    case 'IPCA_PLUS':
      gross = calcIPCAPlus(pv, investmentRate, ipcaRate, totalDays)
      break
    case 'SELIC':
      gross = calcSELICPercent(pv, investmentRate, selicRate, totalDays)
      break
    case 'SELIC_PLUS':
      gross = calcSELICPlus(pv, investmentRate, selicRate, totalDays)
      break
    default:
      gross = calcCDIPercent(pv, investmentRate, cdiRate, totalDays)
  }

  // Passo 2: Tributação (IOF antes do IR — ordem legal)
  const { iofAmount, irAmount, irRate, netYield } = calculateTaxes(
    gross.grossYieldAmount,
    totalDays,
    taxRegime
  )

  const netFinalValue = pv + netYield
  const netYieldPercent = (netFinalValue / pv - 1) * 100

  // Passo 3: Métricas derivadas
  // Taxa efetiva líquida a.a. (convenção 252 du)
  const netEffectiveRatePA =
    gross.businessDays > 0
      ? (Math.pow(netFinalValue / pv, 252 / gross.businessDays) - 1) * 100
      : 0

  // Retorno real = (1 + nominal) / (1 + inflação_período) - 1
  const inflationFactor = Math.pow(1 + projectedInflation / 100, totalDays / 365)
  const realReturnPercent = (netFinalValue / pv / inflationFactor - 1) * 100

  // % do CDI equivalente = taxa efetiva líquida / CDI a.a.
  const cdiEquivalentPercent = cdiRate > 0 ? (netEffectiveRatePA / cdiRate) * 100 : 0

  return {
    grossFinalValue: gross.grossFinalValue,
    grossYieldAmount: gross.grossYieldAmount,
    grossYieldPercent: gross.grossYieldPercent,
    irAmount,
    irRate,
    iofAmount,
    totalTaxAmount: irAmount + iofAmount,
    netFinalValue,
    netYieldAmount: netYield,
    netYieldPercent,
    netEffectiveRatePA,
    realReturnPercent,
    cdiEquivalentPercent,
    taxRegime,
    daysElapsed: totalDays,
    isIofApplicable: totalDays < 30,
  }
}
