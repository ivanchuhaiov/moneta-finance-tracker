import client from './client'

export async function getDashboard(currency, date_from, date_to) {
  const { data } = await client.get('/api/dashboard', { params: { currency, date_from, date_to } })
  return data
}

export async function getExpensesByCategory({ date_from, date_to, currency }) {
  const { data } = await client.get('/api/analytics/expenses', { params: { date_from, date_to, currency } })
  return data
}

export async function getIncomeByCategory({ date_from, date_to, currency }) {
  const { data } = await client.get('/api/analytics/income', { params: { date_from, date_to, currency } })
  return data
}

export async function getSummary(currency, date_from, date_to) {
  const { data } = await client.get('/api/analytics/summary', { params: { currency, date_from, date_to } })
  return data
}

export async function getCashflow(currency, date_from, date_to) {
  const { data } = await client.get('/api/analytics/cashflow', { params: { currency, date_from, date_to } })
  return data
}

export async function getSavingsRate(currency, date_from, date_to) {
  const { data } = await client.get('/api/analytics/savings-rate', { params: { currency, date_from, date_to } })
  return data
}
