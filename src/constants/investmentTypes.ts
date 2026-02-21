import type { InvestmentType, TaxRegime, Indexer } from '@/types/investment'

export interface InvestmentMeta {
  label: string
  shortLabel: string
  taxRegime: TaxRegime
  allowedIndexers: Indexer[]
  description: string
  group: 'bancario' | 'tesouro' | 'credito_privado'
}

export const INVESTMENT_META: Record<InvestmentType, InvestmentMeta> = {
  CDB: {
    label: 'CDB',
    shortLabel: 'CDB',
    taxRegime: 'IR_REGRESSIVO',
    allowedIndexers: ['CDI_PERCENT', 'PREFIXADO', 'IPCA_PLUS'],
    description: 'Certificado de Depósito Bancário. Coberto pelo FGC até R$ 250.000.',
    group: 'bancario',
  },
  LCI: {
    label: 'LCI',
    shortLabel: 'LCI',
    taxRegime: 'ISENTO',
    allowedIndexers: ['CDI_PERCENT', 'PREFIXADO', 'IPCA_PLUS'],
    description: 'Letra de Crédito Imobiliário. Isento de IR para pessoa física.',
    group: 'bancario',
  },
  LCA: {
    label: 'LCA',
    shortLabel: 'LCA',
    taxRegime: 'ISENTO',
    allowedIndexers: ['CDI_PERCENT', 'PREFIXADO', 'IPCA_PLUS'],
    description: 'Letra de Crédito do Agronegócio. Isento de IR para pessoa física.',
    group: 'bancario',
  },
  TESOURO_SELIC: {
    label: 'Tesouro SELIC',
    shortLabel: 'T. SELIC',
    taxRegime: 'IR_REGRESSIVO',
    allowedIndexers: ['SELIC', 'SELIC_PLUS'],
    description: 'Título público federal indexado à taxa SELIC.',
    group: 'tesouro',
  },
  TESOURO_IPCA: {
    label: 'Tesouro IPCA+',
    shortLabel: 'T. IPCA+',
    taxRegime: 'IR_REGRESSIVO',
    allowedIndexers: ['IPCA_PLUS'],
    description: 'Título público federal. Rentabilidade: IPCA + taxa prefixada.',
    group: 'tesouro',
  },
  TESOURO_PREFIXADO: {
    label: 'Tesouro Prefixado',
    shortLabel: 'T. Pré',
    taxRegime: 'IR_REGRESSIVO',
    allowedIndexers: ['PREFIXADO'],
    description: 'Título público federal com taxa fixa definida na compra.',
    group: 'tesouro',
  },
  CRI: {
    label: 'CRI',
    shortLabel: 'CRI',
    taxRegime: 'ISENTO',
    allowedIndexers: ['CDI_PERCENT', 'PREFIXADO', 'IPCA_PLUS'],
    description: 'Certificado de Recebíveis Imobiliários. Isento de IR para PF.',
    group: 'credito_privado',
  },
  CRA: {
    label: 'CRA',
    shortLabel: 'CRA',
    taxRegime: 'ISENTO',
    allowedIndexers: ['CDI_PERCENT', 'PREFIXADO', 'IPCA_PLUS'],
    description: 'Certificado de Recebíveis do Agronegócio. Isento de IR para PF.',
    group: 'credito_privado',
  },
  DEBENTURE_INCENTIVADA: {
    label: 'Debênture Incentivada',
    shortLabel: 'Debênture',
    taxRegime: 'ISENTO',
    allowedIndexers: ['CDI_PERCENT', 'PREFIXADO', 'IPCA_PLUS'],
    description: 'Debênture incentivada (Lei 12.431/2011). Isenta de IR para PF.',
    group: 'credito_privado',
  },
}

export const INVESTMENT_GROUPS: Record<string, { label: string; types: InvestmentType[] }> = {
  bancario: {
    label: 'Bancário',
    types: ['CDB', 'LCI', 'LCA'],
  },
  tesouro: {
    label: 'Tesouro Direto',
    types: ['TESOURO_SELIC', 'TESOURO_IPCA', 'TESOURO_PREFIXADO'],
  },
  credito_privado: {
    label: 'Crédito Privado',
    types: ['CRI', 'CRA', 'DEBENTURE_INCENTIVADA'],
  },
}
