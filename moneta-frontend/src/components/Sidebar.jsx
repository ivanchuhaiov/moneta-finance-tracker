import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  WalletCards,
  ArrowLeftRight,
  Tags,
  BarChart3,
  FileText,
  Sparkles,
  LogOut,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Дашборд', icon: LayoutDashboard },
  { to: '/wallets', label: 'Кошельки', icon: WalletCards },
  { to: '/transactions', label: 'Операции', icon: ArrowLeftRight },
  { to: '/types', label: 'Типы и категории', icon: Tags },
  { to: '/analytics', label: 'Аналитика', icon: BarChart3 },
  { to: '/reports', label: 'Отчёты', icon: FileText },
  { to: '/ai-chat', label: 'AI-ассистент', icon: Sparkles },
]

export default function Sidebar() {
  const { user, logout } = useAuth()

  const initials = user
    ? `${(user.firstname || '?')[0]}${(user.lastname || '?')[0]}`.toUpperCase()
    : '?'

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark">M</div>
        Moneta
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Меню</div>
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          >
            <Icon />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-foot">
        {user && (
          <div className="sidebar-user">
            <div className="avatar">{initials}</div>
            <div>
              <div className="sidebar-user-name">
                {user.firstname} {user.lastname}
              </div>
              <div className="sidebar-user-email">{user.email}</div>
            </div>
          </div>
        )}
        <button className="logout-btn" onClick={logout}>
          <LogOut size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
          Выйти
        </button>
      </div>
    </aside>
  )
}