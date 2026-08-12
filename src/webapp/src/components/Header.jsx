import { useApp } from '../context/AppContext'
import { Link } from 'react-router-dom'

export default function Header() {
  const { balance, isAdmin } = useApp()

  return (
    <header className="app-header">
      <div className="header-logo">
        <div className="header-logo-icon">🛍️</div>
        <span className="header-logo-text">NexШоп</span>
      </div>
      <div className="flex items-center gap-2">
        {isAdmin && (
          <Link to="/admin" className="header-badge" style={{ textDecoration: 'none', background: 'var(--gradient-gold)', color: '#000', fontWeight: 'bold', padding: '6px 12px', border: 'none', boxShadow: '0 0 10px rgba(255, 179, 0, 0.4)' }}>
            🛠 Admin Panel
          </Link>
        )}
        <div className="header-badge" style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.12)', color: '#f1f1f5' }}>
          💰 {Number(balance).toLocaleString()} $
        </div>
      </div>

    </header>
  )
}
