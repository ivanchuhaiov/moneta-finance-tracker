import { useEffect, useState } from 'react'
import { Plus, Pencil, Ban, CheckCircle2 } from 'lucide-react'
import TopBar from '../components/TopBar'
import Modal from '../components/Modal'
import {
  listWallets,
  createWallet,
  updateWallet,
  deactivateWallet,
  listCurrencies,
} from '../api/wallets'
import { listWalletTypes, createWalletType } from '../api/types'
import { formatMoney, formatDate } from '../utils/format'

const emptyForm = { name: '', wallet_type_id: '', currency_id: '', balance: '0' }

export default function Wallets() {
  const [wallets, setWallets] = useState([])
  const [walletTypes, setWalletTypes] = useState([])
  const [currencies, setCurrencies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState('')

  const [editWallet, setEditWallet] = useState(null)
  const [editName, setEditName] = useState('')

  const [showNewType, setShowNewType] = useState(false)
  const [newType, setNewType] = useState({ code: '', name: '' })

  async function loadAll() {
    setLoading(true)
    setError('')
    try {
      const [w, wt, cur] = await Promise.all([listWallets(), listWalletTypes(), listCurrencies()])
      setWallets(w)
      setWalletTypes(wt)
      setCurrencies(cur)
    } catch (err) {
      setError('Не удалось загрузить кошельки')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAll()
  }, [])

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleCreate(e) {
    e.preventDefault()
    setFormError('')
    setSubmitting(true)
    try {
      await createWallet({
        name: form.name,
        wallet_type_id: Number(form.wallet_type_id),
        currency_id: Number(form.currency_id),
        balance: form.balance,
      })
      setShowCreate(false)
      setForm(emptyForm)
      loadAll()
    } catch (err) {
      const detail = err.response?.data?.detail
      setFormError(typeof detail === 'string' ? detail : 'Не удалось создать кошелёк. Проверьте ID валюты и типа.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleToggleActive(wallet) {
    try {
      if (wallet.is_active) {
        await deactivateWallet(wallet.id)
      } else {
        await updateWallet(wallet.id, { is_active: true })
      }
      loadAll()
    } catch {
      setError('Не удалось изменить статус кошелька')
    }
  }

  function openEdit(wallet) {
    setEditWallet(wallet)
    setEditName(wallet.name)
  }

  async function handleSaveEdit(e) {
    e.preventDefault()
    try {
      await updateWallet(editWallet.id, { name: editName })
      setEditWallet(null)
      loadAll()
    } catch {
      setError('Не удалось сохранить изменения')
    }
  }

  async function handleCreateType(e) {
    e.preventDefault()
    try {
      await createWalletType(newType)
      setShowNewType(false)
      setNewType({ code: '', name: '' })
      const wt = await listWalletTypes()
      setWalletTypes(wt)
    } catch {
      setError('Не удалось создать тип кошелька')
    }
  }

  function walletTypeName(id) {
    return walletTypes.find((t) => t.id === id)?.name || `#${id}`
  }

  function currencyCode(id) {
    return currencies.find((c) => c.id === id)?.code || `#${id}`
  }

  return (
    <>
      <TopBar
        title="Кошельки"
        subtitle={`${wallets.length} кошельков`}
        actions={
          <button className="btn btn-primary btn-sm" onClick={() => setShowCreate(true)}>
            <Plus size={15} /> Новый кошелёк
          </button>
        }
      />
      <div className="content">
        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="page-loading">
            <div className="spinner" />
          </div>
        ) : (
          <div className="card">
            {wallets.length === 0 ? (
              <div className="empty-state">Кошельков пока нет — создайте первый</div>
            ) : (
              <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Название</th>
                    <th>Тип</th>
                    <th>Валюта</th>
                    <th style={{ textAlign: 'right' }}>Баланс</th>
                    <th>Статус</th>
                    <th>Создан</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {wallets.map((w) => (
                    <tr key={w.id}>
                      <td style={{ fontWeight: 700 }}>{w.name}</td>
                      <td style={{ color: 'var(--text-secondary)' }}>{walletTypeName(w.wallet_type_id)}</td>
                      <td>
                        <span className="badge badge-gray">{currencyCode(w.currency_id)}</span>
                      </td>
                      <td className="num" style={{ textAlign: 'right', fontWeight: 700 }}>
                        {formatMoney(w.balance, '')}
                      </td>
                      <td>
                        {w.is_active ? (
                          <span className="badge badge-green">Активен</span>
                        ) : (
                          <span className="badge badge-gray">Отключён</span>
                        )}
                      </td>
                      <td style={{ color: 'var(--text-tertiary)', fontSize: 12.5 }}>{formatDate(w.created_at)}</td>
                      <td>
                        <div style={{ display: 'flex', gap: 6, justifyContent: 'flex-end' }}>
                          <button className="btn btn-ghost btn-sm" onClick={() => openEdit(w)}>
                            <Pencil size={13} />
                          </button>
                          <button className="btn btn-ghost btn-sm" onClick={() => handleToggleActive(w)}>
                            {w.is_active ? <Ban size={13} /> : <CheckCircle2 size={13} />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              </div>
            )}
          </div>
        )}

        {currencies.length > 0 && (
          <div className="card card-pad" style={{ marginTop: 18 }}>
            <div className="card-head">
              <div className="card-title">Справочник валют</div>
            </div>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              {currencies.map((c) => (
                <span key={c.id} className="badge badge-gray">
                  {c.code} — {c.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {showCreate && (
        <Modal
          title="Новый кошелёк"
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
          {formError && <div className="alert alert-error">{formError}</div>}
          <form onSubmit={handleCreate}>
            <div className="field">
              <label>Название</label>
              <input required value={form.name} onChange={(e) => update('name', e.target.value)} placeholder="Например, Основной счёт" />
            </div>
            <div className="field">
              <label>
                Тип кошелька{' '}
                <button
                  type="button"
                  onClick={() => setShowNewType(true)}
                  style={{ border: 'none', background: 'none', color: 'var(--accent-blue)', cursor: 'pointer', fontSize: 11.5, fontWeight: 700 }}
                >
                  + новый тип
                </button>
              </label>
              <select required value={form.wallet_type_id} onChange={(e) => update('wallet_type_id', e.target.value)}>
                <option value="">Выберите тип</option>
                {walletTypes.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="field-row">
              <div className="field">
                <label>Валюта</label>
                <select required value={form.currency_id} onChange={(e) => update('currency_id', e.target.value)}>
                  <option value="">Выберите валюту</option>
                  {currencies.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.code} — {c.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>Начальный баланс</label>
                <input
                  required
                  type="number"
                  step="0.01"
                  value={form.balance}
                  onChange={(e) => update('balance', e.target.value)}
                />
              </div>
            </div>
          </form>
        </Modal>
      )}

      {showNewType && (
        <Modal
          title="Новый тип кошелька"
          onClose={() => setShowNewType(false)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setShowNewType(false)}>
                Отмена
              </button>
              <button className="btn btn-primary" onClick={handleCreateType}>
                Создать
              </button>
            </>
          }
        >
          <form onSubmit={handleCreateType}>
            <div className="field">
              <label>Код</label>
              <input required value={newType.code} onChange={(e) => setNewType((f) => ({ ...f, code: e.target.value }))} placeholder="CASH" />
            </div>
            <div className="field">
              <label>Название</label>
              <input required value={newType.name} onChange={(e) => setNewType((f) => ({ ...f, name: e.target.value }))} placeholder="Наличные" />
            </div>
          </form>
        </Modal>
      )}

      {editWallet && (
        <Modal
          title={`Редактировать «${editWallet.name}»`}
          onClose={() => setEditWallet(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setEditWallet(null)}>
                Отмена
              </button>
              <button className="btn btn-primary" onClick={handleSaveEdit}>
                Сохранить
              </button>
            </>
          }
        >
          <form onSubmit={handleSaveEdit}>
            <div className="field">
              <label>Название</label>
              <input required value={editName} onChange={(e) => setEditName(e.target.value)} />
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}
