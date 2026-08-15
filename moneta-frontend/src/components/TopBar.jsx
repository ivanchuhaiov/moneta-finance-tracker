import { useCurrency } from '../context/CurrencyContext'
import { CURRENCY_CODES } from '../api/constants'

export default function TopBar({ title, subtitle, actions }) {
  const { currency, setCurrency } = useCurrency()

  return (
    <header className="topbar">
      <div>
        <div className="topbar-title">{title}</div>
        {subtitle && <div className="topbar-sub">{subtitle}</div>}
      </div>
      <div className="topbar-actions">
        {actions}
        <select
          className="currency-select"
          value={currency}
          onChange={(e) => setCurrency(e.target.value)}
          style={{
            border: '1px solid var(--border-strong)',
            borderRadius: 8,
            padding: '8px 12px',
            fontSize: 13,
            fontWeight: 700,
            background: 'var(--surface)',
          }}
        >
          {CURRENCY_CODES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
    </header>
  )
}
