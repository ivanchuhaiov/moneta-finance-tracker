import { createContext, useContext, useState } from 'react'
import { CURRENCY_CODES } from '../api/constants'

const CurrencyContext = createContext(null)

export function CurrencyProvider({ children }) {
  const [currency, setCurrency] = useState(CURRENCY_CODES[0])
  return (
    <CurrencyContext.Provider value={{ currency, setCurrency }}>
      {children}
    </CurrencyContext.Provider>
  )
}

export function useCurrency() {
  const ctx = useContext(CurrencyContext)
  if (!ctx) throw new Error('useCurrency must be used within CurrencyProvider')
  return ctx
}
