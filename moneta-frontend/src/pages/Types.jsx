import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import TopBar from '../components/TopBar'
import Modal from '../components/Modal'
import {
  listWalletTypes,
  createWalletType,
  listCreditTypes,
  createCreditType,
  listDebitTypes,
  createDebitType,
} from '../api/types'

const TABS = [
  { key: 'wallet', label: 'Типы кошельков' },
  { key: 'credit', label: 'Категории доходов' },
  { key: 'debit', label: 'Категории расходов' },
]

const BADGE_CLASS = {
  wallet: 'badge-blue',
  credit: 'badge-green',
  debit: 'badge-red',
}

export default function Types() {
  const [tab, setTab] = useState('wallet')
  const [walletTypes, setWalletTypes] = useState([])
  const [creditTypes, setCreditTypes] = useState([])
  const [debitTypes, setDebitTypes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ code: '', name: '' })
  const [submitting, setSubmitting] = useState(false)

  async function loadAll() {
    setLoading(true)
    setError('')
    try {
      const [wt, ct, dt] = await Promise.all([listWalletTypes(), listCreditTypes(), listDebitTypes()])
      setWalletTypes(wt)
      setCreditTypes(ct)
      setDebitTypes(dt)
    } catch {
      setError('Не удалось загрузить справочники')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAll()
  }, [])

  const config = {
    wallet: { data: walletTypes, create: createWalletType, label: 'тип кошелька' },
    credit: { data: creditTypes, create: createCreditType, label: 'категорию дохода' },
    debit: { data: debitTypes, create: createDebitType, label: 'категорию расхода' },
  }[tab]

  async function handleCreate(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await config.create(form)
      setShowCreate(false)
      setForm({ code: '', name: '' })
      loadAll()
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Не удалось создать запись')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <TopBar
        title="Типы и категории"
        subtitle="Справочники для кошельков, доходов и расходов"
        actions={
          <button className="btn btn-primary btn-sm" onClick={() => setShowCreate(true)}>
            <Plus size={15} /> Добавить
          </button>
        }
      />
      <div className="content">
        <div className="tabs">
          {TABS.map((t) => (
            <button key={t.key} className={`tab-btn${tab === t.key ? ' active' : ''}`} onClick={() => setTab(t.key)}>
              {t.label}
            </button>
          ))}
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="page-loading">
            <div className="spinner" />
          </div>
        ) : (
          <div className="card">
            {config.data.length === 0 ? (
              <div className="empty-state">Пока пусто — добавьте первую запись</div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Код</th>
                      <th>Название</th>
                    </tr>
                  </thead>
                  <tbody>
                    {config.data.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <span className={`badge ${BADGE_CLASS[tab]}`}>{item.code}</span>
                        </td>
                        <td style={{ fontWeight: 600 }}>{item.name}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>

      {showCreate && (
        <Modal
          title={`Новая запись — ${config.label}`}
          onClose={() => setShowCreate(false)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setShowCreate(false)}>
                Отмена
              </button>
              <button className="btn btn-primary" onClick={handleCreate} disabled={submitting}>
                {submitting ? 'Создаём…' : 'Создать'}
              </button>
            </>
          }
        >
          <form onSubmit={handleCreate}>
            <div className="field">
              <label>Код</label>
              <input required value={form.code} onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))} placeholder="SALARY" />
            </div>
            <div className="field">
              <label>Название</label>
              <input required value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="Зарплата" />
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}
