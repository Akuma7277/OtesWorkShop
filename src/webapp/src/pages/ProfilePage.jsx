import { useEffect, useState } from 'react'
import { useApp } from '../context/AppContext'
import { getMe, getBalance, createTopup, submitReview, updateMe } from '../api'
import Spinner from '../components/Spinner'
import { haptic } from '../tg'
import { t, getLanguage, setLanguage } from '../i18n'

export default function ProfilePage() {
  const { user, setUser, balance, showToast, loadBalance, tgUser, lang } = useApp()
  const [tab, setTab] = useState('info')
  const [topupAmount, setTopupAmount] = useState('')
  const [topupMethod, setTopupMethod] = useState('click')
  const [submittingTopup, setSubmittingTopup] = useState(false)
  const [reviewText, setReviewText] = useState('')
  const [reviewRating, setReviewRating] = useState(5)
  const [submittingReview, setSubmittingReview] = useState(false)

  if (!user) return <Spinner />

  const displayName = user.full_name || tgUser?.first_name || 'Foydalanuvchi'
  const initials = displayName.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)

  const handleTopup = async () => {
    if (!topupAmount || Number(topupAmount) < 10000) {
      showToast(lang === 'ru' ? '❌ Минимальная сумма: 10,000 сум' : '❌ Minimal miqdor: 10,000 so\'m')
      return
    }
    haptic.medium()
    setSubmittingTopup(true)
    try {
      await createTopup({ amount: Number(topupAmount), payment_method: topupMethod, receipt_file_id: 'webapp' })
      haptic.success()
      showToast(lang === 'ru' ? '✅ Запрос отправлен! Ожидайте подтверждения админа.' : '✅ To\'ldirish so\'rovi yuborildi! Admin tasdiqlaydi.')
      setTopupAmount('')
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

  const handleLanguageChange = async (newLang) => {
    haptic.light()
    setLanguage(newLang)
    try {
      // Sync with backend database
      await updateMe({ language_code: newLang })
      setUser({ ...user, language_code: newLang })
      showToast(newLang === 'ru' ? '🇷🇺 Язык изменен на Русский' : '🇺🇿 Til O\'zbekchaga o\'zgartirildi')
    } catch {}
  }

  return (
    <div className="page-content fade-in">
      {/* Profile card */}
      <div className="hero-card mb-4">
        <div className="flex items-center gap-4 mb-4">
          <div className="profile-avatar">{initials}</div>
          <div>
            <div className="profile-name">{displayName}</div>
            {user.username && <div className="profile-username">@{user.username}</div>}
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginTop: 4 }}>
              📍 {user.address || '—'}
            </div>
          </div>
        </div>
        <div className="profile-balance" style={{ background: 'rgba(0,0,0,0.25)', border: '1px solid rgba(255,255,255,0.1)' }}>
          <div className="balance-amount">{Number(balance).toLocaleString()}</div>
          <div className="balance-label">{t('balance')}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {[
          { key: 'info', label: `👤 ${t('profile')}` },
          { key: 'topup', label: `💳 ${t('balance')}` },
          { key: 'review', label: `⭐ ${t('reviews')}` },
        ].map(tItem => (
          <button
            key={tItem.key}
            className="btn btn-sm"
            style={{ flex: 1, ...(tab === tItem.key ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
            onClick={() => { haptic.light(); setTab(tItem.key) }}
          >
            {tItem.label}
          </button>
        ))}
      </div>

      {tab === 'info' && (
        <div className="stagger">
          <InfoRow label={t('full_name')} value={user.full_name} />
          <InfoRow label={t('telegram_id')} value={user.telegram_id} />
          {user.phone && <InfoRow label={t('phone')} value={user.phone} />}
          <InfoRow label={t('age')} value={user.age} />
          <InfoRow label={t('status')} value={
            user.status === 'APPROVED' ? (lang === 'ru' ? '✅ Подтвержден' : '✅ Tasdiqlangan') :
            user.status === 'PENDING' ? (lang === 'ru' ? '⏳ Ожидает' : '⏳ Kutilmoqda') :
            (lang === 'ru' ? '🚫 Заблокирован' : '🚫 Bloklangan')
          } />
          
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
          <div className="input-group">
            <label className="input-label">{t('amount')} (so'm)</label>
            <input
              type="number"
              className="input"
              placeholder={lang === 'ru' ? 'Минимум 10,000 сум' : 'Minimum 10,000 so\'m'}
              value={topupAmount}
              onChange={e => setTopupAmount(e.target.value)}
            />
          </div>

          {/* Quick amounts */}
          <div className="scroll-x mb-4">
            {[50000, 100000, 200000, 500000].map(amt => (
              <button
                key={amt}
                className="btn btn-sm"
                style={{ flexShrink: 0, ...(topupAmount === String(amt) ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
                onClick={() => { haptic.light(); setTopupAmount(String(amt)) }}
              >
                {amt.toLocaleString()} so'm
              </button>
            ))}
          </div>

          <div className="input-group">
            <label className="input-label">{t('payment_method')}</label>
            <div className="flex gap-2">
              {['click', 'payme', 'transfer'].map(m => (
                <button
                  key={m}
                  className="btn btn-sm"
                  style={{ flex: 1, ...(topupMethod === m ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
                  onClick={() => { haptic.light(); setTopupMethod(m) }}
                >
                  {m === 'click' ? '💙 Click' : m === 'payme' ? '💚 Payme' : '🏦 O\'tkazma'}
                </button>
              ))}
            </div>
          </div>

          <div className="card mb-4" style={{ background: 'rgba(91,141,238,0.08)', borderColor: 'rgba(91,141,238,0.2)' }}>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {lang === 'ru'
                ? 'ℹ️ Отправьте чек об оплате в бот или свяжитесь с админом. После запроса админ подтвердит транзакцию.'
                : 'ℹ️ To\'lov chekini botga yuboring yoki admin bilan bog\'laning. So\'rov yuborilgandan so'ng admin tasdiqlashi kutiladi.'
              }
            </div>
          </div>

          <button
            className="btn btn-gold btn-full btn-lg"
            onClick={handleTopup}
            disabled={submittingTopup}
          >
            {submittingTopup ? '⏳ ...' : t('topup_balance')}
          </button>
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
