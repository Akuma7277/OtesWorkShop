import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getMyOrders } from '../api'
import Spinner from '../components/Spinner'

const STATUS_MAP = {
  PENDING_ADMIN:    { label: 'Kutilmoqda', cls: 'status-pending', icon: '⏳' },
  APPROVED:         { label: 'Tasdiqlangan', cls: 'status-approved', icon: '✅' },
  PACKING:          { label: 'Qadoqlanmoqda', cls: 'status-packing', icon: '📦' },
  OUT_FOR_DELIVERY: { label: 'Yetkazilmoqda', cls: 'status-delivery', icon: '🚚' },
  DELIVERED:        { label: 'Yetkazildi', cls: 'status-delivered', icon: '🏁' },
  REJECTED:         { label: 'Rad etildi', cls: 'status-rejected', icon: '❌' },
  CANCELLED:        { label: 'Bekor qilindi', cls: 'status-cancelled', icon: '🚫' },
  REFUNDED:         { label: 'Qaytarildi', cls: 'status-cancelled', icon: '💰' },
  DRAFT:            { label: 'Qoralama', cls: 'status-pending', icon: '📝' },
}

const FILTERS = [
  { key: null, label: 'Barchasi' },
  { key: 'PENDING_ADMIN', label: '⏳ Kutilmoqda' },
  { key: 'APPROVED', label: '✅ Tasdiqlangan' },
  { key: 'OUT_FOR_DELIVERY', label: '🚚 Yetkazilmoqda' },
  { key: 'DELIVERED', label: '🏁 Yetkazildi' },
]

export default function OrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    setLoading(true)
    const params = { page, per_page: 10 }
    if (filter) params.status = filter
    getMyOrders(params)
      .then(data => {
        setOrders(data?.items || data || [])
        setTotalPages(data?.total_pages || 1)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [filter, page])

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column' }}>
      {/* Filter pills */}
      <div className="scroll-x" style={{ padding: '16px 16px 4px' }}>
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
          <Spinner text="Buyurtmalar yuklanmoqda..." />
        ) : orders.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📦</div>
            <div className="empty-state-title">Buyurtmalar topilmadi</div>
            <div className="empty-state-desc">
              {filter ? 'Bu statusdagi buyurtmalar yo\'q' : 'Hali birorta buyurtma bermadingiz'}
            </div>
            {!filter && (
              <Link className="btn btn-primary mt-4" to="/shop">🛍️ Xarid qilish</Link>
            )}
          </div>
        ) : (
          <>
            <div className="stagger">
              {orders.map(order => <OrderCard key={order.id} order={order} />)}
            </div>
            {totalPages > 1 && (
              <div className="flex justify-between items-center mt-4 gap-2">
                <button
                  className="btn btn-secondary btn-sm"
                  disabled={page === 1}
                  onClick={() => setPage(p => p - 1)}
                >← Oldingi</button>
                <span className="text-sm text-muted">{page} / {totalPages}</span>
                <button
                  className="btn btn-secondary btn-sm"
                  disabled={page >= totalPages}
                  onClick={() => setPage(p => p + 1)}
                >Keyingi →</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

function OrderCard({ order }) {
  const s = STATUS_MAP[order.status] || { label: order.status, cls: 'status-pending', icon: '📋' }
  const date = new Date(order.created_at).toLocaleDateString('uz-Latn', {
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
          {order.items?.length || '—'} mahsulot · {order.delivery_address?.slice(0, 30)}...
        </div>
        <div className="order-total">{Number(order.total_amount).toLocaleString()} so'm</div>
      </div>
    </Link>
  )
}
