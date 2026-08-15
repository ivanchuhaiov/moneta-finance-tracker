import { ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { formatMoney, formatPercent } from '../utils/format'

export default function KpiCard({ label, value, currency, changePercent, accent = 'blue', progress }) {
  const hasChange = changePercent !== undefined && changePercent !== null && !Number.isNaN(Number(changePercent))
  const isUp = hasChange && Number(changePercent) >= 0

  return (
    <div className="card card-pad">
      <div className="card-title-sm">{label}</div>
      <div className="num" style={{ fontSize: 26, fontWeight: 800, marginTop: 10, letterSpacing: '-0.02em' }}>
        {formatMoney(value, currency)}
      </div>

      {hasChange && (
        <div className={`trend ${isUp ? 'up' : 'down'}`} style={{ marginTop: 8 }}>
          {isUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {formatPercent(changePercent)} к прошлому периоду
        </div>
      )}

      {progress !== undefined && progress !== null && !Number.isNaN(Number(progress)) && (
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{
              width: `${Math.min(Math.max(Number(progress), 0), 100)}%`,
              background: `var(--accent-${accent})`,
            }}
          />
        </div>
      )}
    </div>
  )
}
