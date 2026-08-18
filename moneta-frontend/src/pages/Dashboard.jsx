import { useEffect, useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import TopBar from '../components/TopBar'
import KpiCard from '../components/KpiCard'
import { useCurrency } from '../context/CurrencyContext'
import { getDashboard, getCashflow } from '../api/analytics'
import { formatMoney, formatDate, formatDateTime, PERIOD_PRESETS, presetRange } from '../utils/format'

const PANEL_HEIGHT = 380

const PERIOD_KPI_LABEL = {
  week: 'за неделю',
  month: 'за месяц',
  quarter: 'за квартал',
}

export default function Dashboard() {
  const { currency } = useCurrency()
  const [period, setPeriod] = useState('month')
  const [dashboard, setDashboard] = useState(null)
  const [cashflow, setCashflow] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')

    const { date_from, date_to } = presetRange(period)

    Promise.all([getDashboard(currency, date_from, date_to), getCashflow(currency, date_from, date_to)])
      .then(([d, cf]) => {
        if (cancelled) return
        setDashboard(d)
        setCashflow(cf)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.response?.data?.detail ? String(err.response.data.detail) : 'Не удалось загрузить дашборд')
      })
      .finally(() => !cancelled && setLoading(false))

    return () => {
      cancelled = true
    }
  }, [currency, period])

  const chartData = cashflow.map((w) => ({
    label: formatDate(w.week_start),
    Доход: Number(w.income),
    Расход: Number(w.expense),
  }))

  const kpiSuffix = PERIOD_KPI_LABEL[period] || 'за месяц'

  return (
    <>
      <TopBar title="Дашборд" subtitle="Общая картина по всем кошелькам" />
      <div className="content">
        {error && <div className="alert alert-error">{error}</div>}

        {loading && !dashboard ? (
          <div className="page-loading">
            <div className="spinner" />
          </div>
        ) : (
          dashboard && (
            <>
              <div className="grid grid-3" style={{ marginBottom: 18 }}>
                <KpiCard label={`Доход ${kpiSuffix}`} value={dashboard.current_month_income} currency={currency} accent="green" />
                <KpiCard label={`Расход ${kpiSuffix}`} value={dashboard.current_month_expense} currency={currency} accent="amber" />
                <KpiCard
                  label={`Чистая прибыль ${kpiSuffix}`}
                  value={Number(dashboard.current_month_income) - Number(dashboard.current_month_expense)}
                  currency={currency}
                  accent="blue"
                />
              </div>

              <div className="grid" style={{ gridTemplateColumns: '2fr 1fr', gap: 18, alignItems: 'stretch' }}>
                <div className="card card-pad" style={{ display: 'flex', flexDirection: 'column', height: PANEL_HEIGHT }}>
                  <div className="card-head">
                    <div className="card-title">Приход / Расход по неделям</div>
                    <div style={{ display: 'flex', gap: 6 }}>
                      {PERIOD_PRESETS.map((p) => (
                        <button
                          key={p.key}
                          type="button"
                          className={`btn btn-sm ${period === p.key ? 'btn-primary' : 'btn-secondary'}`}
                          onClick={() => setPeriod(p.key)}
                        >
                          {p.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  {chartData.length === 0 ? (
                    <div className="empty-state">Пока нет данных для графика</div>
                  ) : (
                    <div style={{ flex: 1, minHeight: 0 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} barGap={4}>
                          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                          <XAxis dataKey="label" tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} axisLine={false} tickLine={false} />
                          <YAxis tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} axisLine={false} tickLine={false} />
                          <Tooltip
                            formatter={(value) => formatMoney(value, currency)}
                            contentStyle={{ borderRadius: 10, border: '1px solid var(--border)', fontSize: 12.5 }}
                          />
                          <Legend wrapperStyle={{ fontSize: 12.5 }} />
                          <Bar dataKey="Доход" fill="var(--accent-green)" radius={[4, 4, 0, 0]} />
                          <Bar dataKey="Расход" fill="var(--accent-amber)" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>

                <div className="card card-pad" style={{ display: 'flex', flexDirection: 'column', height: PANEL_HEIGHT }}>
                  <div className="card-head">
                    <div className="card-title">Кошельки</div>
                  </div>
                  {dashboard.wallets.length === 0 ? (
                    <div className="empty-state">Кошельков пока нет</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
                      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 10 }}>
                        {dashboard.wallets.map((w) => (
                          <div
                            key={w.wallet_id}
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              padding: '10px 0',
                              borderBottom: '1px solid var(--border)',
                            }}
                          >
                            <div>
                              <div style={{ fontWeight: 700, fontSize: 13.5 }}>{w.wallet_name}</div>
                              <div style={{ fontSize: 11.5, color: 'var(--text-tertiary)' }}>{w.wallet_currency}</div>
                            </div>
                            <div className="num" style={{ fontWeight: 700, fontSize: 13.5 }}>
                              {formatMoney(w.balance, w.wallet_currency)}
                            </div>
                          </div>
                        ))}
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 10, borderTop: '1px solid var(--border)' }}>
                        <div style={{ fontWeight: 800, fontSize: 13.5 }}>Итого</div>
                        <div className="num" style={{ fontWeight: 800, fontSize: 13.5 }}>
                          {formatMoney(dashboard.total_balance, dashboard.currency)}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="card card-pad" style={{ marginTop: 18 }}>
                <div className="card-head">
                  <div className="card-title">Последние операции</div>
                </div>
                {dashboard.recent_transactions.length === 0 ? (
                  <div className="empty-state">Операций ещё не было</div>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>Дата</th>
                        <th>Тип</th>
                        <th>Описание</th>
                        <th style={{ textAlign: 'right' }}>Сумма</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dashboard.recent_transactions.map((t) => (
                        <tr key={t.transaction_id}>
                          <td>{formatDateTime(t.transaction_date)}</td>
                          <td>
                            <span className="badge badge-blue">{t.operation_code}</span>
                          </td>
                          <td style={{ color: 'var(--text-secondary)' }}>{t.description || '—'}</td>
                          <td className="num" style={{ textAlign: 'right', fontWeight: 700 }}>
                            {formatMoney(t.amount, t.currency)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </>
          )
        )}
      </div>
    </>
  )
}