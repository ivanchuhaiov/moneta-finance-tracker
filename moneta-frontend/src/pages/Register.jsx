import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '',
    username: '',
    firstname: '',
    lastname: '',
    password: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form)
      navigate('/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Не удалось зарегистрироваться. Проверьте данные.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="sidebar-brand-mark">M</div>
          <span style={{ fontWeight: 800, fontSize: 17 }}>Moneta</span>
        </div>
        <h1 className="auth-title">Создать аккаунт</h1>
        <p className="auth-sub">Начните вести учёт финансов за пару минут</p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="field-row">
            <div className="field">
              <label>Имя</label>
              <input required value={form.firstname} onChange={(e) => update('firstname', e.target.value)} />
            </div>
            <div className="field">
              <label>Фамилия</label>
              <input required value={form.lastname} onChange={(e) => update('lastname', e.target.value)} />
            </div>
          </div>
          <div className="field">
            <label>Имя пользователя</label>
            <input required value={form.username} onChange={(e) => update('username', e.target.value)} />
          </div>
          <div className="field">
            <label>Email</label>
            <input type="email" required value={form.email} onChange={(e) => update('email', e.target.value)} />
          </div>
          <div className="field">
            <label>Пароль</label>
            <input type="password" required value={form.password} onChange={(e) => update('password', e.target.value)} />
          </div>
          <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
            {loading ? 'Создаём…' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="auth-switch">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </div>
      </div>
    </div>
  )
}
