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
  const { addToCart, showToast, getProductPriceForGrams, lang } = useApp()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [grams, setGrams] = useState(1)
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
  const subtotal = getProductPriceForGrams(product, grams)
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
          ← {t('back')}
        </button>
      </div>

      <div style={{ padding: '20px 16px' }}>
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <h1 style={{ fontSize: 24, fontWeight: 900, letterSpacing: '-0.5px', flex: 1 }}>
            {product.name}
          </h1>
          <div style={{ fontSize: 22, fontWeight: 900, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginLeft: 12 }}>
            {Number(product.sale_price_per_gram).toFixed(1)} $/g
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
            {/* Package selector */}
            <div style={{ marginBottom: 20 }}>
              <div className="input-label" style={{ marginBottom: 12 }}>
                {lang === 'ru' ? 'Выберите количество грамм' : 'Gramm miqdorini tanlang'}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }} className="stagger">
                {[
                  { grams: 1, label: lang === 'ru' ? '1 грамм' : '1 gram', factor: 1.0 },
                  { grams: 3, label: lang === 'ru' ? '3 грамма' : '3 gram', factor: 2.0 },
                  { grams: 5, label: lang === 'ru' ? '5 грамм' : '5 gram', factor: 3.0 },
                  { grams: 10, label: lang === 'ru' ? '10 грамм' : '10 gram', factor: 5.6 }
                ].map(pkg => {
                  const basePrice = Number(product.sale_price_per_gram)
                  const pkgPrice = basePrice * pkg.factor
                  const isDisabled = stock < pkg.grams
                  const isSelected = grams === pkg.grams

                  return (
                    <div
                      key={pkg.grams}
                      onClick={() => { if (!isDisabled) { haptic.light(); setGrams(pkg.grams) } }}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '14px 16px',
                        borderRadius: 12,
                        border: isSelected ? '2px solid var(--accent-primary)' : '1px solid var(--border)',
                        background: isSelected ? 'rgba(124, 92, 252, 0.12)' : 'var(--bg-glass)',
                        cursor: isDisabled ? 'not-allowed' : 'pointer',
                        opacity: isDisabled ? 0.5 : 1,
                        transition: 'all 0.2s ease',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{
                          width: 20, height: 20, borderRadius: '50%',
                          border: '2px solid ' + (isSelected ? 'var(--accent-primary)' : 'var(--text-muted)'),
                          display: 'flex', alignItems: 'center', justifyContent: 'center'
                        }}>
                          {isSelected && <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--accent-primary)' }} />}
                        </div>
                        <div style={{ fontWeight: 700, fontSize: 15, color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                          {pkg.label}
                        </div>
                      </div>
                      <div style={{ fontWeight: 800, fontSize: 16, color: isSelected ? 'var(--accent-primary)' : 'var(--text-primary)' }}>
                        {isDisabled ? (lang === 'ru' ? 'Нет в наличии' : 'Mavjud emas') : `${pkgPrice.toFixed(0)} $`}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Subtotal */}
            <div className="card mb-6" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div className="text-xs text-muted">{t('subtotal')}</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
                  {grams} g
                </div>
              </div>
              <div style={{ fontSize: 24, fontWeight: 900, background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
                {subtotal.toFixed(1)} $
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
            {adding ? '✅ Qo\'shildi!' : `🛒 ${t('add_to_cart')} — ${subtotal.toFixed(1)} $`}
          </button>
        </div>
      )}
    </div>
  )
}
