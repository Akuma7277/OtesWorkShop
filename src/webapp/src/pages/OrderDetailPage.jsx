import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getOrderDetail, cancelOrder } from '../api'
import Spinner from '../components/Spinner'
import { haptic } from '../tg'
import { t, getLanguage } from '../i18n'
import { useApp } from '../context/AppContext'

const STATUS_MAP = {
  PENDING_ADMIN:    { label: t('status_pending'), cls: 'status-pending', icon: '⏳', step: 1 },
  APPROVED:         { label: t('status_approved'), cls: 'status-approved', icon: '✅', step: 2 },
  PACKING:          { label: t('status_packing'), cls: 'status-packing', icon: '📦', step: 3 },
  OUT_FOR_DELIVERY: { label: t('status_delivery'), cls: 'status-delivery', icon: '🚚', step: 4 },
  DELIVERED:        { label: t('status_delivered'), cls: 'status-delivered', icon: '🏁', step: 5 },
  REJECTED:         { label: t('status_rejected'), cls: 'status-rejected', icon: '❌', step: -1 },
  CANCELLED:        { label: t('status_cancelled'), cls: 'status-cancelled', icon: '🚫', step: -1 },
  REFUNDED:         { label: t('status_refunded'), cls: 'status-cancelled', icon: '💰', step: -1 },
}

export default function OrderDetailPage() {
  const { lang } = useApp()
  const { id } = useParams()
  const navigate = useNavigate()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [cancelling, setCancelling] = useState(false)

  const STEPS = [
    t('status_pending'),
    t('status_approved'),
    t('status_packing'),
    t('status_delivery'),
    t('status_delivered')
  ]

  useEffect(() => {
    getOrderDetail(id)
      .then(data => setOrder(data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  const handleCancel = async () => {
    if (!confirm(lang === 'ru' ? 'Вы уверены, что хотите отменить этот заказ?' : 'Haqiqatan ham ushbu buyurtmani bekor qilmoqchimisiz?')) return
    haptic.medium()
    setCancelling(true)
    try {
      await cancelOrder(id)
      haptic.success()
      const data = await getOrderDetail(id)
      setOrder(data)
    } catch {}
    setCancelling(false)
  }

  if (loading) return <Spinner />
  if (!order) return null

  const s = STATUS_MAP[order.status] || { label: order.status, cls: 'status-pending', icon: '📋', step: 0 }
  const currentStep = s.step
  const canCancel = order.status === 'PENDING_ADMIN'

  return (
    <div className="page-content fade-in" style={{ paddingBottom: 'var(--nav-height)' }}>
      {/* Back */}
      <button
        onClick={() => { haptic.light(); navigate(-1) }}
        style={{ background: 'none', border: 'none', color: 'var(--accent-primary)', cursor: 'pointer', fontSize: 14, fontWeight: 600, marginBottom: 16, padding: 0 }}
      >
        ← {t('back')}
      </button>

      {/* Header */}
      <div className="hero-card mb-4">
        <div className="flex justify-between items-center mb-3">
          <div>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)' }}>{t('order_number')}</div>
            <div style={{ fontSize: 22, fontWeight: 900 }}>№{order.order_number}</div>
          </div>
          <span className={`status-badge ${s.cls}`}>{s.icon} {s.label}</span>
        </div>
        <div className="flex justify-between items-center">
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>
            {new Date(order.created_at).toLocaleString(lang === 'ru' ? 'ru-RU' : 'uz-Latn')}
          </div>
          <div style={{ fontSize: 22, fontWeight: 900, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            {Number(order.total_amount).toLocaleString()} $
          </div>
        </div>
      </div>

      {/* Delivery progress */}
      {currentStep >= 1 && (
        <div className="card mb-4">
          <div style={{ fontWeight: 700, marginBottom: 16 }}>📍 {t('delivery_progress')}</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', position: 'relative' }}>
            <div style={{ position: 'absolute', top: 14, left: '10%', right: '10%', height: 2, background: 'var(--border)', zIndex: 0 }} />
            <div style={{ position: 'absolute', top: 14, left: '10%', width: `${Math.max(0, ((currentStep - 1) / 4) * 80)}%`, height: 2, background: 'var(--gradient-primary)', zIndex: 1, transition: 'width 0.6s ease' }} />
            {STEPS.map((label, i) => {
              const done = i < currentStep
              const active = i === currentStep - 1
              return (
                <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, zIndex: 2, flex: '0 0 20%' }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%',
                    background: done ? 'var(--accent-green)' : active ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                    border: `2px solid ${done ? 'var(--accent-green)' : active ? 'var(--accent-primary)' : 'var(--border)'}`,
                    boxShadow: active ? '0 0 16px rgba(124,92,252,0.5)' : done ? '0 0 12px rgba(52,211,153,0.3)' : 'none',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12,
                    transition: 'all 0.4s ease',
                  }}>
                    {done ? '✓' : ''}
                  </div>
                  <div style={{ fontSize: 9, color: active || done ? 'var(--text-primary)' : 'var(--text-muted)', textAlign: 'center', lineHeight: 1.2, fontWeight: active ? 700 : 400 }}>
                    {label}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Delivery address */}
      <div className="card mb-4">
        <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8 }}>📍 {t('delivery_address').toUpperCase()}</div>
        <div style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{order.delivery_address}</div>
      </div>

      {/* Order items */}
      <div className="card mb-4">
        <div style={{ fontWeight: 700, marginBottom: 12 }}>📋 {lang === 'ru' ? 'Содержимое заказа' : 'Buyurtma tarkibi'}</div>
        {(order.items || []).map(item => (
          <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 10, marginBottom: 10, borderBottom: '1px solid var(--border)' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700 }}>{item.product_name_snapshot}</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{item.grams} g × {Number(item.unit_price_per_gram).toFixed(1)} $</div>
            </div>
            <div style={{ fontWeight: 700, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              {Number(item.subtotal).toLocaleString()} $
            </div>
          </div>
        ))}
        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800 }}>
          <span>{lang === 'ru' ? 'Итого:' : 'Jami:'}</span>
          <span style={{ fontSize: 18, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            {Number(order.total_amount).toLocaleString()} $
          </span>
        </div>
      </div>

      {/* Rejection reason */}
      {order.rejection_reason && (
        <div className="card mb-4" style={{ borderColor: 'rgba(248,113,113,0.3)', background: 'rgba(248,113,113,0.05)' }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--accent-red)', marginBottom: 8 }}>❌ {lang === 'ru' ? 'ПРИЧИНА ОТКЛОНЕНИЯ' : 'RAD ETISH SABABI'}</div>
          <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>{order.rejection_reason}</div>
        </div>
      )}

      {/* Delivery events */}
      {order.delivery_events?.length > 0 && (
        <div className="card mb-4">
          <div style={{ fontWeight: 700, marginBottom: 12 }}>🕐 {t('delivery_history')}</div>
          <div className="timeline">
            {order.delivery_events.map((ev, i) => (
              <div key={ev.id} className="timeline-item">
                <div className={`timeline-dot ${i === 0 ? 'active' : 'completed'}`} />
                <div className="timeline-title">{ev.status}</div>
                {ev.note && <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{ev.note}</div>}
                <div className="timeline-time">{new Date(ev.created_at).toLocaleString(lang === 'ru' ? 'ru-RU' : 'uz-Latn')}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cancel button */}
      {canCancel && (
        <button
          className="btn btn-danger btn-full btn-lg"
          onClick={handleCancel}
          disabled={cancelling}
        >
          {cancelling ? `⏳ ${lang === 'ru' ? 'Отмена...' : 'Bekor qilinmoqda...'}` : `🚫 ${t('cancel_order')}`}
        </button>
      )}
    </div>
  )
}
