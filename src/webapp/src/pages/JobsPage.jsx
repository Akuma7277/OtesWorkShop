import { useEffect, useState } from 'react'
import { getJobs, applyJob, getMyJobApplications } from '../api'
import { haptic } from '../tg'
import Spinner from '../components/Spinner'
import { useApp } from '../context/AppContext'

export default function JobsPage() {
  const { lang, showToast } = useApp()
  const [positions, setPositions] = useState([])
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedPos, setSelectedPos] = useState(null)
  const [motivationText, setMotivationText] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const posData = await getJobs()
      const appData = await getMyJobApplications()
      setPositions(posData || [])
      setApplications(appData || [])
    } catch (e) {
      showToast(`❌ ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleApply = (pos) => {
    haptic.light()
    setSelectedPos(pos)
    setMotivationText('')
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!motivationText.trim()) {
      showToast(lang === 'ru' ? '❌ Напишите мотивационное письмо!' : '❌ Motivatsion xat yozing!')
      return
    }
    haptic.medium()
    setSubmitting(true)
    try {
      await applyJob({
        position_id: selectedPos.id,
        motivation_text: motivationText.trim()
      })
      haptic.success()
      showToast(lang === 'ru' ? '✅ Заявка успешно отправлена!' : '✅ Ariza muvaffaqiyatli yuborildi!')
      setShowModal(false)
      setSelectedPos(null)
      setMotivationText('')
      // Reload applications list
      const appData = await getMyJobApplications()
      setApplications(appData || [])
    } catch (e) {
      haptic.error()
      showToast(`❌ ${e.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="page-content fade-in">
      <div className="section-header mb-4">
        <h1 className="section-title">💼 {lang === 'ru' ? 'Вакансии' : 'Ish o\'rinlari'}</h1>
      </div>

      {positions.length === 0 ? (
        <div className="empty-state mb-5">
          <div className="empty-state-icon">💼</div>
          <div className="empty-state-title">
            {lang === 'ru' ? 'Нет открытых вакансий' : 'Bo\'sh ish o\'rinlari yo\'q'}
          </div>
          <div className="empty-state-desc">
            {lang === 'ru' ? 'Приходите позже, мы обязательно добавим что-то интересное.' : 'Keyinroq kelib ko\'ring, albatta yangi lavozimlar qo\'shamiz.'}
          </div>
        </div>
      ) : (
        <div className="stagger mb-5">
          {positions.map(pos => {
            const hasApplied = applications.some(app => app.position.id === pos.id && (app.status === 'PENDING' || app.status === 'APPROVED'))
            return (
              <div key={pos.id} className="card mb-3" style={{ padding: '16px 20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <h2 style={{ fontSize: 18, fontWeight: 800, margin: 0 }}>{pos.title}</h2>
                  <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent-primary)', background: 'rgba(124,92,252,0.1)', padding: '4px 8px', borderRadius: 8 }}>
                    💰 {pos.salary_info || '—'}
                  </span>
                </div>
                
                {pos.description && (
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
                    <strong>{lang === 'ru' ? 'Обязанности / Требования:' : 'Vazifalar / Talablar:'}</strong><br />
                    {pos.description}
                  </div>
                )}

                <button 
                  className={`btn btn-full btn-sm ${hasApplied ? 'btn-secondary' : 'btn-primary'}`}
                  disabled={hasApplied}
                  onClick={() => handleApply(pos)}
                >
                  {hasApplied 
                    ? (lang === 'ru' ? '⏳ Заявка отправлена' : '⏳ Ariza topshirilgan') 
                    : (lang === 'ru' ? 'Qo\'shish (Подать заявку)' : 'Qo\'shish (Ariza topshirish)')
                  }
                </button>
              </div>
            )
          })}
        </div>
      )}

      {/* Applications section */}
      {applications.length > 0 && (
        <div className="stagger">
          <div style={{ fontWeight: 800, fontSize: 16, marginBottom: 16 }}>
            📋 {lang === 'ru' ? 'Мои заявки' : 'Mening arizalarim'}
          </div>
          {applications.map(app => {
            let statusCls = 'status-pending'
            let statusIcon = '⏳'
            let statusText = lang === 'ru' ? 'Ожидает' : 'Kutilmoqda'
            
            if (app.status === 'APPROVED') {
              statusCls = 'status-approved'
              statusIcon = '✅'
              statusText = lang === 'ru' ? 'Одобрено' : 'Tasdiqlandi'
            } else if (app.status === 'REJECTED') {
              statusCls = 'status-rejected'
              statusIcon = '❌'
              statusText = lang === 'ru' ? 'Отклонено' : 'Rad etildi'
            }

            return (
              <div key={app.id} className="card mb-3" style={{ padding: '14px 18px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                  <div style={{ fontWeight: 700, fontSize: 14 }}>{app.position.title}</div>
                  <span className={`status-badge ${statusCls}`}>{statusIcon} {statusText}</span>
                </div>
                
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>
                  <strong>{lang === 'ru' ? 'Моя анкета:' : 'Mening motivatsiyam:'}</strong><br />
                  {app.motivation_text}
                </div>

                {app.admin_note && (
                  <div style={{ fontSize: 12, color: 'var(--accent-red)', background: 'rgba(239,68,68,0.05)', padding: '8px 10px', borderRadius: 8, marginTop: 8 }}>
                    <strong>{lang === 'ru' ? 'Комментарий администратора:' : 'Admin izohi:'}</strong> {app.admin_note}
                  </div>
                )}

                {app.status === 'APPROVED' && (
                  <div style={{ marginTop: 12 }}>
                    <a
                      href={app.operator_telegram_link ? (app.operator_telegram_link.startsWith('http') ? app.operator_telegram_link : `https://t.me/${app.operator_telegram_link.replace('@', '')}`) : '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-success btn-sm btn-full"
                      style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
                    >
                      💬 {lang === 'ru' ? 'Написать оператору в Telegram' : 'Telegram orqali operatorga yozish'}
                    </a>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Apply Modal */}
      {showModal && selectedPos && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'flex-end', zIndex: 9999 }}>
          <div style={{ background: 'var(--bg-secondary)', width: '100%', borderRadius: '20px 20px 0 0', padding: '24px 20px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ fontWeight: 800, fontSize: 18, marginBottom: 8, textAlign: 'center' }}>
              💼 {selectedPos.title}
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', textAlign: 'center', marginBottom: 20 }}>
              {lang === 'ru' ? 'Напишите мотивационное письмо о себе' : 'O\'zingiz haqingizda motivatsion xat yozing'}
            </div>

            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <label className="input-label">
                  {lang === 'ru' ? 'О себе (минимум 15-20 слов):' : 'O\'zi haqida (motivatsion gaplar):'}
                </label>
                <textarea
                  className="input"
                  rows={6}
                  value={motivationText}
                  onChange={e => setMotivationText(e.target.value)}
                  placeholder={lang === 'ru' 
                    ? 'Напишите о ваших навыках, опыте и почему вы хотите у нас работать...' 
                    : 'O\'z tajribangiz, qobiliyatlaringiz va nima uchun bizning jamoaga qo\'shilmoqchi ekanligingiz haqida yozing...'
                  }
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary btn-full" disabled={submitting}>
                {submitting ? '⏳ ...' : (lang === 'ru' ? 'Отправить' : 'Arizani topshirish')}
              </button>
              
              <button 
                type="button" 
                className="btn btn-secondary btn-full" 
                style={{ marginTop: 8 }}
                onClick={() => { haptic.light(); setShowModal(false); setSelectedPos(null); }}
              >
                {lang === 'ru' ? 'Отмена' : 'Bekor qilish'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
