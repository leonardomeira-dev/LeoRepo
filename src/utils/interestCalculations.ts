import { businessDayFraction } from '@/utils/dateHelpers'

export interface GrossResult {
  grossFinalValue: number
  grossYieldAmount: number
  grossYieldPercent: number
  businessDays: number
}

// % CDI: daily = 1 + (rate%/100) × (cdiDaily - 1)
// Convenção: percentual do CDI (não spread)
export function calcCDIPercent(
  pv: number,
  ratePercent: number, // e.g. 110 = 110% do CDI
  cdiAA: number,
  totalDays: number
): GrossResult {
  const du = businessDayFraction(totalDays)
  const cdiDaily = Math.pow(1 + cdiAA / 100, 1 / 252)
  const adjustedDaily = 1 + (ratePercent / 100) * (cdiDaily - 1)
  const grossFinalValue = pv * Math.pow(adjustedDaily, du)
  const grossYieldAmount = grossFinalValue - pv
  const grossYieldPercent = (grossFinalValue / pv - 1) * 100
  return { grossFinalValue, grossYieldAmount, grossYieldPercent, businessDays: du }
}

// Prefixado: taxa fixa ao ano, capitalização 252 du
export function calcPrefixado(
  pv: number,
  taxaAA: number, // e.g. 12.5 = 12,5% a.a.
  totalDays: number
): GrossResult {
  const du = businessDayFraction(totalDays)
  const dailyFactor = Math.pow(1 + taxaAA / 100, 1 / 252)
  const grossFinalValue = pv * Math.pow(dailyFactor, du)
  const grossYieldAmount = grossFinalValue - pv
  const grossYieldPercent = (grossFinalValue / pv - 1) * 100
  return { grossFinalValue, grossYieldAmount, grossYieldPercent, businessDays: du }
}

// IPCA+: componente IPCA (mensal) × componente spread (252 du)
// FV = PV × (1+IPCA_aa)^(meses/12) × (1+spread_aa)^(du/252)
export function calcIPCAPlus(
  pv: number,
  spreadAA: number, // e.g. 6.0 = IPCA + 6% a.a.
  ipcaAA: number,
  totalDays: number
): GrossResult {
  const du = businessDayFraction(totalDays)
  const months = totalDays / 30 // convenção DC/30
  const ipcaFactor = Math.pow(1 + ipcaAA / 100, months / 12)
  const spreadFactor = Math.pow(1 + spreadAA / 100, du / 252)
  const grossFinalValue = pv * ipcaFactor * spreadFactor
  const grossYieldAmount = grossFinalValue - pv
  const grossYieldPercent = (grossFinalValue / pv - 1) * 100
  return { grossFinalValue, grossYieldAmount, grossYieldPercent, businessDays: du }
}

// SELIC (% da SELIC): mesma convenção do CDI%
export function calcSELICPercent(
  pv: number,
  ratePercent: number, // e.g. 100 = 100% da SELIC
  selicAA: number,
  totalDays: number
): GrossResult {
  const du = businessDayFraction(totalDays)
  const selicDaily = Math.pow(1 + selicAA / 100, 1 / 252)
  const adjustedDaily = 1 + (ratePercent / 100) * (selicDaily - 1)
  const grossFinalValue = pv * Math.pow(adjustedDaily, du)
  const grossYieldAmount = grossFinalValue - pv
  const grossYieldPercent = (grossFinalValue / pv - 1) * 100
  return { grossFinalValue, grossYieldAmount, grossYieldPercent, businessDays: du }
}

// SELIC+ (SELIC + spread fixo em % a.a.)
export function calcSELICPlus(
  pv: number,
  spreadAA: number, // e.g. 0.07 = SELIC + 0,07% a.a.
  selicAA: number,
  totalDays: number
): GrossResult {
  const du = businessDayFraction(totalDays)
  const selicDaily = Math.pow(1 + selicAA / 100, 1 / 252)
  const spreadDaily = Math.pow(1 + spreadAA / 100, 1 / 252)
  const combinedDaily = selicDaily * spreadDaily
  const grossFinalValue = pv * Math.pow(combinedDaily, du)
  const grossYieldAmount = grossFinalValue - pv
  const grossYieldPercent = (grossFinalValue / pv - 1) * 100
  return { grossFinalValue, grossYieldAmount, grossYieldPercent, businessDays: du }
}
