import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { login as apiLogin, registerUser, fetchMe, logout as apiLogout } from '../api/auth'
import { clearTokens } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('moneta_access_token')
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const me = await fetchMe()
      setUser(me)
    } catch {
      clearTokens()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  async function login(email, password) {
    await apiLogin(email, password)
    const me = await fetchMe()
    setUser(me)
    return me
  }

  async function register(payload) {
    await registerUser(payload)
    return login(payload.email, payload.password)
  }

  function logout() {
    apiLogout()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
