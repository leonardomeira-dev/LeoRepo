// Tabela IR Regressivo — Lei 11.033/2004
export const IR_TABLE: Array<{ maxDays: number; rate: number }> = [
  { maxDays: 180, rate: 0.225 },
  { maxDays: 360, rate: 0.200 },
  { maxDays: 720, rate: 0.175 },
  { maxDays: Infinity, rate: 0.150 },
]

// Tabela IOF Regressivo — Decreto 6.306/2007, Art. 15
// Índice = dia (1-based); valor = alíquota como decimal
// Dia 1 = 96%, Dia 29 = 3%, Dia 30+ = 0%
export const IOF_DAILY_RATES: number[] = [
  0,     // índice 0 não usado
  0.96, 0.93, 0.90, 0.86, 0.83, 0.80, 0.76, 0.73, 0.70, 0.66, // dias 1–10
  0.63, 0.60, 0.56, 0.53, 0.50, 0.46, 0.43, 0.40, 0.36, 0.33, // dias 11–20
  0.30, 0.26, 0.23, 0.20, 0.16, 0.13, 0.10, 0.06, 0.03,        // dias 21–29
]
