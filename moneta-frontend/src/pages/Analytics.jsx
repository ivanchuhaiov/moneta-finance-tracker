import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { Sparkles } from 'lucide-react'
import TopBar from '../components/TopBar'
import { useCurrency } from '../context/CurrencyContext'
import { getExpensesByCategory, getIncomeByCategory, getSummary, getSavingsRate } from '../api/analytics'
import { getAiSummary } from '../api/ai'
import { formatMoney, formatPercent, toISODate, firstDayOfMonth, today, PERIOD_PRESETS, presetRange } from '../utils/format'

const PALETTE = ['#3d63f5', '#16a879', '#e69a1f', '#e5484d', '#8657e0', '#0ea5e9', '#f97316', '#22c55e']

export default function Analytics() {
  const { currency } = useCurrency()
  const [dateFrom, setDateFrom] = useState(toISODate(firstDayOfMonth()))
  const [dateTo, setDateTo] = useState(toISODate(today()))
  const [activePreset, setActivePreset] = useState('month')

  const [expenses, setExpenses] = useState([])
  const [income, setIncome] = useState([])
  const [summary, setSummary] = useState(null)
  const [savings, setSavings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [aiSummary, setAiSummary] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiError, setAiError] = useState('')

  function load(from = dateFrom, to = dateTo) {
    setLoading(true)
    setError('')
    Promise.all([
      getExpensesByCategory({ date_from: from, date_to: to, currency }),
      getIncomeByCategory({ date_from: from, date_to: to, currency }),
      getSummary(currency, from, to),
      getSavingsRate(currency, from, to),
    ])
      .then(([exp, inc, sum, sr]) => {
        setExpenses(exp)
        setIncome(inc)
        setSummary(sum)
        setSavings(sr)
      })
      .catch(() => setError('Не удалось загрузить аналитику'))
      .finally(() => setLoading(false))
  }

  function handleAiSummary() {
    setAiLoading(true)
    setAiError('')
    getAiSummary(currency, dateFrom, dateTo)
      .then(setAiSummary)
      .catch(() => setAiError('Не удалось получить AI-обзор'))
      .finally(() => setAiLoading(false))
  }

  function applyPreset(preset) {
    const { date_from, date_to } = presetRange(preset.key)
    setActivePreset(preset.key)
    setDateFrom(date_from)
    setDateTo(date_to)
    setAiSummary(null)
    setAiError('')
    load(date_from, date_to)
  }

  function handleManualApply() {
    setActivePreset(null)
    setAiSummary(null)
    setAiError('')
    load()
  }

  useEffect(() => {
    setAiSummary(null)
    setAiError('')
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currency])

  return (
    <>
      <TopBar title="Аналитика" subtitle="Разбивка доходов и расходов по категориям" />
      <div className="content">
        <div className="card card-pad" style={{ marginBottom: 18 }}>
          <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            {PERIOD_PRESETS.map((p) => (
              <button
                key={p.key}
                type="button"
                className={`btn btn-sm ${activePreset === p.key ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => applyPreset(p)}
              >
                {p.label}
              </button>
            ))}
          </div>
          <div className="field-row" style={{ alignItems: 'flex-end', marginBottom: 0 }}>
            <div className="field" style={{ marginBottom: 0 }}>
              <label>С даты</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => {
                  setActivePreset(null)
                  setDateFrom(e.target.value)
                }}
              />
            </div>
            <div className="field" style={{ marginBottom: 0 }}>
              <label>По дату</label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => {
                  setActivePreset(null)
                  setDateTo(e.target.value)
                }}
              />
            </div>
            <button className="btn btn-primary" onClick={handleManualApply} style={{ height: 38 }}>
              Применить
            </button>
          </div>
        </div>

        <div className="card card-pad ai-summary-card" style={{ marginBottom: 18 }}>
          <div className="card-head">
            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Sparkles size={16} style={{ color: 'var(--accent-purple)' }} />
              AI-обзор периода
            </div>
            <button className="btn btn-sm btn-secondary" onClick={handleAiSummary} disabled={aiLoading}>
              {aiLoading ? 'Генерируем…' : aiSummary ? 'Обновить' : 'Получить обзор'}
            </button>
          </div>
          {aiError && <div className="alert alert-error" style={{ marginTop: 4 }}>{aiError}</div>}
          {aiSummary && !aiError && <p className="ai-summary-text">{aiSummary.summary}</p>}
          {!aiSummary && !aiError && !aiLoading && (
            <div className="empty-state" style={{ padding: '4px 0 0' }}>
              Нажмите «Получить обзор», чтобы AI проанализировал доходы, расходы и норму сбережений за выбранный период
            </div>
          )}
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="page-loading">
            <div className="spinner" />
          </div>
        ) : (
          <>
            {summary && savings && (
              <div className="grid grid-3" style={{ marginBottom: 18 }}>
                <div className="card card-pad">
                  <div className="card-title-sm">Доход (период)</div>
                  <div className="num" style={{ fontSize: 20, fontWeight: 800, marginTop: 8 }}>
                    {formatMoney(summary.current_income, currency)}
                  </div>
                </div>
                <div className="card card-pad">
                  <div className="card-title-sm">Расход (период)</div>
                  <div className="num" style={{ fontSize: 20, fontWeight: 800, marginTop: 8 }}>
                    {formatMoney(summary.current_expense, currency)}
                  </div>
                </div>
                <div className="card card-pad">
                  <div className="card-title-sm">Норма сбережений</div>
                  <div className="num" style={{ fontSize: 20, fontWeight: 800, marginTop: 8 }}>
                    {formatPercent(savings.savings_rate_percentage)}
                  </div>
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{ width: `${Math.min(Math.max(Number(savings.savings_rate_percentage), 0), 100)}%`, background: 'var(--accent-blue)' }}
                    />
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-2">
              <CategoryCard title="Расходы по категориям" rows={expenses} currency={currency} emptyText="Расходов за период нет" />
              <CategoryCard title="Доходы по категориям" rows={income} currency={currency} emptyText="Доходов за период нет" />
            </div>
          </>
        )}
      </div>
    </>
  )
}

function CategoryCard({ title, rows, currency, emptyText }) {
  const data = rows.map((r) => ({ name: r.category, value: Number(r.total), percentage: Number(r.percentage) }))

  return (
    <div className="card card-pad">
      <div className="card-head">
        <div className="card-title">{title}</div>
      </div>
      {data.length === 0 ? (
        <div className="empty-state">{emptyText}</div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
                {data.map((_, i) => (
                  <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatMoney(value, currency)} contentStyle={{ borderRadius: 10, fontSize: 12.5 }} />
              <Legend wrapperStyle={{ fontSize: 11.5 }} />
            </PieChart>
          </ResponsiveContainer>
          <table style={{ marginTop: 8 }}>
            <tbody>
              {data.map((row, i) => (
                <tr key={row.name}>
                  <td style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ width: 8, height: 8, borderRadius: 999, background: PALETTE[i % PALETTE.length] }} />
                    {row.name}
                  </td>
                  <td className="num" style={{ textAlign: 'right' }}>
                    {formatMoney(row.value, currency)}
                  </td>
                  <td style={{ textAlign: 'right', color: 'var(--text-tertiary)', width: 60 }}>{row.percentage.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  )
}