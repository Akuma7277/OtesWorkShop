import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProduct } from '../api'
import { useApp } from '../context/AppContext'
import Spinner from '../components/Spinner'
import { haptic } from '../tg'

const GRAM_PRESETS = [10, 25, 50, 100, 250, 500]

export default function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { addToCart, showToast } = useApp()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [grams, setGrams] = useState(50)
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    getProduct(id)
      .then(setProduct)
      .catch(() => navigate(-1))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <Spinner />
  if (!product) return null

  const stock = Number(product.stock_grams)
  const maxGrams = Math.min(stock, 5000)
  const subtotal = grams * Number(product.sale_price_per_gram)
  const isOut = stock <= 0

  const handleAdd = () => {
    if (isOut) return
    haptic.medium()
    setAdding(true)
    addToCart(product, grams)
    setTimeout(() => setAdding(false), 800)
  }

  return (
    <div className="fade-in" style={{ paddingBottom: 'calc(var(--nav-height) + 80px)' }}>
      {/* Product image */}
      <div style={{ position: 'relative' }}>
        <div style={{
          width: '100%',
          aspectRatio: '16/9',
          background: 'linear-gradient(135deg, rgba(124,92,252,0.1), rgba(91,141,238,0.05))',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 80,
        }}>
          {product.image_url
            ? <img src={product.image_url} alt={product.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            : '🍃'
          }
        </div>
        <button
          onClick={() => { haptic.light(); navigate(-1) }}
          style={{
            position: 'absolute', top: 16, left: 16,
            background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(8px)',
            border: '1px solid rgba(255,255,255,0.15)',
            borderRadius: 'var(--radius-full)', padding: '8px 14px',
            color: '#fff', cursor: 'pointer', fontSize: 14, fontWeight: 600,
          }}
        >
          ← Orqaga
        </button>
      </div>

      <div style={{ padding: '20px 16px' }}>
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <h1 style={{ fontSize: 24, fontWeight: 900, letterSpacing: '-0.5px', flex: 1 }}>
            {product.name}
          </h1>
          <div style={{ fontSize: 22, fontWeight: 900, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginLeft: 12 }}>
            {Number(product.sale_price_per_gram).toFixed(0)} so'm/g
          </div>
        </div>

        {/* Stock */}
        <div className={`product-stock ${isOut ? 'out' : stock < 100 ? 'low' : 'ok'} mb-4`} style={{ fontSize: 13 }}>
          {isOut ? '❌ Omborda mavjud emas' : stock < 100 ? `⚠️ Faqat ${stock.toFixed(0)} g qoldi` : `✅ Mavjud: ${stock.toFixed(0)} g`}
        </div>

        {product.description && (
          <div className="card mb-4">
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>Tavsif</div>
            <div style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{product.description}</div>
          </div>
        )}

        {!isOut && (
          <>
            {/* Gram presets */}
            <div style={{ marginBottom: 16 }}>
              <div className="input-label">Gramm miqdorini tanlang</div>
              <div className="scroll-x" style={{ paddingBottom: 0 }}>
                {GRAM_PRESETS.filter(g => g <= maxGrams).map(g => (
                  <button
                    key={g}
                    className="btn btn-sm"
                    style={{ flexShrink: 0, ...(grams === g ? {} : { background: 'var(--bg-glass)', color: 'var(--text-secondary)' }) }}
                    onClick={() => { haptic.light(); setGrams(g) }}
                  >
                    {g} g
                  </button>
                ))}
              </div>
            </div>

            {/* Custom input */}
            <div className="input-group">
              <label className="input-label">Yoki o'zingiz kiriting (g)</label>
              <div className="flex items-center gap-2">
                <button
                  className="qty-btn"
                  onClick={() => { haptic.light(); setGrams(g => Math.max(1, g - 5)) }}
                >−</button>
                <input
                  type="number"
                  className="input"
                  style={{ flex: 1, textAlign: 'center' }}
                  value={grams}
                  min={1}
                  max={maxGrams}
                  onChange={e => setGrams(Math.min(maxGrams, Math.max(1, Number(e.target.value) || 1)))}
                />
                <button
                  className="qty-btn"
                  onClick={() => { haptic.light(); setGrams(g => Math.min(maxGrams, g + 5)) }}
                >+</button>
              </div>
            </div>

            {/* Subtotal */}
            <div className="card mb-6" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div className="text-xs text-muted">Jami narx</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{grams} g × {Number(product.sale_price_per_gram).toFixed(0)} so'm</div>
              </div>
              <div style={{ fontSize: 24, fontWeight: 900, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
                {subtotal.toFixed(0)} so'm
              </div>
            </div>
          </>
        )}
      </div>

      {/* Add to cart button — fixed bottom */}
      {!isOut && (
        <div style={{
          position: 'fixed', bottom: 'var(--nav-height)', left: '50%', transform: 'translateX(-50%)',
          width: '100%', maxWidth: 480, padding: '12px 16px',
          background: 'rgba(10,10,15,0.95)', backdropFilter: 'blur(12px)',
          borderTop: '1px solid var(--border)', zIndex: 150,
        }}>
          <button
            className={`btn btn-primary btn-full btn-lg ${adding ? 'pulse' : ''}`}
            onClick={handleAdd}
            disabled={adding}
          >
            {adding ? '✅ Qo\'shildi!' : `🛒 Savatga qo'shish — ${subtotal.toFixed(0)} so'm`}
          </button>
        </div>
      )}
    </div>
  )
}
