import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { getProducts, getMyOrders, getNews } from '../api'
import Spinner from '../components/Spinner'
import { t } from '../i18n'
import { haptic } from '../tg'

export default function HomePage() {
  const { user, balance, tgUser, lang } = useApp()
  const [products, setProducts] = useState([])
  const [recentOrders, setRecentOrders] = useState([])
  const [news, setNews] = useState([])
  const [loadingProducts, setLoadingProducts] = useState(true)
  const [loadingOrders, setLoadingOrders] = useState(true)
  const [selectedNews, setSelectedNews] = useState(null)

  const STATUS_MAP = {
    PENDING_ADMIN: { label: t('status_pending'), cls: 'status-pending', icon: '⏳' },
    APPROVED:      { label: t('status_approved'), cls: 'status-approved', icon: '✅' },
    PACKING:       { label: t('status_packing'), cls: 'status-packing', icon: '📦' },
    OUT_FOR_DELIVERY: { label: t('status_delivery'), cls: 'status-delivery', icon: '🚚' },
    DELIVERED:     { label: t('status_delivered'), cls: 'status-delivered', icon: '🏁' },
    REJECTED:      { label: t('status_rejected'), cls: 'status-rejected', icon: '❌' },
    CANCELLED:     { label: t('status_cancelled'), cls: 'status-cancelled', icon: '🚫' },
    REFUNDED:      { label: t('status_refunded'), cls: 'status-cancelled', icon: '💰' },
  }

  useEffect(() => {
    getProducts({ limit: 6, is_active: true })
      .then(data => setProducts(data?.items || data || []))
      .catch(() => {})
      .finally(() => setLoadingProducts(false))

    getMyOrders({ limit: 3 })
      .then(data => setRecentOrders(data?.items || data || []))
      .catch(() => {})
      .finally(() => setLoadingOrders(false))

    getNews()
      .then(data => setNews(data || []))
      .catch(() => {})
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
              {t('welcome')} 👋
            </div>
            <div style={{ fontSize: 18, fontWeight: 800 }}>{displayName}</div>
          </div>
        </div>

        <div className="profile-balance" style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)' }}>
          <div className="balance-amount">{Number(balance).toLocaleString()}</div>
          <div className="balance-label">$ — {t('balance')}</div>
          <Link to="/profile" className="btn btn-gold btn-sm mt-2" style={{ display: 'inline-flex', marginTop: 12, textDecoration: 'none' }}>
            💳 {t('topup_balance')}
          </Link>
        </div>
      </div>

      {/* News / Announcements Widget */}
      {news.length > 0 && (
        <div className="mb-6">
          <div className="section-header mb-3">
            <h2 className="section-title">📰 {t('news')}</h2>
          </div>
          <div className="scroll-x gap-3" style={{ paddingBottom: 8 }}>
            {news.map(item => (
              <div
                key={item.id}
                className="card"
                style={{ width: 240, flexShrink: 0, padding: 12, cursor: 'pointer', background: 'var(--bg-glass)' }}
                onClick={() => { haptic.light(); setSelectedNews(item) }}
              >
                {item.image_url ? (
                  <img src={item.image_url} alt={item.title} style={{ width: '100%', height: 100, objectFit: 'cover', borderRadius: 8, marginBottom: 8 }} />
                ) : (
                  <div style={{ width: '100%', height: 100, background: 'rgba(255,255,255,0.05)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, marginBottom: 8 }}>📢</div>
                )}
                <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 4, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.title}</div>
                <div style={{ fontSize: 11, color: 'var(--text-secondary)', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', height: 32, lineHeight: 1.4 }}>{item.content}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="section-header mb-4">
        <h2 className="section-title">{t('quick_actions')}</h2>
      </div>
      <div className="grid-2 mb-6 stagger">
        <Link to="/shop" className="card" style={{ textDecoration: 'none', textAlign: 'center', padding: '20px 12px' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🛍️</div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>{t('products')}</div>
        </Link>
        <Link to="/orders" className="card" style={{ textDecoration: 'none', textAlign: 'center', padding: '20px 12px' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📦</div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>{t('my_orders')}</div>
        </Link>
        <Link to="/cart" className="card" style={{ textDecoration: 'none', textAlign: 'center', padding: '20px 12px' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🛒</div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>{t('cart')}</div>
        </Link>
        <Link to="/reviews" className="card" style={{ textDecoration: 'none', textAlign: 'center', padding: '20px 12px' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>⭐</div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>{t('reviews')}</div>
        </Link>
      </div>

      {/* Featured Products */}
      <div className="section-header">
        <h2 className="section-title">🔥 {t('featured_products')}</h2>
        <Link to="/shop" className="section-link">{t('all')} →</Link>
      </div>

      {loadingProducts ? (
        <Spinner text="..." />
      ) : products.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🛒</div>
          <div className="empty-state-title">{t('empty_products')}</div>
          <div className="empty-state-desc">{t('no_products_desc')}</div>
        </div>
      ) : (
        <div className="grid-2 stagger mb-6">
          {products.slice(0, 4).map(p => (
            <ProductMiniCard key={p.id} product={p} lang={lang} />
          ))}
        </div>
      )}

      {/* Recent Orders */}
      {recentOrders.length > 0 && (
        <>
          <div className="section-header">
            <h2 className="section-title">📦 {t('recent_orders')}</h2>
            <Link to="/orders" className="section-link">{t('all')} →</Link>
          </div>
          <div className="stagger">
            {recentOrders.map(order => (
              <RecentOrderRow key={order.id} order={order} statusMap={STATUS_MAP} lang={lang} />
            ))}
          </div>
        </>
      )}

      {/* News Lightbox/Modal */}
      {selectedNews && (
        <div
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 9999, padding: 20, backdropFilter: 'blur(10px)'
          }}
          onClick={() => setSelectedNews(null)}
        >
          <div
            className="card scale-in"
            style={{ width: '100%', maxWidth: 400, maxHeight: '80vh', overflowY: 'auto', background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: 20 }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <h3 style={{ fontSize: 18, fontWeight: 800, margin: 0 }}>{selectedNews.title}</h3>
              <button
                className="btn btn-sm"
                style={{ padding: '4px 8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: 'none', borderRadius: '50%' }}
                onClick={() => setSelectedNews(null)}
              >✕</button>
            </div>
            
            {selectedNews.image_url && (
              <img src={selectedNews.image_url} alt="News large" style={{ width: '100%', maxHeight: 200, objectFit: 'contain', borderRadius: 8, marginBottom: 16 }} />
            )}

            <div style={{ fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.6, whiteSpace: 'pre-wrap', marginBottom: 16 }}>
              {selectedNews.content}
            </div>

            <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'right' }}>
              {new Date(selectedNews.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ProductMiniCard({ product, lang }) {
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
        <div className="product-price">{Number(product.sale_price_per_gram).toFixed(0)} $/g</div>
        <div className={`product-stock ${stockCls}`}>
          {stockCls === 'out'
            ? `❌ ${t('stock_none')}`
            : stockCls === 'low'
              ? `⚠️ ${t('stock_low')}`
              : `✅ ${stock.toFixed(0)} g`
          }
        </div>
      </div>
    </Link>
  )
}

function RecentOrderRow({ order, statusMap, lang }) {
  const s = statusMap[order.status] || { label: order.status, cls: 'status-pending', icon: '📋' }
  return (
    <Link to={`/orders/${order.id}`} className="order-card" style={{ textDecoration: 'none' }}>
      <div className="order-header">
        <div className="order-number">№{order.order_number}</div>
        <span className={`status-badge ${s.cls}`}>{s.icon} {s.label}</span>
      </div>
      <div className="flex items-center justify-between">
        <div className="order-date">{new Date(order.created_at).toLocaleDateString(lang === 'ru' ? 'ru-RU' : 'uz-Latn')}</div>
        <div className="order-total">{Number(order.total_amount).toLocaleString()} $</div>
      </div>
    </Link>
  )
}
