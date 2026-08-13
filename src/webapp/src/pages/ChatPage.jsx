import { useEffect, useState, useRef } from 'react'
import { useApp } from '../context/AppContext'
import { getChatMessages, sendChatMessage } from '../api'
import Spinner from '../components/Spinner'
import { haptic } from '../tg'

export default function ChatPage() {
  const { lang, showToast } = useApp()
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [inputText, setInputText] = useState('')
  const [sendImage, setSendImage] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    loadMessages()
    // Poll for new messages every 5 seconds
    const interval = setInterval(loadMessages, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadMessages = async () => {
    try {
      const res = await getChatMessages()
      setMessages(res || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    if (file.size > 8 * 1024 * 1024) {
      showToast(lang === 'ru' ? '❌ Макс размер: 8MB' : '❌ Maksimal hajm: 8MB')
      return
    }
    const reader = new FileReader()
    reader.onloadend = () => {
      setSendImage(reader.result)
      showToast(lang === 'ru' ? '📸 Изображение прикреплено!' : '📸 Rasm biriktirildi!')
    }
    reader.readAsDataURL(file)
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!inputText.trim() && !sendImage) return

    haptic.light()
    setSending(true)
    const textToSend = inputText.trim()
    const imgToSend = sendImage

    // Optimistic update
    const tempId = Date.now()
    setMessages(prev => [
      ...prev,
      { id: tempId, sender_type: 'USER', text: textToSend, image_url: imgToSend, created_at: new Date().toISOString() }
    ])

    setInputText('')
    setSendImage('')

    try {
      await sendChatMessage({ text: textToSend, image_url: imgToSend || null })
      await loadMessages()
    } catch (err) {
      showToast(`❌ ${err.message}`)
    } finally {
      setSending(false)
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="page-content fade-in" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - var(--nav-height) - 70px)', padding: '16px 12px 0' }}>
      <div className="section-header mb-3" style={{ flexShrink: 0 }}>
        <h1 className="section-title">💬 {lang === 'ru' ? 'Чат с Админом' : 'Admin bilan bog\'lanish'}</h1>
      </div>

      {/* Messages Area */}
      <div className="card scroll-y" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '16px 12px', background: 'var(--bg-glass)', borderRadius: 16, marginBottom: 12 }}>
        {messages.length === 0 ? (
          <div style={{ margin: 'auto', textAlign: 'center', padding: '24px 12px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>💬</div>
            <p style={{ fontSize: 13, lineHeight: 1.5 }}>
              {lang === 'ru'
                ? 'Напишите ваше сообщение здесь. Админ ответит вам в ближайшее время.'
                : 'Savollaringiz bo\'lsa shu yerda yozishingiz mumkin. Admin tez orada javob beradi.'
              }
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {messages.map(m => {
              const isUser = m.sender_type === 'USER'
              const date = new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              return (
                <div
                  key={m.id}
                  style={{
                    alignSelf: isUser ? 'flex-end' : 'flex-start',
                    maxWidth: '85%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: isUser ? 'flex-end' : 'flex-start'
                  }}
                >
                  <div
                    style={{
                      background: isUser ? 'var(--gradient-primary)' : 'rgba(255,255,255,0.06)',
                      color: isUser ? '#fff' : 'var(--text-primary)',
                      border: isUser ? 'none' : '1px solid var(--border)',
                      borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                      padding: '10px 14px',
                      boxShadow: '0 4px 10px rgba(0,0,0,0.15)'
                    }}
                  >
                    {m.image_url && (
                      <div style={{ marginBottom: 6 }}>
                        <img src={m.image_url} alt="Uploaded" style={{ maxWidth: '100%', maxHeight: 200, borderRadius: 8, objectFit: 'contain' }} />
                      </div>
                    )}
                    {m.text && <div style={{ fontSize: 14, wordBreak: 'break-word', whiteSpace: 'pre-wrap', lineHeight: 1.4 }}>{m.text}</div>}
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, padding: '0 4px' }}>{date}</div>
                </div>
              )
            })}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input panel */}
      <form onSubmit={handleSend} className="card" style={{ flexShrink: 0, padding: 10, background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)', borderRadius: 16, marginBottom: 12 }}>
        {sendImage && (
          <div style={{ position: 'relative', display: 'inline-block', margin: '4px 0 10px 4px' }}>
            <img src={sendImage} alt="Preview" style={{ height: 60, borderRadius: 8, objectFit: 'cover' }} />
            <button
              type="button"
              onClick={() => setSendImage('')}
              style={{
                position: 'absolute', top: -6, right: -6,
                background: '#ef4444', color: '#fff', border: 'none',
                borderRadius: '50%', width: 18, height: 18, fontSize: 10,
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}
            >
              ✕
            </button>
          </div>
        )}

        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <label style={{ cursor: 'pointer', padding: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 8, background: 'rgba(255,255,255,0.05)' }}>
            <span style={{ fontSize: 18 }}>📸</span>
            <input type="file" accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} />
          </label>
          <input
            type="text"
            className="input"
            placeholder={lang === 'ru' ? 'Написать сообщение...' : 'Xabar yozing...'}
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            style={{ flex: 1, padding: '10px 14px', borderRadius: 12, height: 40 }}
          />
          <button type="submit" className="btn btn-primary" style={{ padding: '0 16px', height: 40, borderRadius: 12 }} disabled={sending || (!inputText.trim() && !sendImage)}>
            {lang === 'ru' ? 'Отправить' : 'Yuborish'}
          </button>
        </div>
      </form>
    </div>
  )
}
