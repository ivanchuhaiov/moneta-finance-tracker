import client from './client'

export async function listWallets() {
  const { data } = await client.get('/wallets')
  return data
}

export async function createWallet(payload) {
  // payload: { name, wallet_type_id, currency_id, balance }
  const { data } = await client.post('/wallets', payload)
  return data
}

export async function getWallet(walletId) {
  const { data } = await client.get(`/wallets/${walletId}`)
  return data
}

export async function updateWallet(walletId, payload) {
  // payload: { name?, is_active? }
  const { data } = await client.patch(`/wallets/${walletId}`, payload)
  return data
}

export async function deactivateWallet(walletId) {
  const { data } = await client.delete(`/wallets/${walletId}`)
  return data
}

export async function listCurrencies() {
  const { data } = await client.get('/wallets/currencies')
  return data
}

export async function getWalletBalance(walletId) {
  const { data } = await client.get(`/wallets/${walletId}/balance`)
  return data
}

export async function getWalletOperations(walletId) {
  const { data } = await client.get(`/wallets/${walletId}/operations`)
  return data
}

export async function getTotalBalance(currency) {
  const { data } = await client.get('/wallets/summary/total-balance', { params: { currency } })
  return data
}
