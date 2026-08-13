import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { getMe, getBalance, createTopup, submitReview, updateMe, getMyOrders } from '../api'
import Spinner from '../components/Spinner'
import { haptic } from '../tg'
import { t, getLanguage, setLanguage } from '../i18n'

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

export default function ProfilePage({ initialTab = 'info' }) {
  const { user, setUser, balance, showToast, loadBalance, tgUser, lang } = useApp()
  const [tab, setTab] = useState(initialTab)
  const [topupAmount, setTopupAmount] = useState('')
  const [receiptImage, setReceiptImage] = useState('')
  const [submittingTopup, setSubmittingTopup] = useState(false)
  const [reviewText, setReviewText] = useState('')
  const [reviewRating, setReviewRating] = useState(5)
  const [submittingReview, setSubmittingReview] = useState(false)

  const [orders, setOrders] = useState([])
  const [loadingOrders, setLoadingOrders] = useState(false)

  // Profile Edit states
  const [isEditing, setIsEditing] = useState(false)
  const [editName, setEditName] = useState('')
  const [editAge, setEditAge] = useState('')
  const [submittingProfile, setSubmittingProfile] = useState(false)

  useEffect(() => {
    setTab(initialTab)
  }, [initialTab])

  useEffect(() => {
    if (tab === 'orders') {
      loadOrders()
    }
  }, [tab])

  useEffect(() => {
    if (user) {
      setEditName(user.full_name || '')
      setEditAge(user.age !== null && user.age !== undefined ? String(user.age) : '')
    }
  }, [user])

  const loadOrders = async () => {
    setLoadingOrders(true)
    try {
      const res = await getMyOrders({ limit: 50 })
      setOrders(res.items || res || [])
    } catch {}
    setLoadingOrders(false)
  }

  if (!user) return <Spinner />

  const displayName = user.full_name || tgUser?.first_name || 'Foydalanuvchi'
  const initials = displayName.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    if (file.size > 8 * 1024 * 1024) {
      showToast(lang === 'ru' ? '❌ Максимальный размер файла: 8MB' : '❌ Maksimal fayl hajmi: 8MB')
      return
    }
    const reader = new FileReader()
    reader.onloadend = () => {
      setReceiptImage(reader.result)
      showToast(lang === 'ru' ? '✅ Чек успешно загружен!' : '✅ Chek muvaffaqiyatli yuklandi!')
    }
    reader.readAsDataURL(file)
  }

  const handleTopup = async () => {
    if (!topupAmount || Number(topupAmount) < 5) {
      showToast(lang === 'ru' ? '❌ Минимальная сумма: 5 $' : '❌ Minimal miqdor: 5 $')
      return
    }
    if (!receiptImage) {
      showToast(lang === 'ru' ? '❌ Загрузка чека обязательна!' : '❌ To\'lov chekini yuklash majburiy!')
      return
    }
    haptic.medium()
    setSubmittingTopup(true)
    try {
      await createTopup({
        amount: Number(topupAmount),
        payment_method: 'Litecoin (LTC)',
        receipt_file_id: receiptImage
      })
      haptic.success()
      showToast(lang === 'ru' ? '✅ Запрос отправлен! Ожидайте подтверждения админа.' : '✅ To\'ldirish so\'rovi yuborildi! Admin tasdiqlaydi.')
      setTopupAmount('')
      setReceiptImage('')
      await loadBalance()
    } catch (e) {
      haptic.error()
      showToast(`❌ ${e.message}`)
    } finally {
      setSubmittingTopup(false)
    }
  }

  const handleReview = async () => {
    if (!reviewText.trim()) {
      showToast(lang === 'ru' ? '❌ Введите текст отзыва' : '❌ Sharh matnini kiriting')
      return
    }
    haptic.medium()
    setSubmittingReview(true)
    try {
      await submitReview({ rating: reviewRating, text: reviewText })
      haptic.success()
      showToast(lang === 'ru' ? '✅ Отзыв отправлен на модерацию!' : '✅ Sharh yuborildi! Tez orada ko\'rib chiqiladi.')
      setReviewText('')
      setReviewRating(5)
    } catch (e) {
      haptic.error()
      showToast(`❌ ${e.message}`)
    } finally {
      setSubmittingReview(false)
    }
  }

  const handleSaveProfile = async (e) => {
    e.preventDefault()
    if (!editName.trim()) {
      showToast(lang === 'ru' ? '❌ Имя не может быть пустым' : '❌ Ism bo\'sh bo\'lishi mumkin emas')
      return
    }

    if (editAge.trim()) {
      const ageNum = parseInt(editAge)
      if (isNaN(ageNum) || ageNum < 13 || ageNum > 120) {
        showToast(lang === 'ru' ? '❌ Возраст должен быть от 13 до 120' : '❌ Yosh 13 va 120 oralig\'ida bo\'lishi kerak')
        return
      }
    }

    haptic.medium()
    setSubmittingProfile(true)
    try {
      await updateMe({
        full_name: editName.trim(),
        age: editAge.trim() ? parseInt(editAge) : null
      })
      setUser({
        ...user,
        full_name: editName.trim(),
        age: editAge.trim() ? parseInt(editAge) : null
      })
      haptic.success()
      showToast(lang === 'ru' ? '✅ Профиль обновлен!' : '✅ Profil yangilandi!')
      setIsEditing(false)
    } catch (err) {
      haptic.error()
      showToast(`❌ ${err.message}`)
    } finally {
      setSubmittingProfile(false)
    }
  }

  const handleLanguageChange = async (newLang) => {
    haptic.light()
    setLanguage(newLang)
    try {
      await updateMe({ language_code: newLang })
      setUser({ ...user, language_code: newLang })
      showToast(newLang === 'ru' ? '🇷🇺 Язык изменен на Русский' : '🇺🇿 Til O\'zbekchaga o\'zgartirildi')
    } catch {}
  }

  const handleCopyAddress = () => {
    haptic.light()
    navigator.clipboard.writeText('LLzgbAscn4Dgfcxf8F7xUynN5wMSuTanSw')
    showToast(lang === 'ru' ? '📋 Адрес скопирован!' : '📋 Manzil nusxalandi!')
  }

  return (
    <div className="page-content fade-in" style={{ paddingBottom: 'var(--nav-height)' }}>
      {/* Profile card */}
      <div className="hero-card mb-4">
        <div className="flex items-center gap-4 mb-4">
          <div className="profile-avatar">{initials}</div>
          <div>
            <div className="profile-name">{displayName}</div>
            {user.username && <div className="profile-username">@{user.username}</div>}
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginTop: 4 }}>
              📌 {lang === 'ru' ? 'Пользователь системы' : 'Foydalanuvchi'}
            </div>
          </div>
        </div>
        <div className="profile-balance" style={{ background: 'rgba(0,0,0,0.25)', border: '1px solid rgba(255,255,255,0.1)' }}>
          <div className="balance-amount">{Number(balance).toLocaleString()}</div>
          <div className="balance-label">$ — {t('balance')}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4 scroll-x" style={{ paddingBottom: 4 }}>
        {[
          { key: 'info', label: `👤 ${t('profile')}` },
          { key: 'topup', label: `💳 ${lang === 'ru' ? 'Пополнить' : 'To\'ldirish'}` },
          { key: 'orders', label: `📦 ${t('my_orders')}` },
          { key: 'review', label: `⭐ ${t('reviews')}` },
        ].map(tItem => (
          <button
            key={tItem.key}
            className="btn btn-sm"
            style={{ flexShrink: 0, ...(tab === tItem.key ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
            onClick={() => { haptic.light(); setTab(tItem.key) }}
          >
            {tItem.label}
          </button>
        ))}
      </div>

      {tab === 'info' && (
        <div className="stagger">
          {isEditing ? (
            <form onSubmit={handleSaveProfile} className="card stagger" style={{ padding: 16 }}>
              <div className="input-group">
                <label className="input-label">{t('full_name')}</label>
                <input
                  type="text"
                  className="input"
                  value={editName}
                  onChange={e => setEditName(e.target.value)}
                  required
                />
              </div>

              <div className="input-group">
                <label className="input-label">{t('age')}</label>
                <input
                  type="number"
                  className="input"
                  placeholder={lang === 'ru' ? 'Неизвестно' : "Noma'lum"}
                  value={editAge}
                  onChange={e => setEditAge(e.target.value)}
                />
              </div>

              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={submittingProfile}>
                  {submittingProfile ? '...' : (lang === 'ru' ? 'Сохранить' : 'Saqlash')}
                </button>
                <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setIsEditing(false)}>
                  {lang === 'ru' ? 'Отмена' : 'Bekor qilish'}
                </button>
              </div>
            </form>
          ) : (
            <>
              <InfoRow label={t('full_name')} value={user.full_name} />
              <InfoRow label={t('telegram_id')} value={user.telegram_id} />
              {user.phone && <InfoRow label={t('phone')} value={user.phone} />}
              <InfoRow
                label={t('age')}
                value={user.age ? `${user.age} ${lang === 'ru' ? 'лет' : 'yosh'}` : (lang === 'ru' ? 'Неизвестно' : "Noma'lum")}
              />
              <InfoRow label={t('status')} value={
                user.status === 'APPROVED' ? (lang === 'ru' ? '✅ Подтвержден' : '✅ Tasdiqlangan') :
                user.status === 'PENDING' ? (lang === 'ru' ? '⏳ Ожидает' : '⏳ Kutilmoqda') :
                (lang === 'ru' ? '🚫 Заблокирован' : '🚫 Bloklangan')
              } />
              
              <button
                className="btn btn-secondary btn-full mt-4 mb-4"
                onClick={() => { haptic.light(); setIsEditing(true) }}
              >
                ✍️ {lang === 'ru' ? 'Редактировать профиль' : 'Profilni tahrirlash'}
              </button>
            </>
          )}
          
          {/* Language Switcher Row */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
            <span style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 600 }}>{t('language')}</span>
            <div className="flex gap-2">
              <button
                className="btn btn-sm"
                style={lang === 'uz' ? { background: 'var(--gradient-primary)', color: '#fff' } : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }}
                onClick={() => handleLanguageChange('uz')}
              >
                🇺🇿 UZ
              </button>
              <button
                className="btn btn-sm"
                style={lang === 'ru' ? { background: 'var(--gradient-primary)', color: '#fff' } : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }}
                onClick={() => handleLanguageChange('ru')}
              >
                🇷🇺 RU
              </button>
            </div>
          </div>
        </div>
      )}

      {tab === 'topup' && (
        <div className="stagger">
          {/* LTC Wallet Box */}
          <div className="card mb-4" style={{ background: 'rgba(255, 179, 0, 0.08)', borderColor: 'rgba(255, 179, 0, 0.2)' }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6 }}>
              🪙 {lang === 'ru' ? 'Адрес оплаты Litecoin (LTC):' : 'Litecoin (LTC) to\'lov manzili:'}
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', background: 'rgba(0,0,0,0.3)', padding: 8, borderRadius: 8 }}>
              <code style={{ fontSize: 12, wordBreak: 'break-all', flex: 1, color: '#ffb300' }}>
                LLzgbAscn4Dgfcxf8F7xUynN5wMSuTanSw
              </code>
              <button className="btn btn-sm" style={{ padding: '4px 8px', fontSize: 12 }} onClick={handleCopyAddress}>
                📋 Copy
              </button>
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
              {lang === 'ru'
                ? '⚠️ Внимание: после оплаты обязательно загрузите скриншот чека ниже!'
                : '⚠️ Diqqat: to\'lov qilgach, chek (skrinshot) rasmini pastda yuklash MAJBURIY!'
              }
            </div>
          </div>

          <div className="input-group">
            <label className="input-label">{t('amount')}</label>
            <input
              type="number"
              className="input"
              placeholder={lang === 'ru' ? 'Минимум 5 $' : 'Minimum 5 $'}
              value={topupAmount}
              onChange={e => setTopupAmount(e.target.value)}
            />
          </div>

          {/* Quick amounts */}
          <div className="scroll-x mb-4">
            {[5, 10, 20, 50, 100].map(amt => (
              <button
                key={amt}
                className="btn btn-sm"
                style={{ flexShrink: 0, ...(topupAmount === String(amt) ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
                onClick={() => { haptic.light(); setTopupAmount(String(amt)) }}
              >
                {amt.toLocaleString()} $
              </button>
            ))}
          </div>

          {/* File uploader */}
          <div className="input-group">
            <label className="input-label">
              {lang === 'ru' ? '📸 Загрузить чек (Обязательно)' : '📸 To\'lov chekini yuklash (Majburiy)'}
            </label>
            <input
              type="file"
              accept="image/*"
              className="input"
              onChange={handleFileChange}
              style={{ padding: '8px 12px' }}
            />
          </div>

          {/* Image preview */}
          {receiptImage && (
            <div className="card mb-4" style={{ textAlign: 'center' }}>
              <img src={receiptImage} alt="Receipt preview" style={{ maxWidth: '100%', maxHeight: 150, borderRadius: 8, objectFit: 'contain' }} />
            </div>
          )}

          <button
            className="btn btn-gold btn-full btn-lg"
            onClick={handleTopup}
            disabled={submittingTopup || !receiptImage}
          >
            {submittingTopup ? '⏳ ...' : t('topup_balance')}
          </button>
        </div>
      )}

      {tab === 'orders' && (
        <div className="stagger">
          {loadingOrders ? (
            <Spinner />
          ) : orders.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📦</div>
              <div className="empty-state-title">{lang === 'ru' ? 'Заказы не найдены' : 'Buyurtmalar topilmadi'}</div>
            </div>
          ) : (
            orders.map(order => {
              const sMap = STATUS_MAP[order.status] || { label: order.status, cls: 'status-pending', icon: '⏳' }
              const date = new Date(order.created_at).toLocaleDateString(lang === 'ru' ? 'ru-RU' : 'uz-Latn', {
                day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
              })
              return (
                <Link key={order.id} to={`/orders/${order.id}`} className="order-card" style={{ textDecoration: 'none', display: 'block', marginBottom: 12 }}>
                  <div className="order-header">
                    <div>
                      <div className="order-number">№{order.order_number}</div>
                      <div className="order-date">{date}</div>
                    </div>
                    <span className={`status-badge ${sMap.cls}`}>{sMap.icon} {sMap.label}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                      {order.items?.length || '—'} {lang === 'ru' ? 'товар(ов)' : 'mahsulot'}
                    </div>
                    <div className="order-total">{Number(order.total_amount).toLocaleString()} $</div>
                  </div>
                </Link>
              )
            })
          )}
        </div>
      )}

      {tab === 'review' && (
        <div className="stagger">
          <div className="card mb-4" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>{t('rating')}</div>
            <div className="stars" style={{ justifyContent: 'center', marginBottom: 8 }}>
              {[1,2,3,4,5].map(i => (
                <span
                  key={i}
                  className={`star ${i <= reviewRating ? 'filled' : ''}`}
                  onClick={() => { haptic.light(); setReviewRating(i) }}
                >
                  {i <= reviewRating ? '⭐' : '☆'}
                </span>
              ))}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {reviewRating === 5 ? (lang === 'ru' ? 'Отлично!' : 'A\'lo!') :
               reviewRating === 4 ? (lang === 'ru' ? 'Хорошо' : 'Yaxshi') :
               reviewRating === 3 ? (lang === 'ru' ? 'Средне' : 'O\'rtacha') :
               reviewRating === 2 ? (lang === 'ru' ? 'Плохо' : 'Yomon') :
               (lang === 'ru' ? 'Очень плохо' : 'Juda yomon')}
            </div>
          </div>

          <div className="input-group">
            <label className="input-label">{t('reviews')}</label>
            <textarea
              className="input"
              rows={5}
              placeholder={t('review_placeholder')}
              value={reviewText}
              onChange={e => setReviewText(e.target.value)}
              style={{ resize: 'none' }}
            />
          </div>

          <button
            className="btn btn-primary btn-full btn-lg"
            onClick={handleReview}
            disabled={submittingReview}
          >
            {submittingReview ? '⏳ ...' : t('submit_review')}
          </button>
        </div>
      )}
    </div>
  )
}

function InfoRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
      <span style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 600 }}>{label}</span>
      <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', textAlign: 'right', maxWidth: '60%' }}>{value}</span>
    </div>
  )
}
