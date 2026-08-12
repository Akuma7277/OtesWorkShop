import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  adminGetDashboard, adminGetOrders, adminApproveOrder, adminRejectOrder,
  adminSetDeliveryStatus, adminGetPendingTopups, adminApproveTopup, adminRejectTopup,
  adminGetUsers, adminApproveUser, adminRejectUser,
} from '../api'
import { useApp } from '../context/AppContext'
import Spinner from '../components/Spinner'
import { haptic } from '../tg'

const STATUS_MAP = {
  PENDING_ADMIN:    { label: 'Kutilmoqda',    cls: 'status-pending',  icon: '⏳' },
  APPROVED:         { label: 'Tasdiqlangan',  cls: 'status-approved', icon: '✅' },
  PACKING:          { label: 'Qadoqlanmoqda', cls: 'status-packing',  icon: '📦' },
  OUT_FOR_DELIVERY: { label: 'Yetkazilmoqda', cls: 'status-delivery', icon: '🚚' },
  DELIVERED:        { label: 'Yetkazildi',    cls: 'status-delivered',icon: '🏁' },
  REJECTED:         { label: 'Rad etildi',    cls: 'status-rejected', icon: '❌' },
  CANCELLED:        { label: 'Bekor qilindi', cls: 'status-cancelled',icon: '🚫' },
}

const DELIVERY_NEXT = {
  APPROVED: 'PACKING', PACKING: 'OUT_FOR_DELIVERY', OUT_FOR_DELIVERY: 'DELIVERED'
}
const DELIVERY_NEXT_LABEL = {
  APPROVED: '📦 Qadoqlashga o\'tkazish',
  PACKING: '🚚 Yetkazishga yuborish',
  OUT_FOR_DELIVERY: '🏁 Yetkazildi deb belgilash',
}

export default function AdminPage() {
  const { isAdmin } = useApp()
  const [tab, setTab] = useState('dashboard')
  const [dashboard, setDashboard] = useState(null)
  const [orders, setOrders] = useState([])
  const [topups, setTopups] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)

  if (!isAdmin) {
    return (
      <div className="page-content fade-in">
        <div className="empty-state">
          <div className="empty-state-icon">🔒</div>
          <div className="empty-state-title">Kirish taqiqlangan</div>
          <div className="empty-state-desc">Bu sahifa faqat adminlar uchun</div>
        </div>
      </div>
    )
  }

  const tabs = [
    { key: 'dashboard', label: '📊' },
    { key: 'orders', label: '📦' },
    { key: 'topups', label: '💳' },
    { key: 'users', label: '👥' },
  ]

  useEffect(() => {
    loadTab()
  }, [tab])

  const loadTab = async () => {
    setLoading(true)
    try {
      if (tab === 'dashboard') setDashboard(await adminGetDashboard())
      if (tab === 'orders') setOrders((await adminGetOrders({ status: 'PENDING_ADMIN', per_page: 20 }))?.items || [])
      if (tab === 'topups') setTopups(await adminGetPendingTopups() || [])
      if (tab === 'users') setUsers((await adminGetUsers({ status: 'PENDING', per_page: 20 }))?.items || [])
    } catch {}
    setLoading(false)
  }

  return (
    <div className="page-content fade-in">
      <div className="section-header mb-4">
        <h1 className="section-title">🛠 Admin <span>Panel</span></h1>
      </div>

      {/* Tab bar */}
      <div className="flex gap-2 mb-4">
        {tabs.map(t => (
          <button
            key={t.key}
            className="btn btn-sm"
            style={{ flex: 1, fontSize: 18, ...(tab === t.key ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
            onClick={() => { haptic.light(); setTab(t.key) }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading ? <Spinner /> : (
        <>
          {tab === 'dashboard' && dashboard && <DashboardTab d={dashboard} />}
          {tab === 'orders' && <OrdersTab orders={orders} reload={loadTab} />}
          {tab === 'topups' && <TopupsTab topups={topups} reload={loadTab} />}
          {tab === 'users' && <UsersTab users={users} reload={loadTab} />}
        </>
      )}
    </div>
  )
}

function DashboardTab({ d }) {
  return (
    <div className="stagger">
      <div className="stats-grid mb-4">
        <StatCard icon="📦" value={d.orders_today_count} label="Bugungi buyurtmalar" />
        <StatCard icon="💰" value={`${Number(d.revenue_today || 0).toLocaleString()} s`} label="Bugungi daromad" />
        <StatCard icon="⏳" value={d.pending_orders_count} label="Kutilayotgan" />
        <StatCard icon="👥" value={d.active_users_count} label="Faol foydalanuvchilar" />
        <StatCard icon="📋" value={d.pending_registrations_count} label="Yangi arizalar" />
        <StatCard icon="💳" value={d.pending_topups_count} label="To'ldirish so'rovlari" />
        <StatCard icon="📈" value={d.total_orders_count} label="Jami buyurtmalar" />
        <StatCard icon="⚠️" value={d.low_stock_products_count} label="Kam qolgan mahsulotlar" />
      </div>
    </div>
  )
}

function StatCard({ icon, value, label }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

function OrdersTab({ orders, reload }) {
  const { showToast } = useApp()
  const [processing, setProcessing] = useState({})

  const action = async (fn, id, label) => {
    haptic.medium()
    setProcessing(p => ({ ...p, [id]: true }))
    try {
      await fn()
      haptic.success()
      showToast(`✅ ${label}`)
      reload()
    } catch (e) {
      haptic.error()
      showToast(`❌ ${e.message}`)
    }
    setProcessing(p => ({ ...p, [id]: false }))
  }

  if (orders.length === 0) return (
    <div className="empty-state"><div className="empty-state-icon">✅</div><div className="empty-state-title">Kutilayotgan buyurtmalar yo'q</div></div>
  )

  return (
    <div className="stagger">
      {orders.map(order => {
        const s = STATUS_MAP[order.status] || {}
        const busy = processing[order.id]
        const nextStatus = DELIVERY_NEXT[order.status]
        return (
          <div key={order.id} className="card mb-3">
            <div className="flex justify-between items-center mb-2">
              <div className="order-number">№{order.order_number}</div>
              <span className={`status-badge ${s.cls}`}>{s.icon} {s.label}</span>
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>
              👤 {order.user?.full_name || '—'} · {Number(order.total_amount).toLocaleString()} so'm
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
              📍 {order.delivery_address}
            </div>
            <div className="flex gap-2">
              {order.status === 'PENDING_ADMIN' && (
                <>
                  <button
                    className="btn btn-success btn-sm"
                    style={{ flex: 1 }}
                    disabled={busy}
                    onClick={() => action(() => adminApproveOrder(order.id), order.id, 'Buyurtma tasdiqlandi')}
                  >
                    ✅ Tasdiqlash
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    style={{ flex: 1 }}
                    disabled={busy}
                    onClick={() => action(() => adminRejectOrder(order.id, 'Admin tomonidan rad etildi'), order.id, 'Rad etildi')}
                  >
                    ❌ Rad
                  </button>
                </>
              )}
              {nextStatus && (
                <button
                  className="btn btn-primary btn-sm btn-full"
                  disabled={busy}
                  onClick={() => action(() => adminSetDeliveryStatus(order.id, nextStatus), order.id, 'Holat yangilandi')}
                >
                  {DELIVERY_NEXT_LABEL[order.status] || 'Keyingi holat'}
                </button>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function TopupsTab({ topups, reload }) {
  const { showToast } = useApp()
  const [processing, setProcessing] = useState({})

  const action = async (fn, id, label) => {
    haptic.medium()
    setProcessing(p => ({ ...p, [id]: true }))
    try {
      await fn()
      haptic.success()
      showToast(`✅ ${label}`)
      reload()
    } catch (e) {
      haptic.error()
      showToast(`❌ ${e.message}`)
    }
    setProcessing(p => ({ ...p, [id]: false }))
  }

  if (topups.length === 0) return (
    <div className="empty-state"><div className="empty-state-icon">✅</div><div className="empty-state-title">Kutilayotgan to'ldirish so'rovlari yo'q</div></div>
  )

  return (
    <div className="stagger">
      {topups.map(t => (
        <div key={t.id} className="card mb-3">
          <div className="flex justify-between items-center mb-2">
            <div style={{ fontWeight: 700 }}>{Number(t.amount).toLocaleString()} so'm</div>
            <span className="status-badge status-pending">⏳ Kutilmoqda</span>
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>
            👤 Foydalanuvchi ID: {t.user_id} · {t.payment_method}
          </div>
          <div className="flex gap-2">
            <button
              className="btn btn-success btn-sm"
              style={{ flex: 1 }}
              disabled={processing[t.id]}
              onClick={() => action(() => adminApproveTopup(t.id), t.id, 'To\'ldirish tasdiqlandi')}
            >✅ Tasdiqlash</button>
            <button
              className="btn btn-danger btn-sm"
              style={{ flex: 1 }}
              disabled={processing[t.id]}
              onClick={() => action(() => adminRejectTopup(t.id, 'Admin tomonidan rad etildi'), t.id, 'Rad etildi')}
            >❌ Rad</button>
          </div>
        </div>
      ))}
    </div>
  )
}

function UsersTab({ users, reload }) {
  const { showToast } = useApp()
  const [processing, setProcessing] = useState({})

  const action = async (fn, id, label) => {
    haptic.medium()
    setProcessing(p => ({ ...p, [id]: true }))
    try {
      await fn()
      haptic.success()
      showToast(`✅ ${label}`)
      reload()
    } catch (e) {
      haptic.error()
      showToast(`❌ ${e.message}`)
    }
    setProcessing(p => ({ ...p, [id]: false }))
  }

  if (users.length === 0) return (
    <div className="empty-state"><div className="empty-state-icon">✅</div><div className="empty-state-title">Kutilayotgan ro'yxatdan o'tish arizalari yo'q</div></div>
  )

  return (
    <div className="stagger">
      {users.map(u => (
        <div key={u.id} className="card mb-3">
          <div className="flex items-center gap-3 mb-3">
            <div className="profile-avatar" style={{ width: 44, height: 44, fontSize: 16 }}>
              {(u.full_name || '?').split(' ').map(w => w[0]).join('').slice(0, 2)}
            </div>
            <div>
              <div style={{ fontWeight: 700 }}>{u.full_name}</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                {u.username ? `@${u.username}` : 'username yo\'q'} · {u.age} yosh
              </div>
            </div>
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>📍 {u.address}</div>
          <div className="flex gap-2">
            <button
              className="btn btn-success btn-sm"
              style={{ flex: 1 }}
              disabled={processing[u.id]}
              onClick={() => action(() => adminApproveUser(u.id), u.id, 'Foydalanuvchi tasdiqlandi')}
            >✅ Qabul</button>
            <button
              className="btn btn-danger btn-sm"
              style={{ flex: 1 }}
              disabled={processing[u.id]}
              onClick={() => action(() => adminRejectUser(u.id, 'Rad etildi'), u.id, 'Rad etildi')}
            >❌ Rad</button>
          </div>
        </div>
      ))}
    </div>
  )
}
