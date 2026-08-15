import { useEffect, useState } from 'react'
import TopBar from '../components/TopBar'
import { listWallets } from '../api/wallets'
import { listCreditTypes, listDebitTypes } from '../api/types'
import { transfer, transactionHistory, createCredit, createDebit } from '../api/transactions'
import { getWalletOperations } from '../api/wallets'
import { formatMoney, formatDateTime } from '../utils/format'

const TABS = [
  { key: 'transfer', label: 'Перевод' },
  { key: 'credit', label: 'Пополнение' },
  { key: 'debit', label: 'Списание' },
  { key: 'history', label: 'История переводов' },
  { key: 'operations', label: 'Операции кошелька' },
]

function nowLocalISO() {
  const d = new Date()
  d.setSeconds(0, 0)
  return d.toISOString().slice(0, 16)
}

export default function Transactions() {
  const [tab, setTab] = useState('transfer')
  const [wallets, setWallets] = useState([])
  const [creditTypes, setCreditTypes] = useState([])
  const [debitTypes, setDebitTypes] = useState([])
  const [message, setMessage] = useState(null) // { type: 'error'|'success', text }

  useEffect(() => {
    Promise.all([listWallets(), listCreditTypes(), listDebitTypes()])
      .then(([w, ct, dt]) => {
        setWallets(w)
        setCreditTypes(ct)
        setDebitTypes(dt)
      })
      .catch(() => setMessage({ type: 'error', text: 'Не удалось загрузить справочники' }))
  }, [])

  return (
    <>
      <TopBar title="Операции" subtitle="Переводы, пополнения и списания" />
      <div className="content">
        <div className="tabs">
          {TABS.map((t) => (
            <button
              key={t.key}
              className={`tab-btn${tab === t.key ? ' active' : ''}`}
              onClick={() => {
                setTab(t.key)
                setMessage(null)
              }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}

        {tab === 'transfer' && <TransferForm wallets={wallets} onDone={setMessage} />}
        {tab === 'credit' && <CreditForm wallets={wallets} creditTypes={creditTypes} onDone={setMessage} />}
        {tab === 'debit' && <DebitForm wallets={wallets} debitTypes={debitTypes} onDone={setMessage} />}
        {tab === 'history' && <History />}
        {tab === 'operations' && <WalletOperations wallets={wallets} />}
      </div>
    </>
  )
}

function TransferForm({ wallets, onDone }) {
  const [form, setForm] = useState({ from_wallet_id: '', to_wallet_id: '', amount: '', description: '' })
  const [submitting, setSubmitting] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await transfer({
        from_wallet_id: Number(form.from_wallet_id),
        to_wallet_id: Number(form.to_wallet_id),
        amount: form.amount,
        description: form.description || null,
      })
      onDone({ type: 'success', text: 'Перевод выполнен' })
      setForm({ from_wallet_id: '', to_wallet_id: '', amount: '', description: '' })
    } catch (err) {
      const detail = err.response?.data?.detail
      onDone({ type: 'error', text: typeof detail === 'string' ? detail : 'Не удалось выполнить перевод' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="card card-pad op-form">
      <div className="op-form-head">
        <span className="badge badge-blue">Перевод</span>
        <span className="op-form-hint">Между двумя своими кошельками</span>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="grid grid-2">
          <div className="field">
            <label>Со счёта</label>
            <select required value={form.from_wallet_id} onChange={(e) => update('from_wallet_id', e.target.value)}>
              <option value="">Выберите кошелёк</option>
              {wallets.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>На счёт</label>
            <select required value={form.to_wallet_id} onChange={(e) => update('to_wallet_id', e.target.value)}>
              <option value="">Выберите кошелёк</option>
              {wallets.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Сумма</label>
            <input required type="number" step="0.01" min="0" value={form.amount} onChange={(e) => update('amount', e.target.value)} />
          </div>
          <div className="field">
            <label>Описание (необязательно)</label>
            <input value={form.description} onChange={(e) => update('description', e.target.value)} placeholder="Например, перевод на сбережения" />
          </div>
        </div>
        <div className="op-form-foot">
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Отправляем…' : 'Выполнить перевод'}
          </button>
        </div>
      </form>
    </div>
  )
}

function CreditForm({ wallets, creditTypes, onDone }) {
  const [form, setForm] = useState({ wallet_id: '', amount: '', credit_type_id: '', operation_date: nowLocalISO() })
  const [submitting, setSubmitting] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await createCredit(Number(form.wallet_id), {
        amount: form.amount,
        credit_type_id: Number(form.credit_type_id),
        operation_date: new Date(form.operation_date).toISOString(),
      })
      onDone({ type: 'success', text: 'Пополнение добавлено' })
      setForm({ wallet_id: '', amount: '', credit_type_id: '', operation_date: nowLocalISO() })
    } catch (err) {
      const detail = err.response?.data?.detail
      onDone({ type: 'error', text: typeof detail === 'string' ? detail : 'Не удалось добавить пополнение' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="card card-pad op-form">
      <div className="op-form-head">
        <span className="badge badge-green">Пополнение</span>
        <span className="op-form-hint">Увеличивает баланс выбранного кошелька</span>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="grid grid-2">
          <div className="field">
            <label>Кошелёк</label>
            <select required value={form.wallet_id} onChange={(e) => update('wallet_id', e.target.value)}>
              <option value="">Выберите кошелёк</option>
              {wallets.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Категория дохода</label>
            <select required value={form.credit_type_id} onChange={(e) => update('credit_type_id', e.target.value)}>
              <option value="">Выберите</option>
              {creditTypes.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Сумма</label>
            <input required type="number" step="0.01" min="0" value={form.amount} onChange={(e) => update('amount', e.target.value)} />
          </div>
          <div className="field">
            <label>Дата операции</label>
            <input required type="datetime-local" value={form.operation_date} onChange={(e) => update('operation_date', e.target.value)} />
          </div>
        </div>
        <div className="op-form-foot">
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Добавляем…' : 'Добавить пополнение'}
          </button>
        </div>
      </form>
    </div>
  )
}

function DebitForm({ wallets, debitTypes, onDone }) {
  const [form, setForm] = useState({ wallet_id: '', amount: '', debit_type_id: '', operation_date: nowLocalISO() })
  const [submitting, setSubmitting] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await createDebit(Number(form.wallet_id), {
        amount: form.amount,
        debit_type_id: Number(form.debit_type_id),
        operation_date: new Date(form.operation_date).toISOString(),
      })
      onDone({ type: 'success', text: 'Списание добавлено' })
      setForm({ wallet_id: '', amount: '', debit_type_id: '', operation_date: nowLocalISO() })
    } catch (err) {
      const detail = err.response?.data?.detail
      onDone({ type: 'error', text: typeof detail === 'string' ? detail : 'Не удалось добавить списание' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="card card-pad op-form">
      <div className="op-form-head">
        <span className="badge badge-red">Списание</span>
        <span className="op-form-hint">Уменьшает баланс выбранного кошелька</span>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="grid grid-2">
          <div className="field">
            <label>Кошелёк</label>
            <select required value={form.wallet_id} onChange={(e) => update('wallet_id', e.target.value)}>
              <option value="">Выберите кошелёк</option>
              {wallets.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Категория расхода</label>
            <select required value={form.debit_type_id} onChange={(e) => update('debit_type_id', e.target.value)}>
              <option value="">Выберите</option>
              {debitTypes.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Сумма</label>
            <input required type="number" step="0.01" min="0" value={form.amount} onChange={(e) => update('amount', e.target.value)} />
          </div>
          <div className="field">
            <label>Дата операции</label>
            <input required type="datetime-local" value={form.operation_date} onChange={(e) => update('operation_date', e.target.value)} />
          </div>
        </div>
        <div className="op-form-foot">
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Добавляем…' : 'Добавить списание'}
          </button>
        </div>
      </form>
    </div>
  )
}

function History() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    transactionHistory()
      .then(setRows)
      .catch(() => setError('Не удалось загрузить историю переводов'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-loading"><div className="spinner" /></div>
  if (error) return <div className="alert alert-error">{error}</div>

  return (
    <div className="card">
      {rows.length === 0 ? (
        <div className="empty-state">Переводов пока не было</div>
      ) : (
        <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Дата</th>
              <th>Откуда</th>
              <th>Куда</th>
              <th style={{ textAlign: 'right' }}>Сумма</th>
              <th>Описание</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{formatDateTime(r.transaction_date)}</td>
                <td>{r.from_wallet_id ? `#${r.from_wallet_id}` : '—'}</td>
                <td>{r.to_wallet_id ? `#${r.to_wallet_id}` : '—'}</td>
                <td className="num" style={{ textAlign: 'right', fontWeight: 700 }}>
                  {formatMoney(r.from_amount, '')}
                </td>
                <td style={{ color: 'var(--text-secondary)' }}>{r.description || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      )}
    </div>
  )
}

function WalletOperations({ wallets }) {
  const [walletId, setWalletId] = useState('')
  const [ops, setOps] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleLoad() {
    if (!walletId) return
    setLoading(true)
    setError('')
    try {
      const data = await getWalletOperations(Number(walletId))
      setOps(data)
    } catch {
      setError('Не удалось загрузить операции')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card card-pad op-form" style={{ marginBottom: 18 }}>
        <div className="op-form-head">
          <span className="badge badge-blue">Фильтр</span>
          <span className="op-form-hint">Пополнения и списания конкретного кошелька</span>
        </div>
        <div className="grid grid-2" style={{ alignItems: 'end' }}>
          <div className="field" style={{ marginBottom: 0 }}>
            <label>Кошелёк</label>
            <select value={walletId} onChange={(e) => setWalletId(e.target.value)}>
              <option value="">Выберите кошелёк</option>
              {wallets.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleLoad} disabled={!walletId || loading} style={{ height: 38 }}>
            {loading ? 'Загружаем…' : 'Показать операции'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {ops && (
        <div className="grid grid-2">
          <div className="card card-pad">
            <div className="card-title" style={{ marginBottom: 12 }}>
              Пополнения
            </div>
            {ops.credits.length === 0 ? (
              <div className="empty-state">Нет пополнений</div>
            ) : (
              ops.credits.map((c) => (
                <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 12.5 }}>{formatDateTime(c.operation_date)}</span>
                  <span className="num badge-green badge" >+{formatMoney(c.amount, '')}</span>
                </div>
              ))
            )}
          </div>
          <div className="card card-pad">
            <div className="card-title" style={{ marginBottom: 12 }}>
              Списания
            </div>
            {ops.debits.length === 0 ? (
              <div className="empty-state">Нет списаний</div>
            ) : (
              ops.debits.map((d) => (
                <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 12.5 }}>{formatDateTime(d.operation_date)}</span>
                  <span className="num badge-red badge">-{formatMoney(d.amount, '')}</span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
