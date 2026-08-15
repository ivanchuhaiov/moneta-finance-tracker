import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const client = axios.create({
  baseURL: BASE_URL,
})

function getTokens() {
  return {
    access: localStorage.getItem('moneta_access_token'),
    refresh: localStorage.getItem('moneta_refresh_token'),
  }
}

export function setTokens({ access_token, refresh_token }) {
  if (access_token) localStorage.setItem('moneta_access_token', access_token)
  if (refresh_token) localStorage.setItem('moneta_refresh_token', refresh_token)
}

export function clearTokens() {
  localStorage.removeItem('moneta_access_token')
  localStorage.removeItem('moneta_refresh_token')
}

client.interceptors.request.use((config) => {
  const { access } = getTokens()
  if (access) config.headers.Authorization = `Bearer ${access}`
  return config
})

// Queue so parallel 401s don't trigger multiple refresh calls
let isRefreshing = false
let queue = []

function flushQueue(error, token) {
  queue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  queue = []
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const status = error.response ? error.response.status : null

    if (status !== 401 || original._retry || original.url?.includes('/auth/refresh') || original.url?.includes('/auth/login')) {
      return Promise.reject(error)
    }

    const { refresh } = getTokens()
    if (!refresh) {
      clearTokens()
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        queue.push({ resolve, reject })
      }).then((token) => {
        original.headers.Authorization = `Bearer ${token}`
        original._retry = true
        return client(original)
      })
    }

    original._retry = true
    isRefreshing = true

    try {
      const { data } = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refresh })
      setTokens(data)
      flushQueue(null, data.access_token)
      original.headers.Authorization = `Bearer ${data.access_token}`
      return client(original)
    } catch (refreshError) {
      flushQueue(refreshError, null)
      clearTokens()
      window.location.href = '/login'
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default client
