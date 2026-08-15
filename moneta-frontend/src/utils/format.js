import { CURRENCY_SYMBOLS } from '../api/constants'

export function formatMoney(value, currency = 'EUR') {
  const num = Number(value)
  if (Number.isNaN(num)) return '—'
  const symbol = CURRENCY_SYMBOLS[currency] || ''
  const formatted = num.toLocaleString('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return `${formatted} ${symbol}`
}

export function formatPercent(value) {
  const num = Number(value)
  if (Number.isNaN(num)) return '—'
  const sign = num > 0 ? '+' : ''
  return `${sign}${num.toFixed(1)}%`
}

export function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short', year: 'numeric' })
}

export function formatDateTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function toISODate(dateObj) {
  return dateObj.toISOString().slice(0, 10)
}

export function firstDayOfMonth() {
  const d = new Date()
  return new Date(d.getFullYear(), d.getMonth(), 1)
}

export function today() {
  return new Date()
}

function daysAgo(n) {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return d
}

// Shared period presets used by both Dashboard and Analytics so date ranges
// are calculated identically everywhere.
export const PERIOD_PRESETS = [
  { key: 'week', label: 'Неделя', from: () => daysAgo(7) },
  { key: 'month', label: 'Месяц', from: () => firstDayOfMonth() },
  { key: 'quarter', label: 'Квартал', from: () => daysAgo(90) },
]

export function presetRange(key) {
  const preset = PERIOD_PRESETS.find((p) => p.key === key) || PERIOD_PRESETS[1]
  return { date_from: toISODate(preset.from()), date_to: toISODate(today()) }
}
