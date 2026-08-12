import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  adminGetDashboard, adminGetOrders, adminApproveOrder, adminRejectOrder,
  adminSetDeliveryStatus, adminGetPendingTopups, adminApproveTopup, adminRejectTopup,
  adminGetUsers, adminApproveUser, adminRejectUser, adminBlockUser, adminUnblockUser,
  adminCreateProduct, adminUpdateProduct, adminDeleteProduct, getProducts,
  adminGetPendingReviews, adminApproveReview, adminRejectReview,
  adminGetSettings, adminUpdateSettings, getCategories
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
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [reviews, setReviews] = useState([])
  const [settings, setSettings] = useState(null)
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
    { key: 'products', label: '🏬' },
    { key: 'reviews', label: '⭐' },
    { key: 'settings', label: '⚙️' },
  ]

  useEffect(() => {
    loadTab()
  }, [tab])

  const loadTab = async () => {
    setLoading(true)
    try {
      if (tab === 'dashboard') setDashboard(await adminGetDashboard())
      if (tab === 'orders') setOrders((await adminGetOrders({ per_page: 30 }))?.items || [])
      if (tab === 'topups') setTopups(await adminGetPendingTopups() || [])
      if (tab === 'users') setUsers((await adminGetUsers({ per_page: 30 }))?.items || [])
      if (tab === 'products') {
        const prodData = await getProducts({ is_active: true, limit: 100 })
        const catData = await getCategories()
        setProducts(prodData?.items || prodData || [])
        setCategories(catData || [])
      }
      if (tab === 'reviews') setReviews(await adminGetPendingReviews() || [])
      if (tab === 'settings') setSettings(await adminGetSettings() || null)
    } catch {}
    setLoading(false)
  }

  return (
    <div className="page-content fade-in">
      <div className="section-header mb-4">
        <h1 className="section-title">🛠 Admin <span>Panel</span></h1>
      </div>

      {/* Tab bar */}
      <div className="scroll-x mb-4">
        {tabs.map(t => (
          <button
            key={t.key}
            className="btn btn-sm"
            style={{ flexShrink: 0, fontSize: 18, ...(tab === t.key ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
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
          {tab === 'products' && <ProductsTab products={products} categories={categories} reload={loadTab} />}
          {tab === 'reviews' && <ReviewsTab reviews={reviews} reload={loadTab} />}
          {tab === 'settings' && settings && <SettingsTab initialSettings={settings} reload={loadTab} />}
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
    <div className="empty-state"><div className="empty-state-icon">✅</div><div className="empty-state-title">Buyurtmalar yo'q</div></div>
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
  const [zoomedImage, setZoomedImage] = useState(null)

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
    <div className="empty-state"><div className="empty-state-icon">✅</div><div className="empty-state-title">To'ldirish so'rovlari yo'q</div></div>
  )

  return (
    <div className="stagger">
      {topups.map(t => (
        <div key={t.id} className="card mb-3">
          <div className="flex justify-between items-center mb-2">
            <div style={{ fontWeight: 700, fontSize: 16 }}>{Number(t.amount).toLocaleString()} so'm</div>
            <span className="status-badge status-pending">⏳ Kutilmoqda</span>
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>
            👤 {t.user_name || 'Foydalanuvchi'} (ID: {t.user_id}) · {t.payment_method}
          </div>

          {/* Receipt image preview */}
          {t.receipt_file_id && t.receipt_file_id.startsWith('data:image/') && (
            <div className="mb-3" style={{ cursor: 'pointer', borderRadius: 8, overflow: 'hidden', border: '1px solid var(--border)', background: '#000', maxHeight: 150 }}>
              <img
                src={t.receipt_file_id}
                alt="Receipt screenshot"
                style={{ width: '100%', height: 150, objectFit: 'contain' }}
                onClick={() => { haptic.light(); setZoomedImage(t.receipt_file_id) }}
              />
            </div>
          )}

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

      {/* Lightbox / Zoomed image modal */}
      {zoomedImage && (
        <div
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.95)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 9999, padding: 16
          }}
          onClick={() => setZoomedImage(null)}
        >
          <img src={zoomedImage} alt="Zoomed check" style={{ maxWidth: '100%', maxHeight: '90%', objectFit: 'contain', borderRadius: 8 }} />
          <div style={{ position: 'absolute', top: 20, right: 20, color: '#fff', fontSize: 24, fontWeight: 700, cursor: 'pointer' }}>✕</div>
        </div>
      )}
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
    <div className="empty-state"><div className="empty-state-icon">👥</div><div className="empty-state-title">Foydalanuvchilar topilmadi</div></div>
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
            {u.status === 'PENDING' ? (
              <>
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
              </>
            ) : u.status === 'APPROVED' ? (
              <button
                className="btn btn-danger btn-sm btn-full"
                disabled={processing[u.id]}
                onClick={() => action(() => adminBlockUser(u.id), u.id, 'Foydalanuvchi bloklandi')}
              >
                🚫 Bloklash
              </button>
            ) : (
              <button
                className="btn btn-success btn-sm btn-full"
                disabled={processing[u.id]}
                onClick={() => action(() => adminUnblockUser(u.id), u.id, 'Foydalanuvchi blokdan chiqarildi')}
              >
                ✅ Blokdan chiqarish
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

function ProductsTab({ products, categories, reload }) {
  const { showToast } = useApp()
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [formData, setFormData] = useState({
    name: '', sale_price: '', cost_price: '', initial_stock: '', low_stock_threshold: '10', description: '', category_id: ''
  })
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.name || !formData.sale_price) {
      showToast('❌ Nom va sotuv narxi majburiy!')
      return
    }
    haptic.medium()
    setSubmitting(true)
    try {
      if (editingProduct) {
        await adminUpdateProduct(editingProduct.id, {
          name: formData.name,
          sale_price_per_gram: Number(formData.sale_price),
          cost_price_per_gram: Number(formData.cost_price),
          stock_grams: Number(formData.initial_stock),
          low_stock_threshold_grams: Number(formData.low_stock_threshold),
          description: formData.description,
          category_id: Number(formData.category_id)
        })
        showToast('✅ Mahsulot yangilandi')
      } else {
        await adminCreateProduct(formData)
        showToast('✅ Mahsulot yaratildi')
      }
      setShowAddForm(false)
      setEditingProduct(null)
      setFormData({ name: '', sale_price: '', cost_price: '', initial_stock: '', low_stock_threshold: '10', description: '', category_id: '' })
      reload()
    } catch (err) {
      showToast(`❌ ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm("Mahsulotni o'chirishni tasdiqlaysizmi?")) return
    haptic.warning()
    try {
      await adminDeleteProduct(id)
      showToast("✅ Mahsulot o'chirildi / deaktiv qilindi")
      reload()
    } catch (err) {
      showToast(`❌ ${err.message}`)
    }
  }

  return (
    <div className="stagger">
      <button className="btn btn-primary btn-full mb-4" onClick={() => { haptic.light(); setShowAddForm(!showAddForm); setEditingProduct(null) }}>
        {showAddForm ? '❌ Shaklni yopish' : '➕ Yangi mahsulot qo\'shish'}
      </button>

      {showAddForm && (
        <form onSubmit={handleSubmit} className="card mb-4 stagger">
          <div className="input-group">
            <label className="input-label">Nomi</label>
            <input className="input" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
          </div>
          <div className="grid-2">
            <div className="input-group">
              <label className="input-label">Sotuv narxi (1g uchun)</label>
              <input type="number" className="input" value={formData.sale_price} onChange={e => setFormData({...formData, sale_price: e.target.value})} required />
            </div>
            <div className="input-group">
              <label className="input-label">Tannarxi (1g uchun)</label>
              <input type="number" className="input" value={formData.cost_price} onChange={e => setFormData({...formData, cost_price: e.target.value})} />
            </div>
          </div>
          <div className="grid-2">
            <div className="input-group">
              <label className="input-label">Zaxira (gramm)</label>
              <input type="number" className="input" value={formData.initial_stock} onChange={e => setFormData({...formData, initial_stock: e.target.value})} />
            </div>
            <div className="input-group">
              <label className="input-label">Minimal chegara (g)</label>
              <input type="number" className="input" value={formData.low_stock_threshold} onChange={e => setFormData({...formData, low_stock_threshold: e.target.value})} />
            </div>
          </div>
          <div className="input-group">
            <label className="input-label">Kategoriya</label>
            <select className="input" value={formData.category_id} onChange={e => setFormData({...formData, category_id: e.target.value})}>
              <option value="">Tanlang...</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="input-group">
            <label className="input-label">Tavsif</label>
            <textarea className="input" rows={3} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} />
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={submitting}>
            {submitting ? '⏳ Saqlanmoqda...' : '💾 Saqlash'}
          </button>
        </form>
      )}

      {products.map(p => (
        <div key={p.id} className="card mb-3 flex items-center justify-between">
          <div>
            <div style={{ fontWeight: 700 }}>{p.name}</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              Sotuv: {Number(p.sale_price_per_gram).toFixed(0)} so'm · Zaxira: {Number(p.stock_grams).toFixed(0)} g
            </div>
          </div>
          <div className="flex gap-2">
            <button className="btn btn-secondary btn-sm" onClick={() => {
              haptic.light()
              setEditingProduct(p)
              setFormData({
                name: p.name,
                sale_price: String(p.sale_price_per_gram),
                cost_price: String(p.cost_price_per_gram || ''),
                initial_stock: String(p.stock_grams),
                low_stock_threshold: String(p.low_stock_threshold_grams || '10'),
                description: p.description || '',
                category_id: String(p.category_id || '')
              })
              setShowAddForm(true)
            }}>✏️</button>
            <button className="btn btn-danger btn-sm" onClick={() => handleDelete(p.id)}>🗑️</button>
          </div>
        </div>
      ))}
    </div>
  )
}

function ReviewsTab({ reviews, reload }) {
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

  if (reviews.length === 0) return (
    <div className="empty-state"><div className="empty-state-icon">⭐</div><div className="empty-state-title">Kutilayotgan sharhlar yo'q</div></div>
  )

  return (
    <div className="stagger">
      {reviews.map(r => (
        <div key={r.id} className="card mb-3">
          <div className="flex justify-between items-center mb-2">
            <div style={{ fontWeight: 700 }}>{r.user?.full_name || 'Foydalanuvchi'}</div>
            <div className="stars">{'⭐'.repeat(r.rating)}</div>
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>
            "{r.text}"
          </div>
          <div className="flex gap-2">
            <button
              className="btn btn-success btn-sm"
              style={{ flex: 1 }}
              disabled={processing[r.id]}
              onClick={() => action(() => adminApproveReview(r.id), r.id, 'Sharh tasdiqlandi')}
            >Approve</button>
            <button
              className="btn btn-danger btn-sm"
              style={{ flex: 1 }}
              disabled={processing[r.id]}
              onClick={() => action(() => adminRejectReview(r.id), r.id, 'Sharh rad etildi')}
            >Reject</button>
          </div>
        </div>
      ))}
    </div>
  )
}

function SettingsTab({ initialSettings, reload }) {
  const { showToast } = useApp()
  const [settings, setSettings] = useState(initialSettings)
  const [submitting, setSubmitting] = useState(false)

  const handleSave = async (e) => {
    e.preventDefault()
    haptic.medium()
    setSubmitting(true)
    try {
      await adminUpdateSettings(settings)
      haptic.success()
      showToast('✅ Sozlamalar saqlandi!')
      reload()
    } catch (e) {
      haptic.error()
      showToast(`❌ ${e.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSave} className="card stagger">
      <div className="input-group">
        <label className="input-label">Minimal yosh</label>
        <input type="number" className="input" value={settings.min_user_age} onChange={e => setSettings({...settings, min_user_age: parseInt(e.target.value)})} />
      </div>
      <div className="input-group">
        <label className="input-label">Maksimal yosh</label>
        <input type="number" className="input" value={settings.max_user_age} onChange={e => setSettings({...settings, max_user_age: parseInt(e.target.value)})} />
      </div>
      <div className="input-group">
        <label className="input-label">Minimal to'lov (so'm)</label>
        <input type="number" className="input" value={settings.min_topup_amount} onChange={e => setSettings({...settings, min_topup_amount: parseFloat(e.target.value)})} />
      </div>
      <div className="input-group">
        <label className="input-label">Yetkazib berish SLA (soat)</label>
        <input type="number" className="input" value={settings.delivery_sla_hours} onChange={e => setSettings({...settings, delivery_sla_hours: parseInt(e.target.value)})} />
      </div>
      <div className="input-group">
        <label className="input-label">Kam qoldiq haqida xabar (soat)</label>
        <input type="number" className="input" value={settings.low_stock_notify_interval_hours} onChange={e => setSettings({...settings, low_stock_notify_interval_hours: parseInt(e.target.value)})} />
      </div>
      <div className="input-group">
        <label className="input-label">Operator kontakti</label>
        <input className="input" value={settings.operator_contact} onChange={e => setSettings({...settings, operator_contact: e.target.value})} />
      </div>
      <div className="input-group">
        <label className="input-label">LTC hamyon</label>
        <input className="input" value={settings.ltc_wallet_address} onChange={e => setSettings({...settings, ltc_wallet_address: e.target.value})} />
      </div>
      <div className="input-group">
        <label className="input-label">USDT hamyon</label>
        <input className="input" value={settings.usdt_wallet_address} onChange={e => setSettings({...settings, usdt_wallet_address: e.target.value})} />
      </div>
      <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={submitting}>
        {submitting ? '⏳ Saqlanmoqda...' : '💾 Sozlamalarni saqlash'}
      </button>
    </form>
  )
}
