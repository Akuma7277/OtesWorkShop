import { Link, useLocation } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { t } from '../i18n'

export default function BottomNav() {
  const { pathname } = useLocation()
  const { cart, lang } = useApp()
  const cartCount = cart.length

  const navItems = [
    { path: '/',        icon: '🏠', label: t('welcome') },
    { path: '/shop',    icon: '🍀', label: t('products') },
    { path: '/chat',    icon: '💬', label: lang === 'ru' ? 'Чат' : 'Chat' },
    { path: '/cart',    icon: '🛒', label: t('cart') },
    { path: '/profile', icon: '👤', label: t('profile') },
  ]

  return (
    <nav className="bottom-nav">
      {navItems.map(({ path, icon, label }) => {
        const active = pathname === path || (path !== '/' && pathname.startsWith(path))
        return (
          <Link
            key={path}
            to={path}
            className={`nav-item ${active ? 'active' : ''}`}
          >
            <div className="nav-icon-wrapper">
              <span>{icon}</span>
            </div>
            <span className="nav-label">{label}</span>
            {path === '/cart' && cartCount > 0 && (
              <span className="nav-badge">{cartCount}</span>
            )}
          </Link>
        )
      })}
    </nav>
  )
}

