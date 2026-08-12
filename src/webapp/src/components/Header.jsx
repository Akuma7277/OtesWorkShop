import { useApp } from '../context/AppContext'
import { Link } from 'react-router-dom'

export default function Header() {
  const { balance, isAdmin } = useApp()

  return (
    <header className="app-header">
      <div className="header-logo">
        <div className="header-logo-icon">🛍️</div>
        <span className="header-logo-text">Shopim</span>
      </div>
      <div className="flex items-center gap-2">
        {isAdmin && (
          <Link to="/admin" className="header-badge" style={{ textDecoration: 'none' }}>
            🛠 Admin
          </Link>
        )}
        <div className="header-badge" style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.12)', color: '#f1f1f5' }}>
          💳 {Number(balance).toLocaleString()} so'm
        </div>
      </div>
    </header>
  )
}
