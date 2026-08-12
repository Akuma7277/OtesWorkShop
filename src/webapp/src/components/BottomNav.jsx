import { Link, useLocation } from 'react-router-dom'
import { useApp } from '../context/AppContext'

const navItems = [
  { path: '/',        icon: '🏠', label: 'Bosh sahifa' },
  { path: '/shop',    icon: '🛍️', label: 'Do\'kon'    },
  { path: '/cart',    icon: '🛒', label: 'Savat'      },
  { path: '/orders',  icon: '📦', label: 'Buyurtmalar' },
  { path: '/profile', icon: '👤', label: 'Profil'     },
]

export default function BottomNav() {
  const { pathname } = useLocation()
  const { cart } = useApp()
  const cartCount = cart.length

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
