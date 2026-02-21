import type { InvestmentInput } from '@/types/investment'

export const DEFAULT_INPUT: InvestmentInput = {
  investmentType: 'CDB',
  indexer: 'CDI_PERCENT',
  initialAmount: 10000,
  periodValue: 24,
  periodUnit: 'months',
  investmentRate: 100,
  cdiRate: 13.65,
  selicRate: 13.75,
  ipcaRate: 5.48,
  projectedInflation: 5.48,
}
