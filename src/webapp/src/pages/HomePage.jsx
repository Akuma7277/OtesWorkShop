import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { getProducts, getMyOrders } from '../api'
import Spinner from '../components/Spinner'

const STATUS_MAP = {
  PENDING_ADMIN: { label: 'Kutilmoqda', cls: 'status-pending', icon: '⏳' },
  APPROVED:      { label: 'Tasdiqlangan', cls: 'status-approved', icon: '✅' },
  PACKING:       { label: 'Qadoqlanmoqda', cls: 'status-packing', icon: '📦' },
  OUT_FOR_DELIVERY: { label: 'Yetkazilmoqda', cls: 'status-delivery', icon: '🚚' },
  DELIVERED:     { label: 'Yetkazildi', cls: 'status-delivered', icon: '🏁' },
  REJECTED:      { label: 'Rad etildi', cls: 'status-rejected', icon: '❌' },
  CANCELLED:     { label: 'Bekor qilindi', cls: 'status-cancelled', icon: '🚫' },
}

export default function HomePage() {
  const { user, balance, tgUser } = useApp()
  const [products, setProducts] = useState([])
  const [recentOrders, setRecentOrders] = useState([])
  const [loadingProducts, setLoadingProducts] = useState(true)
  const [loadingOrders, setLoadingOrders] = useState(true)

  useEffect(() => {
    getProducts({ limit: 6, is_active: true })
      .then(data => setProducts(data?.items || data || []))
      .catch(() => {})
      .finally(() => setLoadingProducts(false))

    getMyOrders({ limit: 3 })
      .then(data => setRecentOrders(data?.items || data || []))
      .catch(() => {})
      .finally(() => setLoadingOrders(false))
  }, [])

  const displayName = user?.full_name || tgUser?.first_name || 'Foydalanuvchi'
  const initials = displayName.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)

  return (
    <div className="page-content fade-in">
      {/* Greeting Hero */}
      <div className="hero-card mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="profile-avatar" style={{ width: 52, height: 52, fontSize: 20 }}>
            {initials}
          </div>
          <div>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', marginBottom: 2 }}>
              Xush kelibsiz 👋
            </div>
            <div style={{ fontSize: 18, fontWeight: 800 }}>{displayName}</div>
          </div>
        </div>

        <div className="profile-balance" style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)' }}>
          <div className="balance-amount">{Number(balance).toLocaleString()}</div>
          <div className="balance-label">so'm — Hisobingiz balansi</div>
          <Link to="/profile" className="btn btn-primary btn-sm mt-2" style={{ display: 'inline-flex', marginTop: 12 }}>
            💳 Balans to'ldirish
          </Link>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="section-header mb-4">
        <h2 className="section-title">Tez harakatlar</h2>
      </div>
      <div className="grid-2 mb-6 stagger">
        <Link to="/shop" className="card" style={{ textDecoration: 'none', textAlign: 'center', padding: '20px 12px' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🛍️</div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>Mahsulotlar</div>
          <div className="text-xs text-muted mt-2">Barcha mahsulotlar</div>
        </Link>
        <Link to="/orders" className="card" style={{ textDecoration: 'none', textAlign: 'center', padding: '20px 12px' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📦</div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>Buyurtmalarim</div>
          <div className="text-xs text-muted mt-2">Holat va tarix</div>
        </Link>
        <Link to="/cart" className="card" style={{ textDecoration: 'none', textAlign: 'center', padding: '20px 12px' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🛒</div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>Savat</div>
          <div className="text-xs text-muted mt-2">Tanlangan mahsulotlar</div>
        </Link>
        <Link to="/reviews" className="card" style={{ textDecoration: 'none', textAlign: 'center', padding: '20px 12px' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>⭐</div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>Sharhlar</div>
          <div className="text-xs text-muted mt-2">Fikr qoldiring</div>
        </Link>
      </div>

      {/* Featured Products */}
      <div className="section-header">
        <h2 className="section-title">🔥 Mashhur <span>mahsulotlar</span></h2>
        <Link to="/shop" className="section-link">Barchasi →</Link>
      </div>

      {loadingProducts ? (
        <Spinner text="Mahsulotlar yuklanmoqda..." />
      ) : products.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🛒</div>
          <div className="empty-state-title">Mahsulotlar topilmadi</div>
          <div className="empty-state-desc">Hozircha mahsulotlar mavjud emas</div>
        </div>
      ) : (
        <div className="grid-2 stagger mb-6">
          {products.slice(0, 4).map(p => (
            <ProductMiniCard key={p.id} product={p} />
          ))}
        </div>
      )}

      {/* Recent Orders */}
      {recentOrders.length > 0 && (
        <>
          <div className="section-header">
            <h2 className="section-title">📦 So'nggi <span>buyurtmalar</span></h2>
            <Link to="/orders" className="section-link">Barchasi →</Link>
          </div>
          <div className="stagger">
            {recentOrders.map(order => (
              <RecentOrderRow key={order.id} order={order} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function ProductMiniCard({ product }) {
  const hasImage = product.image_url || product.image_file_id
  const stock = Number(product.stock_grams)
  const stockCls = stock <= 0 ? 'out' : stock < 100 ? 'low' : 'ok'

  return (
    <Link to={`/shop/${product.id}`} className="product-card" style={{ textDecoration: 'none' }}>
      <div className="product-image-placeholder">
        {hasImage ? (
          <img src={product.image_url} alt={product.name} />
        ) : (
          '🍃'
        )}
      </div>
      <div className="product-info">
        <div className="product-name">{product.name}</div>
        <div className="product-price">{Number(product.sale_price_per_gram).toFixed(0)} so'm/g</div>
        <div className={`product-stock ${stockCls}`}>
          {stockCls === 'out' ? '❌ Tugagan' : stockCls === 'low' ? '⚠️ Kam qoldi' : `✅ ${stock.toFixed(0)} g`}
        </div>
      </div>
    </Link>
  )
}

function RecentOrderRow({ order }) {
  const s = STATUS_MAP[order.status] || { label: order.status, cls: 'status-pending', icon: '📋' }
  return (
    <Link to={`/orders/${order.id}`} className="order-card" style={{ textDecoration: 'none' }}>
      <div className="order-header">
        <div className="order-number">№{order.order_number}</div>
        <span className={`status-badge ${s.cls}`}>{s.icon} {s.label}</span>
      </div>
      <div className="flex items-center justify-between">
        <div className="order-date">{new Date(order.created_at).toLocaleDateString('uz-Latn')}</div>
        <div className="order-total">{Number(order.total_amount).toLocaleString()} so'm</div>
      </div>
    </Link>
  )
}
