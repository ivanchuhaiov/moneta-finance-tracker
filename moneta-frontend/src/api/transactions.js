import client from './client'

export async function transfer(payload) {
  // payload: { from_wallet_id, to_wallet_id, amount, description? }
  const { data } = await client.post('/transactions/transfer', payload)
  return data
}

export async function transactionHistory() {
  const { data } = await client.get('/transactions/history')
  return data
}

export async function createCredit(walletId, payload) {
  // payload: { amount, credit_type_id, operation_date }
  const { data } = await client.post(`/wallets/${walletId}/credit`, payload)
  return data
}

export async function createDebit(walletId, payload) {
  // payload: { amount, debit_type_id, operation_date }
  const { data } = await client.post(`/wallets/${walletId}/debit`, payload)
  return data
}
