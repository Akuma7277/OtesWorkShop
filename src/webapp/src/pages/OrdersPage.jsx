import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getMyOrders } from '../api'
import Spinner from '../components/Spinner'
import { haptic } from '../tg'
import { t, getLanguage } from '../i18n'
import { useApp } from '../context/AppContext'

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

export default function OrdersPage() {
  const { lang } = useApp()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filter, setFilter] = useState(null)

  const FILTERS = [
    { key: null,               label: lang === 'ru' ? 'Все' : 'Barchasi' },
    { key: 'PENDING_ADMIN',    label: lang === 'ru' ? '⏳ Ожидает' : '⏳ Kutilmoqda' },
    { key: 'OUT_FOR_DELIVERY', label: lang === 'ru' ? '🚚 В пути' : '🚚 Yetkazilmoqda' },
    { key: 'DELIVERED',        label: lang === 'ru' ? '🏁 Доставлен' : '🏁 Yetkazildi' },
  ]

  useEffect(() => {
    setLoading(true)
    getMyOrders({ page, status: filter || undefined })
      .then(res => {
        setOrders(res.items || [])
        setTotalPages(res.total_pages || 1)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [page, filter])

  return (
    <div className="page-content fade-in" style={{ paddingBottom: 'var(--nav-height)' }}>
      <div className="section-header mb-4">
        <h1 className="section-title">📦 {t('my_orders')}</h1>
      </div>

      {/* Filter tab bar */}
      <div className="scroll-x mb-4">
        {FILTERS.map(f => (
          <button
            key={String(f.key)}
            className="btn btn-sm"
            style={{ flexShrink: 0, ...(filter === f.key ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
            onClick={() => { setFilter(f.key); setPage(1) }}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="page-content" style={{ paddingTop: 8 }}>
        {loading ? (
          <Spinner text={lang === 'ru' ? 'Загрузка заказов...' : 'Buyurtmalar yuklanmoqda...'} />
        ) : orders.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📦</div>
            <div className="empty-state-title">{lang === 'ru' ? 'Заказы не найдены' : 'Buyurtmalar topilmadi'}</div>
            <div className="empty-state-desc">
              {filter 
                ? (lang === 'ru' ? 'Нет заказов с этим статусом' : 'Bu statusdagi buyurtmalar yo\'q') 
                : t('no_orders_desc')
              }
            </div>
            {!filter && (
              <Link className="btn btn-primary mt-4" to="/shop" style={{ textDecoration: 'none' }}>
                🍀 {lang === 'ru' ? 'В магазин' : 'Xarid qilish'}
              </Link>
            )}
          </div>
        ) : (
          <>
            <div className="stagger">
              {orders.map(order => <OrderCard key={order.id} order={order} lang={lang} />)}
            </div>
            {totalPages > 1 && (
              <div className="flex justify-between items-center mt-4 gap-2">
                <button
                  className="btn btn-secondary btn-sm"
                  disabled={page === 1}
                  onClick={() => setPage(p => p - 1)}
                >{lang === 'ru' ? '← Назад' : '← Oldingi'}</button>
                <span className="text-sm text-muted">{page} / {totalPages}</span>
                <button
                  className="btn btn-secondary btn-sm"
                  disabled={page >= totalPages}
                  onClick={() => setPage(p => p + 1)}
                >{lang === 'ru' ? 'Вперед →' : 'Keyingi →'}</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

function OrderCard({ order, lang }) {
  const s = STATUS_MAP[order.status] || { label: order.status, cls: 'status-pending', icon: '📋' }
  const date = new Date(order.created_at).toLocaleDateString(lang === 'ru' ? 'ru-RU' : 'uz-Latn', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })

  return (
    <Link to={`/orders/${order.id}`} className="order-card" style={{ textDecoration: 'none', display: 'block' }}>
      <div className="order-header">
        <div>
          <div className="order-number">№{order.order_number}</div>
          <div className="order-date">{date}</div>
        </div>
        <span className={`status-badge ${s.cls}`}>{s.icon} {s.label}</span>
      </div>
      <div className="flex justify-between items-center">
        <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
          {order.items?.length || '—'} {lang === 'ru' ? 'товар(ов)' : 'mahsulot'} · {order.delivery_address?.slice(0, 30)}...
        </div>
        <div className="order-total">{Number(order.total_amount).toLocaleString()} $</div>
      </div>
    </Link>
  )
}
