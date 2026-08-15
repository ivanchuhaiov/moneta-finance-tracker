import client, { setTokens, clearTokens } from './client'

export async function registerUser(payload) {
  // payload: { email, username, firstname, lastname, password }
  const { data } = await client.post('/auth/register', payload)
  return data
}

export async function login(email, password) {
  const { data } = await client.post('/auth/login', { email, password })
  setTokens(data)
  return data
}

export async function fetchMe() {
  const { data } = await client.get('/auth/me')
  return data
}

export function logout() {
  clearTokens()
}
