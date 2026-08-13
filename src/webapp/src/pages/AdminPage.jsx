import { useEffect, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import {
  adminGetDashboard, adminGetOrders, adminApproveOrder, adminRejectOrder,
  adminSetDeliveryStatus, adminGetPendingTopups, adminApproveTopup, adminRejectTopup,
  adminGetUsers, adminApproveUser, adminRejectUser, adminBlockUser, adminUnblockUser,
  adminCreateProduct, adminUpdateProduct, adminDeleteProduct, getProducts,
  adminGetPendingReviews, adminApproveReview, adminRejectReview,
  adminGetSettings, adminUpdateSettings, getCategories,
  getNews, adminCreateNews, adminDeleteNews,
  adminGetChatRooms, adminGetRoomMessages, adminSendRoomMessage
} from '../api'
import { useApp } from '../context/AppContext'
import Spinner from '../components/Spinner'
import { haptic } from '../tg'
import { setLanguage } from '../i18n'


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
  const { isAdmin, lang } = useApp()
  const [tab, setTab] = useState('dashboard')
  const [dashboard, setDashboard] = useState(null)
  const [orders, setOrders] = useState([])
  const [topups, setTopups] = useState([])
  const [users, setUsers] = useState([])
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [reviews, setReviews] = useState([])
  const [newsList, setNewsList] = useState([])
  const [settings, setSettings] = useState(null)
  const [chatRooms, setChatRooms] = useState([])
  const [loading, setLoading] = useState(false)

  if (!isAdmin) {
    return (
      <div className="page-content fade-in">
        <div className="empty-state">
          <div className="empty-state-icon">🔒</div>
          <div className="empty-state-title">{lang === 'ru' ? 'Доступ запрещен' : 'Kirish taqiqlangan'}</div>
          <div className="empty-state-desc">{lang === 'ru' ? 'Эта страница только для администраторов' : 'Bu sahifa faqat adminlar uchun'}</div>
        </div>
      </div>
    )
  }

  const tabs = [
    { key: 'dashboard', label: '📊 ' + (lang === 'ru' ? 'Панель' : 'Panel') },
    { key: 'orders', label: '📦 ' + (lang === 'ru' ? 'Заказы' : 'Buyurtmalar') },
    { key: 'chat', label: '💬 ' + (lang === 'ru' ? 'Чат' : 'Chat') },
    { key: 'topups', label: '💳 ' + (lang === 'ru' ? 'Оплаты' : 'To\'lovlar') },
    { key: 'users', label: '👥 ' + (lang === 'ru' ? 'Клиенты' : 'Mijozlar') },
    { key: 'products', label: '🏬 ' + (lang === 'ru' ? 'Товары' : 'Mahsulotlar') },
    { key: 'reviews', label: '⭐ ' + (lang === 'ru' ? 'Отзывы' : 'Sharhlar') },
    { key: 'news', label: '📰 ' + (lang === 'ru' ? 'Новости' : 'E\'lonlar') },
    { key: 'settings', label: '⚙️ ' + (lang === 'ru' ? 'Настройки' : 'Sozlamalar') },
  ]

  useEffect(() => {
    loadTab()
  }, [tab])

  const loadTab = async () => {
    setLoading(true)
    try {
      if (tab === 'dashboard') setDashboard(await adminGetDashboard())
      if (tab === 'orders') setOrders((await adminGetOrders({ per_page: 30 }))?.items || [])
      if (tab === 'chat') setChatRooms(await adminGetChatRooms() || [])
      if (tab === 'topups') setTopups(await adminGetPendingTopups() || [])
      if (tab === 'users') setUsers((await adminGetUsers({ per_page: 30 }))?.items || [])
      if (tab === 'products') {
        const prodData = await getProducts({ is_active: true, limit: 100 })
        const catData = await getCategories()
        setProducts(prodData?.items || prodData || [])
        setCategories(catData || [])
      }
      if (tab === 'reviews') setReviews(await adminGetPendingReviews() || [])
      if (tab === 'news') setNewsList(await getNews() || [])
      if (tab === 'settings') setSettings(await adminGetSettings() || null)
    } catch {}
    setLoading(false)
  }

  return (
    <div className="page-content fade-in">
      <div className="section-header mb-4" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 className="section-title">🛠 Admin <span>{lang === 'ru' ? 'Панель' : 'Panel'}</span></h1>
        <div style={{ display: 'flex', gap: 6 }}>
          <button
            type="button"
            className={`btn btn-sm ${lang === 'uz' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '4px 10px', minWidth: 40, borderRadius: 8, fontSize: 12, fontWeight: 700 }}
            onClick={() => { haptic.light(); setLanguage('uz') }}
          >
            UZ
          </button>
          <button
            type="button"
            className={`btn btn-sm ${lang === 'ru' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '4px 10px', minWidth: 40, borderRadius: 8, fontSize: 12, fontWeight: 700 }}
            onClick={() => { haptic.light(); setLanguage('ru') }}
          >
            RU
          </button>
        </div>
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
          {tab === 'chat' && <ChatTab rooms={chatRooms} reload={loadTab} />}
          {tab === 'topups' && <TopupsTab topups={topups} reload={loadTab} />}
          {tab === 'users' && <UsersTab users={users} reload={loadTab} />}
          {tab === 'products' && <ProductsTab products={products} categories={categories} reload={loadTab} />}
          {tab === 'reviews' && <ReviewsTab reviews={reviews} reload={loadTab} />}
          {tab === 'news' && <NewsTab newsList={newsList} reload={loadTab} />}
          {tab === 'settings' && settings && <SettingsTab initialSettings={settings} reload={loadTab} />}
        </>
      )}
    </div>
  )
}

function DashboardTab({ d }) {
  const { lang } = useApp()
  return (
    <div className="stagger">
      <div className="stats-grid mb-4">
        <StatCard icon="📦" value={d.orders_today_count} label={lang === 'ru' ? 'Заказы сегодня' : 'Bugungi buyurtmalar'} />
        <StatCard icon="💰" value={`${Number(d.revenue_today || 0).toFixed(1)} $`} label={lang === 'ru' ? 'Доход сегодня' : 'Bugungi daromad'} />
        <StatCard icon="⏳" value={d.pending_orders_count} label={lang === 'ru' ? 'Ожидают' : 'Kutilayotgan'} />
        <StatCard icon="👥" value={d.active_users_count} label={lang === 'ru' ? 'Активные юзеры' : 'Faol foydalanuvchilar'} />
        <StatCard icon="📋" value={d.pending_registrations_count} label={lang === 'ru' ? 'Новые заявки' : 'Yangi arizalar'} />
        <StatCard icon="💳" value={d.pending_topups_count} label={lang === 'ru' ? 'Запросы оплат' : 'To\'ldirish so\'rovlari'} />
        <StatCard icon="📈" value={d.total_orders_count} label={lang === 'ru' ? 'Всего заказано' : 'Jami buyurtmalar'} />
        <StatCard icon="⚠️" value={d.low_stock_products_count} label={lang === 'ru' ? 'Мало товара' : 'Kam qolgan mahsulotlar'} />
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

const getStatusLabel = (status, lang) => {
  const labels = {
    PENDING_ADMIN:    { uz: 'Kutilmoqda', ru: 'Ожидает' },
    APPROVED:         { uz: 'Tasdiqlangan', ru: 'Подтвержден' },
    PACKING:          { uz: 'Qadoqlanmoqda', ru: 'Собирается' },
    OUT_FOR_DELIVERY: { uz: 'Yetkazilmoqda', ru: 'В пути' },
    DELIVERED:        { uz: 'Yetkazildi', ru: 'Доставлен' },
    REJECTED:         { uz: 'Rad etildi', ru: 'Отклонен' },
    CANCELLED:        { uz: 'Bekor qilindi', ru: 'Отменен' },
  }
  return labels[status]?.[lang] || labels[status]?.['uz'] || status
}

const getDeliveryNextLabel = (status, lang) => {
  const labels = {
    APPROVED: { uz: '📦 Qadoqlashga o\'tkazish', ru: '📦 Начать сборку' },
    PACKING: { uz: '🚚 Yetkazishga yuborish', ru: '🚚 Отправить доставку' },
    OUT_FOR_DELIVERY: { uz: '🏁 Yetkazildi deb belgilash', ru: '🏁 Отметить как доставлен' },
  }
  return labels[status]?.[lang] || labels[status]?.['uz'] || status
}

function OrdersTab({ orders, reload }) {
  const { showToast, lang } = useApp()
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
    <div className="empty-state">
      <div className="empty-state-icon">✅</div>
      <div className="empty-state-title">{lang === 'ru' ? 'Нет заказов' : 'Buyurtmalar yo\'q'}</div>
    </div>
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
              <span className={`status-badge ${s.cls}`}>{s.icon} {getStatusLabel(order.status, lang)}</span>
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>
              👤 {order.user?.full_name || '—'} · {Number(order.total_amount).toFixed(1)} $
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
              📍 {lang === 'ru' ? 'Район получения' : 'Olib ketish tumani'}: {order.delivery_address}
            </div>
            <div className="flex gap-2">
              {order.status === 'PENDING_ADMIN' && (
                <>
                  <button
                    className="btn btn-success btn-sm"
                    style={{ flex: 1 }}
                    disabled={busy}
                    onClick={() => action(() => adminApproveOrder(order.id), order.id, lang === 'ru' ? 'Заказ подтвержден' : 'Buyurtma tasdiqlandi')}
                  >
                    ✅ {lang === 'ru' ? 'Одобрить' : 'Tasdiqlash'}
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    style={{ flex: 1 }}
                    disabled={busy}
                    onClick={() => action(() => adminRejectOrder(order.id, 'Admin tomonidan rad etildi'), order.id, lang === 'ru' ? 'Отклонено' : 'Rad etildi')}
                  >
                    ❌ {lang === 'ru' ? 'Отклонить' : 'Rad etish'}
                  </button>
                </>
              )}
              {nextStatus && (
                <button
                  className="btn btn-primary btn-sm btn-full"
                  disabled={busy}
                  onClick={() => action(() => adminSetDeliveryStatus(order.id, nextStatus), order.id, lang === 'ru' ? 'Статус обновлен' : 'Holat yangilandi')}
                >
                  {getDeliveryNextLabel(order.status, lang)}
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
  const { showToast, lang } = useApp()
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
    <div className="empty-state">
      <div className="empty-state-icon">✅</div>
      <div className="empty-state-title">{lang === 'ru' ? 'Нет запросов на пополнение' : 'To\'ldirish so\'rovlari yo\'q'}</div>
    </div>
  )

  return (
    <div className="stagger">
      {topups.map(t => (
        <div key={t.id} className="card mb-3">
          <div className="flex justify-between items-center mb-2">
            <div style={{ fontWeight: 700, fontSize: 16 }}>{Number(t.amount).toFixed(1)} $</div>
            <span className="status-badge status-pending">{lang === 'ru' ? '⏳ Ожидает' : '⏳ Kutilmoqda'}</span>
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>
            👤 {t.user_name || (lang === 'ru' ? 'Пользователь' : 'Foydalanuvchi')} (ID: {t.user_id}) · {t.payment_method}
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
              onClick={() => action(() => adminApproveTopup(t.id), t.id, lang === 'ru' ? 'Пополнение одобрено' : 'To\'ldirish tasdiqlandi')}
            >✅ {lang === 'ru' ? 'Одобрить' : 'Tasdiqlash'}</button>
            <button
              className="btn btn-danger btn-sm"
              style={{ flex: 1 }}
              disabled={processing[t.id]}
              onClick={() => action(() => adminRejectTopup(t.id, 'Admin tomonidan rad etildi'), t.id, lang === 'ru' ? 'Отклонено' : 'Rad etildi')}
            >❌ {lang === 'ru' ? 'Отклонить' : 'Rad etish'}</button>
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
                {u.username ? `@${u.username}` : 'username yo\'q'} · {u.age ? `${u.age} yosh` : "yoshi noma'lum"}
              </div>
            </div>
          </div>
          {u.address && u.address !== 'Tashkent' && <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>📍 {u.address}</div>}
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
    name: '', sale_price: '', cost_price: '', initial_stock: '', low_stock_threshold: '10', description: '', category_id: '', image_url: ''
  })
  const [submitting, setSubmitting] = useState(false)

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    if (file.size > 8 * 1024 * 1024) {
      showToast('❌ Rasm hajmi 8MB dan oshmasligi kerak')
      return
    }
    const reader = new FileReader()
    reader.onloadend = () => {
      setFormData(prev => ({ ...prev, image_url: reader.result }))
      showToast('✅ Rasm muvaffaqiyatli yuklandi!')
    }
    reader.readAsDataURL(file)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.name || !formData.sale_price) {
      showToast('❌ Nom va sotuv narxi majburiy!')
      return
    }
    if (!editingProduct && !formData.image_url) {
      showToast('❌ Mahsulot rasmini yuklash majburiy!')
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
          category_id: formData.category_id ? Number(formData.category_id) : null,
          image_url: formData.image_url
        })
        showToast('✅ Mahsulot yangilandi')
      } else {
        await adminCreateProduct(formData)
        showToast('✅ Mahsulot yaratildi')
      }
      setShowAddForm(false)
      setEditingProduct(null)
      setFormData({ name: '', sale_price: '', cost_price: '', initial_stock: '', low_stock_threshold: '10', description: '', category_id: '', image_url: '' })
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
      <button className="btn btn-primary btn-full mb-4" onClick={() => { haptic.light(); setShowAddForm(!showAddForm); setEditingProduct(null); setFormData({ name: '', sale_price: '', cost_price: '', initial_stock: '', low_stock_threshold: '10', description: '', category_id: '', image_url: '' }) }}>
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
            <label className="input-label">Rasm (Majburiy)</label>
            <input type="file" accept="image/*" className="input" onChange={handleImageChange} required={!editingProduct} style={{ padding: '8px 12px' }} />
            {formData.image_url && (
              <div style={{ textAlign: 'center', marginTop: 12 }}>
                <img src={formData.image_url} alt="Preview" style={{ maxHeight: 120, borderRadius: 8, objectFit: 'contain', border: '1px solid var(--border)' }} />
              </div>
            )}
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
          <div className="flex items-center gap-3">
            {p.image_url ? (
              <img src={p.image_url} alt={p.name} style={{ width: 44, height: 44, borderRadius: 8, objectFit: 'cover', border: '1px solid var(--border)' }} />
            ) : (
              <div style={{ width: 44, height: 44, borderRadius: 8, background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16 }}>🍃</div>
            )}
            <div>
              <div style={{ fontWeight: 700 }}>{p.name}</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                Sotuv: {Number(p.sale_price_per_gram).toFixed(0)} $ · Zaxira: {Number(p.stock_grams).toFixed(0)} g
              </div>
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
                category_id: String(p.category_id || ''),
                image_url: p.image_url || ''
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
        <label className="input-label">Minimal to'lov ($)</label>
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


function NewsTab({ newsList, reload }) {
  const { showToast } = useApp()
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [image, setImage] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [processingId, setProcessingId] = useState(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onloadend = () => {
      setImage(reader.result)
    }
    reader.readAsDataURL(file)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!title.trim() || !content.trim()) {
      showToast('❌ Sarlavha va matn majburiy!')
      return
    }
    haptic.medium()
    setSubmitting(true)
    try {
      await adminCreateNews({ title: title.trim(), content: content.trim(), image_url: image || null })
      haptic.success()
      showToast('✅ Yangilik nashr qilindi!')
      setTitle('')
      setContent('')
      setImage('')
      reload()
    } catch (err) {
      haptic.error()
      showToast(`❌ ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Haqiqatan ham ushbu yangilikni o\'chirmoqchimisiz?')) return
    haptic.medium()
    setProcessingId(id)
    try {
      await adminDeleteNews(id)
      haptic.success()
      showToast('✅ O\'chirildi!')
      reload()
    } catch (err) {
      haptic.error()
      showToast(`❌ ${err.message}`)
    } finally {
      setProcessingId(null)
    }
  }

  return (
    <div className="stagger">
      {/* Create form */}
      <form onSubmit={handleSubmit} className="card mb-4">
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>📰 Yangi e'lon qo'shish</h3>
        
        <div className="input-group">
          <label className="input-label">Sarlavha</label>
          <input
            type="text"
            className="input"
            placeholder="Yangilik sarlavhasini yozing..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div className="input-group">
          <label className="input-label">Batafsil matn</label>
          <textarea
            className="input"
            rows={4}
            placeholder="Yangilik matnini yozing..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            style={{ resize: 'none' }}
          />
        </div>

        <div className="input-group">
          <label className="input-label">Rasm (ixtiyoriy)</label>
          <input
            type="file"
            accept="image/*"
            className="input"
            onChange={handleFileChange}
            style={{ padding: '8px 12px' }}
          />
        </div>

        {image && (
          <div className="mb-3" style={{ textAlign: 'center' }}>
            <img src={image} alt="Preview" style={{ maxHeight: 120, borderRadius: 8, objectFit: 'contain' }} />
          </div>
        )}

        <button type="submit" className="btn btn-gold btn-full btn-lg" disabled={submitting}>
          {submitting ? '⏳ ...' : '📢 Nashr qilish'}
        </button>
      </form>

      {/* List */}
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>E'lon qilingan yangiliklar</h3>
      {newsList.length === 0 ? (
        <div className="empty-state">Hali hech qanday yangilik yo'q</div>
      ) : (
        newsList.map(item => (
          <div key={item.id} className="card mb-3">
            {item.image_url && (
              <img src={item.image_url} alt="News" style={{ width: '100%', maxHeight: 160, objectFit: 'contain', borderRadius: 8, marginBottom: 12 }} />
            )}
            <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>{item.title}</div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap', lineHeight: 1.5, marginBottom: 12 }}>
              {item.content}
            </div>
            <div className="flex justify-between items-center">
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {new Date(item.created_at).toLocaleString()}
              </span>
              <button
                className="btn btn-danger btn-sm"
                onClick={() => handleDelete(item.id)}
                disabled={processingId === item.id}
              >
                🗑 O'chirish
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  )
}


function ChatTab({ rooms, reload }) {
  const [activeUserId, setActiveUserId] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [sendImage, setSendImage] = useState('')
  const [sending, setSending] = useState(false)
  const [activeUser, setActiveUser] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (!activeUserId) return
    loadRoomMessages()
    const interval = setInterval(loadRoomMessages, 4000)
    return () => clearInterval(interval)
  }, [activeUserId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadRoomMessages = async () => {
    try {
      const res = await adminGetRoomMessages(activeUserId)
      setMessages(res || [])
    } catch (e) {
      console.error(e)
    }
  }

  const handleSelectRoom = (room) => {
    haptic.light()
    setActiveUserId(room.user_id)
    setActiveUser(room)
    setMessages([])
  }

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    if (file.size > 8 * 1024 * 1024) {
      alert('Maksimal hajm: 8MB')
      return
    }
    const reader = new FileReader()
    reader.onloadend = () => {
      setSendImage(reader.result)
    }
    reader.readAsDataURL(file)
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!inputText.trim() && !sendImage) return

    haptic.medium()
    setSending(true)
    const textToSend = inputText.trim()
    const imgToSend = sendImage

    setInputText('')
    setSendImage('')

    try {
      await adminSendRoomMessage(activeUserId, { text: textToSend, image_url: imgToSend || null })
      await loadRoomMessages()
      reload() // refresh rooms list too
    } catch (err) {
      alert(`Xato: ${err.message}`)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="stagger" style={{ display: 'flex', gap: 16, height: '65vh' }}>
      {/* Sidebar: Chat rooms list */}
      <div className="card scroll-y" style={{ width: '35%', display: 'flex', flexDirection: 'column', padding: 8, gap: 8, background: 'var(--bg-glass)' }}>
        <div style={{ padding: '8px 12px', fontSize: 13, fontWeight: 700, color: 'var(--text-muted)' }}>Muloqotlar ({rooms.length})</div>
        {rooms.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 24, fontSize: 13, color: 'var(--text-muted)' }}>Faol chatlar mavjud emas</div>
        ) : (
          rooms.map(room => {
            const active = room.user_id === activeUserId
            const date = room.last_message_time ? new Date(room.last_message_time).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ''
            return (
              <div
                key={room.user_id}
                onClick={() => handleSelectRoom(room)}
                style={{
                  padding: '12px 10px',
                  borderRadius: 12,
                  cursor: 'pointer',
                  background: active ? 'rgba(124,92,252,0.15)' : 'rgba(255,255,255,0.02)',
                  border: `1px solid ${active ? 'var(--accent-primary)' : 'var(--border)'}`,
                  transition: 'all 0.2s ease',
                  position: 'relative'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '70%' }}>
                    {room.full_name || 'Noma\'lum'}
                  </div>
                  <div style={{ fontSize: 9, color: 'var(--text-muted)' }}>{date}</div>
                </div>
                {room.username && <div style={{ fontSize: 10, color: 'var(--accent-primary)', marginBottom: 4 }}>@{room.username}</div>}
                <div style={{ fontSize: 11, color: 'var(--text-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {room.sender_type === 'ADMIN' ? '💬 Siz: ' : ''}{room.last_message_text}
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Main chat window */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 12, background: 'var(--bg-glass)' }}>
        {activeUserId ? (
          <>
            {/* Active User Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 10, borderBottom: '1px solid var(--border)', marginBottom: 12 }}>
              <div>
                <div style={{ fontSize: 14, fontWeight: 800 }}>{activeUser?.full_name}</div>
                {activeUser?.username && <div style={{ fontSize: 11, color: 'var(--accent-primary)' }}>@{activeUser.username}</div>}
              </div>
              <button className="btn btn-sm btn-secondary" onClick={() => setActiveUserId(null)}>Yopish ✕</button>
            </div>

            {/* Messages container */}
            <div className="scroll-y" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10, paddingRight: 4, marginBottom: 12 }}>
              {messages.map(m => {
                const isAdminMsg = m.sender_type === 'ADMIN'
                const date = new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                return (
                  <div
                    key={m.id}
                    style={{
                      alignSelf: isAdminMsg ? 'flex-end' : 'flex-start',
                      maxWidth: '85%',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: isAdminMsg ? 'flex-end' : 'flex-start'
                    }}
                  >
                    <div
                      style={{
                        background: isAdminMsg ? 'var(--gradient-primary)' : 'rgba(255,255,255,0.06)',
                        color: isAdminMsg ? '#fff' : 'var(--text-primary)',
                        border: isAdminMsg ? 'none' : '1px solid var(--border)',
                        borderRadius: isAdminMsg ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                        padding: '8px 12px',
                        boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
                      }}
                    >
                      {m.image_url && (
                        <div style={{ marginBottom: 6 }}>
                          <a href={m.image_url} target="_blank" rel="noreferrer">
                            <img src={m.image_url} alt="Admin attachment" style={{ maxWidth: '100%', maxHeight: 150, borderRadius: 8, objectFit: 'contain' }} />
                          </a>
                        </div>
                      )}
                      {m.text && <div style={{ fontSize: 13, wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>{m.text}</div>}
                    </div>
                    <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 2 }}>{date}</div>
                  </div>
                )
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Input panel */}
            <form onSubmit={handleSend} style={{ padding: 6, background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)', borderRadius: 12 }}>
              {sendImage && (
                <div style={{ position: 'relative', display: 'inline-block', margin: '4px 0 8px 4px' }}>
                  <img src={sendImage} alt="Attachment Preview" style={{ height: 50, borderRadius: 6, objectFit: 'cover' }} />
                  <button
                    type="button"
                    onClick={() => setSendImage('')}
                    style={{
                      position: 'absolute', top: -5, right: -5,
                      background: '#ef4444', color: '#fff', border: 'none',
                      borderRadius: '50%', width: 16, height: 16, fontSize: 8,
                      cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}
                  >
                    ✕
                  </button>
                </div>
              )}
              <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                <label style={{ cursor: 'pointer', padding: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 8, background: 'rgba(255,255,255,0.04)' }}>
                  <span style={{ fontSize: 16 }}>📸</span>
                  <input type="file" accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} />
                </label>
                <input
                  type="text"
                  className="input"
                  placeholder="Xabar yozing / rasm yuklang..."
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  style={{ flex: 1, padding: '8px 12px', borderRadius: 8, height: 36, fontSize: 13 }}
                />
                <button type="submit" className="btn btn-primary" style={{ padding: '0 12px', height: 36, borderRadius: 8, fontSize: 13 }} disabled={sending || (!inputText.trim() && !sendImage)}>
                  Yuborish
                </button>
              </div>
            </form>
          </>
        ) : (
          <div style={{ margin: 'auto', textAlign: 'center', padding: 24, color: 'var(--text-muted)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>💬</div>
            <div style={{ fontSize: 13 }}>Muloqot qilish uchun chap tomondan mijozni tanlang</div>
          </div>
        )}
      </div>
    </div>
  )
}
