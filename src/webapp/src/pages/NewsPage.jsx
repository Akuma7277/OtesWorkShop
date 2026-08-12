import { useEffect, useState } from 'react'
import { getNews } from '../api'
import Spinner from '../components/Spinner'
import { t } from '../i18n'
import { haptic } from '../tg'
import { useApp } from '../context/AppContext'

export default function NewsPage() {
  const { lang } = useApp()
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)
  const [zoomedImage, setZoomedImage] = useState(null)

  useEffect(() => {
    getNews()
      .then(data => setNews(data || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />

  return (
    <div className="page-content fade-in" style={{ paddingBottom: 'var(--nav-height)' }}>
      <div className="section-header mb-4">
        <h1 className="section-title">📰 {t('news')}</h1>
      </div>

      {news.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📰</div>
          <div className="empty-state-title">{t('no_news')}</div>
          <div className="empty-state-desc">{t('no_news_desc')}</div>
        </div>
      ) : (
        <div className="stagger">
          {news.map(item => (
            <div key={item.id} className="card mb-4" style={{ background: 'var(--bg-glass)' }}>
              {item.image_url && (
                <div
                  style={{ cursor: 'pointer', borderRadius: 8, overflow: 'hidden', border: '1px solid var(--border)', background: '#000', marginBottom: 12 }}
                  onClick={() => { haptic.light(); setZoomedImage(item.image_url) }}
                >
                  <img src={item.image_url} alt={item.title} style={{ width: '100%', maxHeight: 220, objectFit: 'contain' }} />
                </div>
              )}
              <h3 style={{ fontSize: 16, fontWeight: 800, marginBottom: 6 }}>{item.title}</h3>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6, whiteSpace: 'pre-wrap', margin: '0 0 12px 0' }}>
                {item.content}
              </p>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'right' }}>
                {new Date(item.created_at).toLocaleString(lang === 'ru' ? 'ru-RU' : 'uz-Latn')}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Lightbox / Zoomed image modal */}
      {zoomedImage && (
        <div
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.95)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 9999, padding: 16, backdropFilter: 'blur(10px)'
          }}
          onClick={() => setZoomedImage(null)}
        >
          <img src={zoomedImage} alt="Zoomed news" style={{ maxWidth: '100%', maxHeight: '90%', objectFit: 'contain', borderRadius: 8 }} />
          <div style={{ position: 'absolute', top: 20, right: 20, color: '#fff', fontSize: 24, fontWeight: 700, cursor: 'pointer' }}>✕</div>
        </div>
      )}
    </div>
  )
}
