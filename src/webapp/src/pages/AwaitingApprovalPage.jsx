import { useState } from 'react'
import { useApp } from '../context/AppContext'
import { haptic } from '../tg'
import { t } from '../i18n'

export default function AwaitingApprovalPage() {
  const { loadUser, lang } = useApp()
  const [checking, setChecking] = useState(false)

  const handleRefresh = async () => {
    haptic.medium()
    setChecking(true)
    await loadUser()
    setChecking(false)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '90dvh', padding: 20 }}>
      <div className="card fade-in" style={{ width: '100%', maxWidth: 400, background: 'var(--bg-glass)', border: '1px solid var(--border)', backdropFilter: 'blur(20px)', borderRadius: 16, padding: 32, textAlign: 'center' }}>
        <div style={{ fontSize: 64, marginBottom: 16 }}>⏳</div>
        <h2 style={{ fontSize: 20, fontWeight: 800, color: 'var(--color-gold)', margin: '0 0 12px 0' }}>
          {t('awaiting_approval_title')}
        </h2>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 24 }}>
          {t('awaiting_approval_desc')}
        </p>

        <button
          className="btn btn-primary btn-full btn-lg"
          onClick={handleRefresh}
          disabled={checking}
        >
          {checking ? '⏳ ...' : (lang === 'ru' ? '🔄 Проверить статус' : '🔄 Holatni tekshirish')}
        </button>
      </div>
    </div>
  )
}
