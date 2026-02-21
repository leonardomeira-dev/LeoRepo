export type InvestmentType =
  | 'CDB'
  | 'LCI'
  | 'LCA'
  | 'TESOURO_SELIC'
  | 'TESOURO_IPCA'
  | 'TESOURO_PREFIXADO'
  | 'CRI'
  | 'CRA'
  | 'DEBENTURE_INCENTIVADA'

export type Indexer =
  | 'CDI_PERCENT'
  | 'PREFIXADO'
  | 'IPCA_PLUS'
  | 'SELIC'
  | 'SELIC_PLUS'

export type PeriodUnit = 'months' | 'days'

export type TaxRegime = 'IR_REGRESSIVO' | 'ISENTO'

export interface InvestmentInput {
  investmentType: InvestmentType
  indexer: Indexer
  initialAmount: number
  periodValue: number
  periodUnit: PeriodUnit
  investmentRate: number
  cdiRate: number
  selicRate: number
  ipcaRate: number
  projectedInflation: number
}
