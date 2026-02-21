export function periodToDays(value: number, unit: 'months' | 'days'): number {
  if (unit === 'days') return Math.max(1, Math.floor(value))
  return Math.max(1, Math.floor(value * 30))
}

// Estimativa de dias úteis — convenção de mercado brasileiro (252 du/ano)
export function businessDayFraction(calendarDays: number): number {
  return calendarDays * (252 / 365)
}

export function daysToYearsBI(businessDays: number): number {
  return businessDays / 252
}
