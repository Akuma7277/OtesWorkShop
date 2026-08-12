import { useState } from 'react'
import { useApp } from '../context/AppContext'
import { registerUser } from '../api'
import { haptic } from '../tg'
import { setLanguage, t } from '../i18n'

export default function RegisterPage() {
  const { loadUser, showToast, lang } = useApp()
  const [fullName, setFullName] = useState('')
  const [age, setAge] = useState('')
  const [selectedLang, setSelectedLang] = useState(lang || 'uz')
  const [submitting, setSubmitting] = useState(false)

  const handleLangSelect = (l) => {
    haptic.light()
    setSelectedLang(l)
    setLanguage(l)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!fullName.trim()) {
      showToast(selectedLang === 'ru' ? '❌ Введите имя или никнейм' : '❌ Ism yoki laqabingizni kiriting')
      return
    }
    const ageNum = parseInt(age)
    if (isNaN(ageNum) || ageNum < 13 || ageNum > 120) {
      showToast(selectedLang === 'ru' ? '❌ Введите корректный возраст (13-120)' : '❌ To\'g\'ri yosh kiriting (13-120)')
      return
    }

    haptic.medium()
    setSubmitting(true)
    try {
      await registerUser({
        full_name: fullName.trim(),
        age: ageNum,
        language_code: selectedLang
      })
      haptic.success()
      showToast(selectedLang === 'ru' ? '✅ Регистрация отправлена!' : '✅ Ro\'yxatdan o\'tish so\'rovi yuborildi!')
      await loadUser()
    } catch (err) {
      haptic.error()
      showToast(`❌ ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '90dvh', padding: 20 }}>
      <div className="card fade-in" style={{ width: '100%', maxWidth: 400, background: 'var(--bg-glass)', border: '1px solid var(--border)', backdropFilter: 'blur(20px)', borderRadius: 16, padding: 24 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>🚀</div>
          <h2 style={{ fontSize: 22, fontWeight: 800, margin: 0, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            {selectedLang === 'ru' ? 'Регистрация в NexШоп' : 'NexШopda ro\'yxatdan o\'tish'}
          </h2>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 6 }}>
            {selectedLang === 'ru' ? 'Создайте профиль, чтобы делать покупки' : 'Haridlarni amalga oshirish uchun profil yarating'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="stagger">
          {/* Language Selector */}
          <div className="input-group">
            <label className="input-label">{t('select_language')}</label>
            <div className="flex gap-2">
              <button
                type="button"
                className="btn"
                style={{ flex: 1, ...(selectedLang === 'uz' ? { background: 'var(--gradient-primary)', color: '#fff' } : { background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }) }}
                onClick={() => handleLangSelect('uz')}
              >
                🇺🇿 O'zbekcha
              </button>
              <button
                type="button"
                className="btn"
                style={{ flex: 1, ...(selectedLang === 'ru' ? { background: 'var(--gradient-primary)', color: '#fff' } : { background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }) }}
                onClick={() => handleLangSelect('ru')}
              >
                🇷🇺 Русский
              </button>
            </div>
          </div>

          {/* Nickname / Name */}
          <div className="input-group">
            <label className="input-label">{t('full_name')}</label>
            <input
              type="text"
              className="input"
              placeholder={selectedLang === 'ru' ? 'Например: NexVoid' : 'Masalan: NexVoid'}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>

          {/* Age */}
          <div className="input-group">
            <label className="input-label">{t('age')}</label>
            <input
              type="number"
              className="input"
              placeholder={selectedLang === 'ru' ? 'Введите ваш возраст' : 'Yoshingizni kiriting'}
              value={age}
              onChange={(e) => setAge(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-gold btn-full btn-lg mt-4"
            disabled={submitting}
          >
            {submitting ? '⏳ ...' : t('register_btn')}
          </button>
        </form>
      </div>
    </div>
  )
}
