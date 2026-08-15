import client from './client'

export async function listWalletTypes() {
  const { data } = await client.get('/wallet-types')
  return data
}

export async function createWalletType(payload) {
  const { data } = await client.post('/wallet-types', payload)
  return data
}

export async function listCreditTypes() {
  const { data } = await client.get('/credit-types')
  return data
}

export async function createCreditType(payload) {
  const { data } = await client.post('/credit-types', payload)
  return data
}

export async function listDebitTypes() {
  const { data } = await client.get('/debit-types')
  return data
}

export async function createDebitType(payload) {
  const { data } = await client.post('/debit-types', payload)
  return data
}
