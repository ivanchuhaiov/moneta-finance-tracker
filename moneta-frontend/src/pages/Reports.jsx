import { useState } from 'react'
import { FileDown, FileText } from 'lucide-react'
import TopBar from '../components/TopBar'
import { generateReport } from '../api/reports'
import { CURRENCY_CODES } from '../api/constants'
import { toISODate, firstDayOfMonth, today } from '../utils/format'

const CHECKBOXES = [
  { key: 'include_summary', label: 'Общая сводка (доходы/расходы)' },
  { key: 'include_by_category', label: 'Разбивка по категориям' },
  { key: 'include_by_wallet', label: 'Разбивка по кошелькам' },
  { key: 'include_transactions', label: 'Полный список операций' },
]

export default function Reports() {
  const [form, setForm] = useState({
    date_from: toISODate(firstDayOfMonth()),
    date_to: toISODate(today()),
    target_currency: CURRENCY_CODES[0],
    include_summary: true,
    include_by_category: true,
    include_by_wallet: true,
    include_transactions: false,
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleGenerate(e) {
    e.preventDefault()
    setLoading(true)
    setMessage(null)
    try {
      await generateReport(form)
      setMessage({ type: 'success', text: 'Отчёт сформирован и скачан' })
    } catch (err) {
      const detail = err.response?.data?.detail
      setMessage({ type: 'error', text: typeof detail === 'string' ? detail : 'Не удалось сформировать отчёт' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <TopBar title="Отчёты" subtitle="Финансовый отчёт в формате Word (.docx)" />
      <div className="content" style={{ display: 'flex', justifyContent: 'center' }}>
        <div className="card card-pad" style={{ maxWidth: 520, width: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20, paddingBottom: 18, borderBottom: '1px solid var(--border)' }}>
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 10,
                background: 'var(--accent-blue-dim)',
                color: 'var(--accent-blue)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <FileText size={19} />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 15 }}>Финансовый отчёт</div>
              <div style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>Word-документ за выбранный период</div>
            </div>
          </div>

          {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}

          <form onSubmit={handleGenerate}>
            <div className="field-row">
              <div className="field">
                <label>С даты</label>
                <input required type="date" value={form.date_from} onChange={(e) => update('date_from', e.target.value)} />
              </div>
              <div className="field">
                <label>По дату</label>
                <input required type="date" value={form.date_to} onChange={(e) => update('date_to', e.target.value)} />
              </div>
            </div>

            <div className="field">
              <label>Валюта отчёта</label>
              <select value={form.target_currency} onChange={(e) => update('target_currency', e.target.value)}>
                {CURRENCY_CODES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label>Разделы отчёта</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 4 }}>
                {CHECKBOXES.map((cb) => (
                  <label key={cb.key} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13.5, fontWeight: 500 }}>
                    <input
                      type="checkbox"
                      checked={form[cb.key]}
                      onChange={(e) => update(cb.key, e.target.checked)}
                      style={{ width: 16, height: 16 }}
                    />
                    {cb.label}
                  </label>
                ))}
              </div>
            </div>

            <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
              <FileDown size={15} />
              {loading ? 'Формируем…' : 'Сформировать и скачать'}
            </button>
          </form>
        </div>
      </div>
    </>
  )
}
